import argparse
from os.path import expanduser
from pathlib import Path

default_workspace_path = str(Path(expanduser('~')))
default_milliseconds_before = 0
default_milliseconds_after = 1000


class GoodTailorArgumentParser:

    def parse_args(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('-w', '--workspace',
                            default=default_workspace_path, help="Setup the workspace path that saved the results.")
        parser.add_argument('-s', '--subtitle-file', required=True)
        parser.add_argument('-m', '--media-file', required=True)
        parser.add_argument('-b', '--milliseconds-before-cutting', default=default_milliseconds_before)
        parser.add_argument('-a', '--milliseconds-after-cutting', default=default_milliseconds_after)
        parser.add_argument('-f', '--force-update', action='store_true')
        parser.add_argument('-d', '--debug', action='store_true')
        args = parser.parse_args()

        return args

