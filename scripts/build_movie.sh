#!/bin/sh
# Build a gource movie about the development.
#
# For this to work, use macOS and install the following:
#
#   brew gource ffmpeg
#
# See also: <https://www.ekreative.com/blog/producing-your-own-git-repository-animated-visualization-video/>
set -ex
mkdir -p build
gource --auto-skip-seconds 1 --file-idle-time 0 --hide dirnames,filenames,mouse --seconds-per-day 1 --title Pygount -1920x1080 --output-ppm-stream - . | ffmpeg -y -r 30 -f image2pipe -vcodec ppm -i - -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 /tmp/pygount_movie.mp4
