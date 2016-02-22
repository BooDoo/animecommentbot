#!/usr/bin/env python2

import os, re, sys, animecomment
from __future__ import unicode_literals, print_function
from animecomment.utility import *
from random import choice, sample
from functools import partial
from imageio import imwrite
from moviepy.editor import VideoFileClip
from animecomment.myytdl import YTDownloader as YT
from animecomment.mycrunchyroll import Crunchyroll as CR

global logger
logger = Logger(verbose=True)
debug, log, error = (logger.debug, logger.log, logger.error)

def dl_and_comment(count=3):
    cr = CR(verbose=True)
    urls = cr.get_random_free_episode_urls(count)
    post_dl = partial(take_screen, count=5, out_path="output")
    yt = YT(post_dl, verbose=False, noprogress=False)
    yt.download(urls)

def make_comment(vid_file, out_path="output", count=5):
    log(u"Using {} as source...".format(os.path.basename(vid_file)))
    label = os.path.basename(vid_file).split(".")[0].replace(" ","").lower()
    vid_clip = VideoFileClip(vid_file)
    ### TODO: Grab frames sequentially with randomish jump between each
    earliest = int(vid_clip.duration * 0.1)
    latest = int(vid_clip.duration * 0.9)
    valid_range = range(earliest, latest+1)

    ### with open("queue.txt", "a") as queue:
    for n in range(1, count+1):
        ### TODO: GET SUBTITLES and make a txt_clip
        ### txt_line = ...
        ### txt_clip = ...
        ### composed = CompositeVideoClip([vid_clip, txt_clip.set_pos("top")])
        composed = vid_clip
        frame = composed.get_frame(choice(valid_range))
        log(u"\tWriting {0} of {1:03d}...".format(n, count) )
        image_path = u"{0}/{1}_{2:03d}.png".format(out_path, label, n)
        imwrite(image_path, frame)
        ### queue.write(u"{0}{1}{2}\n".format(image_path, queue_separator, txt_line).encode('utf8', 'replace') )

def main()
    import argparse

    parser = argparse.ArgumentParser(description=u"Download videos, randomly select frames, put text over them.")
    parser.add_argument('--count', '-c', dest='count', type=int, default=5)
    parser.add_argument('--verbose', '-v', dest='verbose', action="store_true", default=False)

    args = parser.parse_args()
    verbose = args.verbose
    count = args.count

    dl_and_comment(count)

if __name__ == "__main__":
    pass
    # main()
