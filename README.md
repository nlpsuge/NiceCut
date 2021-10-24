# What does this project do?
A tool that manages to cut a media file into small sections according to a subtitle.

# Supported subtitle format
.srt

# Installation

## Via pip
`pip install NiceCut`

# Usage

## Common usage
```
cd video-location
ncut file-name.mp4 file-name.srt
```
Generated files should be appeared in `~/NiceCut/clips` and `~/NiceCut/texts`, which contains video clips and dialogs respectively.

## Help
```
$ ncut -h
usage: ncut [-h] [-st SAVE_TO] [-gns] [-ns {subtitle,media,all}] [-bc MILLISECONDS_BEFORE_CUTTING]
          [-ac MILLISECONDS_AFTER_CUTTING] [-f] [-d] [-v]
          media_file subtitle_file

positional arguments:
  media_file
  subtitle_file

optional arguments:
  -h, --help            show this help message and exit
  -st SAVE_TO, --save-to SAVE_TO
                        Setup the workspace path that saved the results.
  -gns, --generate-new-subtitle
                        Save the new generated subtitle to the folder where the original subtitle file is.
  -ns {subtitle,media,all}, --no-splits {subtitle,media,all}
                        Indicate that don't split the media/subtitle file, but will generate a new subtitle if
                        '-gns/--generate-new-subtitle' is present.
  -bc MILLISECONDS_BEFORE_CUTTING, --milliseconds-before-cutting MILLISECONDS_BEFORE_CUTTING
  -ac MILLISECONDS_AFTER_CUTTING, --milliseconds-after-cutting MILLISECONDS_AFTER_CUTTING
  -f, --force-update
  -d, --debug
  -v, --version         show program's version number and exit
  ```
  
