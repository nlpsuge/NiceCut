import argparse


class GoodTailorArgumentParser:

    def parse_args(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('-w', '--workspace')
        parser.add_argument('-s', '--subtitle-file')
        parser.add_argument('-m', '--media-file')
        parser.add_argument('-b', '--milliseconds-before-cutting')
        parser.add_argument('-a', '--milliseconds-after-cutting')
        parser.add_argument('-f', '--force-update', action='store_true')
        parser.add_argument('-d', '--debug', action='store_true')
        args = parser.parse_args()

        return args

