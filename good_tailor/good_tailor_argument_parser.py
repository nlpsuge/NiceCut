import argparse
from enum import Enum
from os.path import expanduser
from pathlib import Path

default_workspace_path = str(Path(expanduser('~')))
default_milliseconds_before = 0
default_milliseconds_after = 1000


class NoSplitsChoices(Enum):
    SUBTITLE = 'subtitle'
    MEDIA = 'media'
    ALL = 'all'

    def __str__(self):
        return self.value

class GoodTailorArgumentParser:

    def parse_args(self):

        parser = argparse.ArgumentParser()
        # save to
        parser.add_argument('-st', '--save-to',
                            default=default_workspace_path, help="Setup the workspace path that saved the results.")
        parser.add_argument('-sf', '--subtitle-file', required=True)
        parser.add_argument('-mf', '--media-file', required=True)
        parser.add_argument('-gns', '--generate-new-subtitle', required=False,
                            help="Save the new generated subtitle to the folder where the original subtitle file is.",
                            action='store_true')
        parser.add_argument('-ns', '--no-splits',
                            help="Indicate that don't split the media/subtitle file, but will generate a new subtitle "
                                 "if '-gns/--generate-new-subtitle' is present.",
                            type=NoSplitsChoices, choices=list(NoSplitsChoices))
        parser.add_argument('-bc', '--milliseconds-before-cutting', default=default_milliseconds_before)
        parser.add_argument('-ac', '--milliseconds-after-cutting', default=default_milliseconds_after)
        # TODO
        parser.add_argument('-f', '--force-update', action='store_true')
        parser.add_argument('-d', '--debug', action='store_true')
        args = parser.parse_args()

        return args

