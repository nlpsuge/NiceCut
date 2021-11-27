import os
from pathlib import Path

from alive_progress import alive_bar

from nice_cut.argument_parser import ArgumentParser, NoSplitsChoices
from nice_cut.supported_formats.srt import Srt

workspace_path_clips = str(Path('%s', 'NiceCut', 'clips'))
workspace_path_texts = str(Path('%s', 'NiceCut', 'texts'))


def main():
    parser = ArgumentParser()
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

    if args.generate_new_subtitle:
        srt.generate_new_subtitle(all_new_infos)

    if args.no_splits != NoSplitsChoices.ALL:
        if args.no_splits != NoSplitsChoices.SUBTITLE:
            with alive_bar(len(all_new_infos),
                           title='Processing subtitle files',
                           enrich_print=False,
                           bar='classic',
                           theme='classic') as bar:
                for info in all_new_infos:
                    srt.extract_subtitle_sentences(info)
                    bar()

        if args.no_splits != NoSplitsChoices.MEDIA:
            with alive_bar(len(all_new_infos),
                           title='Processing media files',
                           enrich_print=False,
                           bar='classic',
                           theme='classic') as bar:
                for info in all_new_infos:
                    milliseconds_before_cutting = args.milliseconds_before_cutting
                    milliseconds_after_cutting = args.milliseconds_after_cutting
                    srt.extract_media_clips(info, milliseconds_before_cutting, milliseconds_after_cutting)
                    bar()


def prepare_space(srt, args):
    srt.media_file_path = args.media_file
    srt.subtitle_file_path = args.subtitle_file

    save_to = args.save_to
    wpc = Path(workspace_path_clips % save_to)
    wpc.parent.mkdir(parents=True, exist_ok=True)
    wpt = Path(workspace_path_texts % save_to)
    wpt.parent.mkdir(parents=True, exist_ok=True)

    mfp = Path(srt.media_file_path)
    media_file_name_without_extension, file_extension = os.path.splitext(mfp.name)
    srt.media_file_name_without_extension = media_file_name_without_extension

    wpcm = Path(workspace_path_clips % save_to, media_file_name_without_extension)
    srt.this_media_file_clips_path = wpcm

    wptm = Path(workspace_path_texts % save_to, media_file_name_without_extension)
    srt.this_media_file_texts_path = wptm

    srt.target_media_filename = str(Path(srt.this_media_file_clips_path, srt.media_file_name_without_extension
                                         + '.%s.%s'))
    srt.target_text_filename = str(Path(srt.this_media_file_texts_path, srt.media_file_name_without_extension
                                        + '.%s.%s'))
