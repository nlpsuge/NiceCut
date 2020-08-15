from pydub import AudioSegment, silence


class Silence:

    def split(self, media_file_path, min_silence_len=1000, silence_thresh=-16):
        audio_segment = AudioSegment.from_file(media_file_path)
        clips = silence.split_on_silence(audio_segment, min_silence_len, silence_thresh)
        for clip in clips:
            pass

        pass
