import os
from os.path import expanduser
from pathlib import Path

from good_tailor.good_tailor_argument_parser import GoodTailorArgumentParser
from good_tailor.formats.srt import Srt

default_workspace_path = str(Path(expanduser('~')))
workspace_path_clips = str(Path('%s', 'GoodTailor', 'clips'))
workspace_path_texts = str(Path('%s', 'GoodTailor', 'texts'))

default_milliseconds_before = 0
default_milliseconds_after = 1000


def main():
    parser = GoodTailorArgumentParser()
    args = parser.parse_args()
    if args.debug:
        print(args)

    srt = Srt()
    srt.force_update = args.force_update
    srt.debug = args.debug

    prepare_space(srt, args)
    all_information = srt.process_timeline_clip()
    all_new_infos = srt.process_all_info(all_information)
    if args.debug:
        srt.print_infos(all_new_infos)

    milliseconds_before_cutting, milliseconds_after_cutting = get_delay_while_cutting(args)

    srt.extract_clips(all_new_infos, milliseconds_before_cutting, milliseconds_after_cutting)


def get_delay_while_cutting(args):
    if args.milliseconds_before_cutting is not None:
        milliseconds_before_cutting = args.milliseconds_before_cutting
    else:
        milliseconds_before_cutting = default_milliseconds_before
    
    if args.milliseconds_after_cutting is not None:
        milliseconds_after_cutting = args.milliseconds_after_cutting
    else:
        milliseconds_after_cutting = default_milliseconds_after
    
    return milliseconds_before_cutting, milliseconds_after_cutting


def get_workspace_path(args):
    if args.workspace is not None:
        return args.workspace
    else:
        return default_workspace_path


def prepare_space(self, args):
    self.media_file_path = args.media_file
    self.subtitle_file_path = args.subtitle_file

    workspace_path = get_workspace_path(args)
    wpc = Path(workspace_path_clips % workspace_path)
    wpc.parent.mkdir(parents=True, exist_ok=True)
    wpt = Path(workspace_path_texts % workspace_path)
    wpt.parent.mkdir(parents=True, exist_ok=True)

    mfp = Path(self.media_file_path)
    media_file_name_without_extension, file_extension = os.path.splitext(mfp.name)
    self.media_file_name_without_extension = media_file_name_without_extension

    wpcm = Path(workspace_path_clips % workspace_path, media_file_name_without_extension)
    self.this_media_file_clips_path = wpcm

    wptm = Path(workspace_path_texts % workspace_path, media_file_name_without_extension)
    self.this_media_file_texts_path = wptm

    self.target_media_filename = str(Path(self.this_media_file_clips_path, self.media_file_name_without_extension
                                          + '.%s.%s'))
    self.target_text_filename = str(Path(self.this_media_file_texts_path, self.media_file_name_without_extension
                                          + '.%s.%s'))
