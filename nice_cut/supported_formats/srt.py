# -*- coding: utf-8 -*-
import datetime
import os
import subprocess
from pathlib import Path
from typing import Any, Union

from nice_cut.info import Info


class Srt:

    target_text_filename: str
    target_media_filename: str
    media_file_name_without_extension: Union[bytes, str]
    this_media_file_texts_path: Union[Path, Any]
    this_media_file_clips_path: Union[Path, Any]

    subtitle_file_path: str
    media_file_path: str
    force_update: bool
    debug: bool
    workspace: str

    def __init__(self):
        pass
    
    def read_file(self):
        return open(self.subtitle_file_path, 'r')

    def process_timeline_clip(self):
        file = self.read_file()
        lines = file.readlines()

        if len(lines) == 0:
            raise Exception('Empty subtitle file found!')

        infos = []
        total_of_lines = len(lines)
        index = 0
        while index < total_of_lines:
            index = index + 1
            if index >= total_of_lines:
                break

            if ' --> ' in lines[index]:
                info = Info(lines[index - 1], lines[index])
                info.set_time(time_duration=lines[index])

                index_sentence = index
                step = 1
                stop = False
                while index_sentence < total_of_lines:
                    index_sentence = index_sentence + 1

                    if index_sentence >= total_of_lines:
                        break

                    if stop:
                        break

                    if ' --> ' not in lines[index_sentence]:
                        step = step + 1
                    else:
                        stop = True
                        step = step - 1

                if step < 0:
                    print('Something wrong...')
                    exit(-1)

                for i in range(1, step):
                    info.append_sentence(lines[index + i])

                infos.append(info)
                index = index + step

        if len(infos) == 0:
            raise Exception('[%s] is not srt format, please check it out.' % self.subtitle_file_path)
    
        return infos

    def sentence_not_completed(self, info, next_info):
        info_sentences = info.sentences
        if str.endswith(info_sentences, '...') and \
                (next_info is not None and str.startswith(next_info.sentences, '...')):
            return True

        if not (str.endswith(info_sentences, '."') or
                str.endswith(info_sentences, '.') or
                str.endswith(info_sentences, '!"') or
                str.endswith(info_sentences, '!') or
                str.endswith(info_sentences, '?"') or
                str.endswith(info_sentences, '?')):
            return True

        return False

    def process_all_info(self, all_info):
        index = 0
        total_of_all_info = len(all_info)
        new_infos = []
        new_number = 0
        while index < total_of_all_info:

            new_number = new_number + 1

            info = all_info[index]

            if self.skip_clip(info):
                index = index + 1
                continue

            if index + 1 != total_of_all_info:
                next_info = all_info[index + 1]
            else:
                next_info = None

            while self.sentence_not_completed(info, next_info):                
                if next_info is not None:
                    next_info.append_sentence_2_beginning(info.sentences)
                    next_info.start_time = info.start_time
                    next_info.srt_number = info.srt_number
                    info = next_info

                if index + 2 < total_of_all_info:
                    next_info = all_info[index + 2]
                else:
                    # No next info in the end
                    next_info = None

                index = index + 1
                if index >= total_of_all_info:
                    break

            info.number = new_number
            info.next_info = next_info
            new_infos.append(info)

            index = index + 1

        return new_infos

    def extract_clips(self, infos, milliseconds_before_cutting, milliseconds_after_cutting):
        # if self.debug is False:
        #     from tqdm import tqdm
        #     infos = tqdm(infos)

        for info in infos:
            self.extract_media_clips(info, milliseconds_before_cutting, milliseconds_after_cutting)
            self.extract_subtitle_sentences(info)

    def extract_subtitle_sentences(self, info):
        number = info.number
        srt_number = info.srt_number
        text_file = (self.target_text_filename % (number, srt_number)) + ".txt"

        text_file_path = Path(text_file)
        if not self.force_update and text_file_path.exists():
            return

        text_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(Path(text_file), 'w') as file:
            file.write(info.sentences)

    def extract_media_clips(self, info, milliseconds_before, milliseconds_after):
        number = info.number
        srt_number = info.srt_number
        mp4_file = (self.target_media_filename % (number, srt_number)) + ".mp4"

        mp4_file_path = Path(mp4_file)
        if not self.force_update and mp4_file_path.exists():
            return

        mp4_file_path.parent.mkdir(parents=True, exist_ok=True)

        start_time = info.start_time.replace(',', '.')
        end_time = info.end_time.replace(',', '.')

        original_start_datetime = datetime.datetime.strptime(start_time, '%H:%M:%S.%f')
        start_datetime = original_start_datetime - datetime.timedelta(milliseconds=milliseconds_before)
        zero_position = datetime.datetime.strptime('00:00:00.000', '%H:%M:%S.%f')
        if start_datetime < zero_position:
            start_datetime = zero_position

        end_datetime = datetime.datetime.strptime(end_time, '%H:%M:%S.%f') + datetime.timedelta(milliseconds=milliseconds_after)

        if info.next_info is not None:
            next_start_time = info.next_info.start_time.replace(',', '.')
            next_start_datetime = datetime.datetime.strptime(next_start_time, '%H:%M:%S.%f')

            if end_datetime > next_start_datetime:
                end_datetime = next_start_datetime

        start_time = start_datetime.strftime('%H:%M:%S.%f')
        end_time = end_datetime.strftime('%H:%M:%S.%f')

        cmd = "ffmpeg -i \"" + \
              self.media_file_path + \
              "\" -ss '" + \
              start_time + \
              "' -to '" + \
              end_time + \
              "' -loglevel error " + \
              " -acodec copy \"" + \
              mp4_file + "\"" + \
              (" -y " if self.force_update else "") + \
              " > /dev/null"

        if self.debug:
            print('Executing: ' + cmd)

        try:
            subprocess.check_output(cmd, shell=True)
        except:
            print('Oops, something is wrong! Removing the likely corrupted file: ' + mp4_file)
            if mp4_file_path.exists():
                os.remove(mp4_file_path)
            raise

    def print_infos(self, infos):
        for ni in infos:
            sentences = ni.sentences
            print(ni.number)
            print(ni.srt_number)
            print(ni.time_duration)
            print(ni.start_time)
            print(ni.end_time)
            print(sentences)
            print()

    def skip_clip(self, info):
        # Skip advertisement
        if "OpenSubtitles" in info.sentences:
            return True
        # Skip unimportant clips, such as [LAUGH], [SIGHS] etc
        if str.startswith(info.sentences, '[') and str.endswith(info.sentences, ']'):
            return True
        return False

    def generate_new_subtitle(self, infos):
        filename, file_extension = os.path.splitext(self.subtitle_file_path)
        with open(filename + '.generated_by_ncut' + file_extension, 'w') as file:
            for info in infos:
                file.write(str(info.number))
                file.write('\n')
                file.write(info.start_time + " --> " + info.end_time)
                file.write('\n')
                file.write(info.sentences)
                file.write('\n\n')







