# -*- coding: utf-8 -*-
from contextlib import contextmanager
import logging
import io
import os
import platform
import subprocess
from datetime import timedelta

import ffmpeg
import numpy as np
from .sklearn_shim import TransformerMixin
import tqdm

from .constants import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ref: https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
# Create a set of arguments which make a ``subprocess.Popen`` (and
# variants) call work with or without Pyinstaller, ``--noconsole`` or
# not, on Windows and Linux. Typical use::
#
#   subprocess.call(['program_to_run', 'arg_1'], **subprocess_args())
#
# When calling ``check_output``::
#
#   subprocess.check_output(['program_to_run', 'arg_1'],
#                           **subprocess_args(False))
def _subprocess_args(include_stdout=True):
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):
        # On Windows, subprocess calls will pop up a command window by default
        # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
        # distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None

    # ``subprocess.check_output`` doesn't allow specifying ``stdout``::
    #
    #   Traceback (most recent call last):
    #     File "test_subprocess.py", line 58, in <module>
    #       **subprocess_args(stdout=None))
    #     File "C:\Python27\lib\subprocess.py", line 567, in check_output
    #       raise ValueError('stdout argument not allowed, it will be overridden.')
    #   ValueError: stdout argument not allowed, it will be overridden.
    #
    # So, add it only if it's needed.
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}

    # On Windows, running this from the binary produced by Pyinstaller
    # with the ``--noconsole`` option requires redirecting everything
    # (stdin, stdout, stderr) to avoid an OSError exception
    # "[Error 6] the handle is invalid."
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env})
    return ret


def _ffmpeg_bin_path(bin_name):
    if platform.system() == 'Windows':
        bin_name = '{}.exe'.format(bin_name)
    try:
        resource_path = os.environ[SUBSYNC_RESOURCES_ENV_MAGIC]
        if len(resource_path) > 0:
            return os.path.join(resource_path, 'ffmpeg-bin', bin_name)
    except KeyError as e:
        logger.error("Couldn't find resource path; falling back to searching system path")
    return bin_name


def _make_auditok_detector(sample_rate, frame_rate):
    try:
        from auditok import \
            BufferAudioSource, ADSFactory, AudioEnergyValidator, StreamTokenizer
    except ImportError as e:
        logger.error("""Error: auditok not installed!
        Consider installing it with `pip install auditok`. Note that auditok
        is GPLv3 licensed, which means that successfully importing it at
        runtime creates a derivative work that is GPLv3 licensed. For personal
        use this is fine, but note that any commercial use that relies on
        auditok must be open source as per the GPLv3!*
        *Not legal advice. Consult with a lawyer.
        """)
        raise e
    bytes_per_frame = 2
    frames_per_window = frame_rate // sample_rate
    validator = AudioEnergyValidator(
        sample_width=bytes_per_frame, energy_threshold=50)
    tokenizer = StreamTokenizer(
        validator=validator, min_length=0.2*sample_rate,
        max_length=int(5*sample_rate),
        max_continuous_silence=0.25*sample_rate)

    def _detect(asegment):
        asource = BufferAudioSource(data_buffer=asegment,
                                    sampling_rate=frame_rate,
                                    sample_width=bytes_per_frame,
                                    channels=1)
        ads = ADSFactory.ads(audio_source=asource, block_dur=1./sample_rate)
        ads.open()
        tokens = tokenizer.tokenize(ads)
        length = (len(asegment)//bytes_per_frame
                  + frames_per_window - 1)//frames_per_window
        media_bstring = np.zeros(length+1, dtype=int)
        for token in tokens:
            media_bstring[token[1]] += 1
            media_bstring[token[2]+1] -= 1
        return (np.cumsum(media_bstring)[:-1] > 0).astype(float)
    return _detect


def _make_webrtcvad_detector(sample_rate, frame_rate):
    import webrtcvad
    vad = webrtcvad.Vad()
    vad.set_mode(3)  # set non-speech pruning aggressiveness from 0 to 3
    window_duration = 1. / sample_rate  # duration in seconds
    frames_per_window = int(window_duration * frame_rate + 0.5)
    bytes_per_frame = 2

    def _detect(asegment):
        media_bstring = []
        failures = 0
        for start in range(0, len(asegment) // bytes_per_frame,
                           frames_per_window):
            stop = min(start + frames_per_window,
                       len(asegment) // bytes_per_frame)
            try:
                is_speech = vad.is_speech(
                    asegment[start * bytes_per_frame: stop * bytes_per_frame],
                    sample_rate=frame_rate)
            except:
                is_speech = False
                failures += 1
            media_bstring.append(1 if is_speech else 0)
        return np.array(media_bstring)

    return _detect


class VideoSpeechTransformer(TransformerMixin):
    def __init__(self, vad, sample_rate, frame_rate, start_seconds=0, end_seconds=None):
        self.vad = vad
        self.sample_rate = sample_rate
        self.frame_rate = frame_rate
        self.start_seconds = start_seconds
        self.end_seconds = end_seconds
        self.video_speech_results_ = None

    def fit(self, fname, *_):

        try:
            total_duration = float(ffmpeg.probe(
                fname, cmd=_ffmpeg_bin_path('ffprobe')
            )['format']['duration']) - self.start_seconds
        except Exception as e:
            logger.warning(e)
            total_duration = None
        if 'webrtc' in self.vad:
            detector = _make_webrtcvad_detector(self.sample_rate, self.frame_rate)
        elif 'auditok' in self.vad:
            detector = _make_auditok_detector(self.sample_rate, self.frame_rate)
        else:
            raise ValueError('unknown vad: %s' % self.vad)
        media_bstring = []
        ffmpeg_args = [_ffmpeg_bin_path('ffmpeg')]
        if self.start_seconds > 0:
            ffmpeg_args.extend([
                '-ss', str(timedelta(seconds=self.start_seconds)),
            ])
        if self.end_seconds:
            ffmpeg_args.extend([
                '-to', str(timedelta(seconds=self.end_seconds)),
            ])
        ffmpeg_args.extend([
            '-loglevel', 'fatal',
            '-nostdin',
            '-i', fname,
            '-f', 's16le',
            '-ac', '1',
            '-acodec', 'pcm_s16le',
            '-ar', str(self.frame_rate),
            '-'
        ])
        process = subprocess.Popen(ffmpeg_args, **_subprocess_args(include_stdout=True))
        bytes_per_frame = 2
        frames_per_window = bytes_per_frame * self.frame_rate // self.sample_rate
        windows_per_buffer = 10000
        simple_progress = 0.

        @contextmanager
        def redirect_stderr(enter_result=None):
            yield enter_result
        tqdm_extra_args = {}
        pbar_output = io.StringIO()
        with redirect_stderr(pbar_output):
            with tqdm.tqdm(total=total_duration, **tqdm_extra_args) as pbar:
                while True:
                    in_bytes = process.stdout.read(frames_per_window * windows_per_buffer)
                    if not in_bytes:
                        break
                    newstuff = len(in_bytes) / float(bytes_per_frame) / self.frame_rate
                    simple_progress += newstuff
                    pbar.update(newstuff)
                    in_bytes = np.frombuffer(in_bytes, np.uint8)
                    media_bstring.append(detector(in_bytes))
        self.video_speech_results_ = np.concatenate(media_bstring)
        return self

    def transform(self, *_):
        return self.video_speech_results_


class DeserializeSpeechTransformer(TransformerMixin):
    def __init__(self):
        self.deserialized_speech_results_ = None

    def fit(self, fname, *_):
        speech = np.load(fname)
        if hasattr(speech, 'files'):
            if 'speech' in speech.files:
                speech = speech['speech']
            else:
                raise ValueError('could not find "speech" array in '
                                 'serialized file; only contains: %s' % speech.files)
        self.deserialized_speech_results_ = speech
        return self

    def transform(self, *_):
        return self.deserialized_speech_results_
