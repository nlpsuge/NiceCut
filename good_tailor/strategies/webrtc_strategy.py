import datetime
from typing import List

from good_tailor.info import Info

from good_tailor.third_party.ffsubsync.speech_transformers import VideoSpeechTransformer
from good_tailor.third_party.ffsubsync.constants import SAMPLE_RATE
from good_tailor.third_party.ffsubsync.constants import DEFAULT_FRAME_RATE
from good_tailor.third_party.ffsubsync.constants import DEFAULT_VAD


class Webrtc:

    def process(self, media_file, subtitle_lines: List[Info]):
        self.detect_speech(media_file, subtitle_lines)
        self.punctuate(subtitle_lines)
        pass

    def detect_speech(self, media_file, subtitle_lines: List[Info]):
        vad = DEFAULT_VAD
        frame_rate = DEFAULT_FRAME_RATE
        start_seconds = 0
        tf = VideoSpeechTransformer(vad=vad,
                                    sample_rate=SAMPLE_RATE,
                                    frame_rate=frame_rate,
                                    start_seconds=start_seconds)
        tf_self = tf.fit(media_file)
        video_speech_results_ = tf_self.video_speech_results_
        print(video_speech_results_)
        # duation = len(video_speech_results_1) * 10

        the_start_datetime = datetime.datetime.strptime(subtitle_lines[0].start_time.replace(',', '.'), '%H:%M:%S.%f')

        for i in range(len(subtitle_lines)):
            sl = subtitle_lines[i]
            if i >= 1:
                subtitle_lines[i - 1].next_info = sl
            seconds_until_start = (sl.start_datetime - the_start_datetime).total_seconds()
            seconds_until_end = (sl.end_datetime - the_start_datetime).total_seconds()
            sl.video_speech_results = video_speech_results_[round(seconds_until_start * 100):
                                                            round(seconds_until_end * 100)]
        # The last one has no next element
        subtitle_lines[-1].next_info = None

    def punctuate(self, subtitle_lines: List[Info]):
        for sl in subtitle_lines:
            current_video_speech_results = sl.video_speech_results
            print(sl.time_duration)
            print(sl.sentences)
            print("current_video_speech_results: ")
            print(list(current_video_speech_results))
            next_info = sl.next_info
            if next_info:
                next_video_speech_results = next_info.video_speech_results
                print(next_info.time_duration)
                print(next_info.sentences)
                print("next_video_speech_results: ")
                print(list(next_video_speech_results))

                current_index_of_none_voice = None
                next_index_of_none_voice = None

                current_result_samples = "".join([str(elem) for elem in current_video_speech_results[-50:]])
                next_result_samples = "".join([str(elem) for elem in next_video_speech_results[:50]])
                try:
                    current_index_of_none_voice = current_result_samples.index('0000000000')
                except ValueError:
                    pass
                if current_index_of_none_voice:
                    sl.original_end_datetime = sl.end_datetime
                    sl.original_end_time = sl.end_time
                    silence_num = 0
                    for i in range(len(current_result_samples)):
                        if i >= current_index_of_none_voice:
                            silence_num = silence_num + 1
                            if current_result_samples[i] == 1:
                                break

                    sl.end_datetime = sl.start_datetime + datetime.timedelta(
                        milliseconds=((len(current_video_speech_results) - 50 + current_index_of_none_voice) * 10) + silence_num * 10)
                    sl.end_time = sl.end_datetime.strftime('%H:%M:%S.%f').replace('.', ',')
                    sl.original_sentences = sl.sentences
                    sl.sentences = sl.sentences + '.'

                    # try:
                    #     next_index_of_none_voice = next_result_samples.index('0000000000')
                    # except ValueError:
                    #     continue
                    # if next_index_of_none_voice:
                    next_info.original_start_datetime = next_info.start_datetime
                    next_info.original_start_time = next_info.start_time
                    next_info.start_datetime = sl.end_datetime - datetime.timedelta(milliseconds=silence_num * 10)
                    next_info.start_time = next_info.start_datetime.strftime('%H:%M:%S.%f').replace('.', ',')

