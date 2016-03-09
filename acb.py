#!/usr/bin/env python2

from __future__ import unicode_literals, print_function

import os, re, sys, animecomment
from animecomment import queue_separator
from animecomment.utility import *
from animecomment.subtitler import Subtitler
from random import choice, sample
from functools import partial
from imageio import imwrite
from moviepy.editor import VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip

from animecomment.corpus import Corpus
from animecomment.myytdl import YTDownloader as YT
from animecomment.mycrunchyroll import Crunchyroll as CR

cliLogger = Logger(u"cli", logging.DEBUG)

def get_a_line():
    return get_tweetable_line(Corpus().parse(), min_length=30, max_length=90)

def dl_and_comment(ep_count=3,frame_count=5,noprogress=True):
    cr = CR()
    urls = cr.get_random_free_episode_urls(ep_count)
    post_dl = partial(make_comment, frame_count=frame_count, out_path="output")
    yt = YT(post_dl, noprogress=noprogress)
    yt.download(urls)

def make_comment(vid_file, out_path="output", frame_count=5):
    cliLogger.info(u"Using {} as source...".format(os.path.basename(vid_file)))
    label = "".join(os.path.basename(vid_file).split(".")[:-1]).replace(" ","").lower()
    vid_clip = VideoFileClip(vid_file)
    ### TODO: Grab frames sequentially with randomish jump between each
    earliest = int(vid_clip.duration * 0.1)
    latest = int(vid_clip.duration * 0.9)
    valid_range = range(earliest, latest+1)

    subber = Subtitler()
    # TODO: Move all this queueing junk into a discrete component.
    with open("queue.txt", "a") as queue:
        for n in range(1, frame_count+1):
            # TODO: Make get_a_line() better.
            txt = get_a_line()
            cliLogger.warning("Trying to compose clip with... {}".format(txt))
            composed = subber.compose_subs(vid_clip, txt)
            frame = composed.get_frame(choice(valid_range))
            cliLogger.info(u"\tWriting {0} of {1:03d}...".format(n, frame_count) )
            image_path = u"{0}/{1}_{2:03d}.png".format(out_path, label, n)
            imwrite(image_path, frame)
            queue.write(u"{0}{1}{2}\n".format(image_path, queue_separator, txt).encode('utf8', 'replace') )

def main():
    import argparse

    parser = argparse.ArgumentParser(description=u"Download videos, randomly select frames, put text over them.")
    parser.add_argument('--episodes', '--eps', '-e', dest='ep_count', type=int, default=5)
    parser.add_argument('--frames', '-f', dest='frame_count', type=int, default=5)
    parser.add_argument('--verboser', '-v', dest='verbosity', action='count', default=0)
    parser.add_argument('--terser', '-q', dest='terseness', action='count', default=0)
    parser.add_argument('--progress', '-p', dest='progress', action='store_true', default=False)

    args = parser.parse_args()
    ep_count = args.ep_count
    frame_count = args.frame_count

    # make verbosity and terseness mutex
    # TODO: enforce this in argparser
    # TODO: actually use this calculated log_level elsewhere...
    verbosity = args.verbosity
    terseness = args.terseness
    if terseness and verbosity:
        verbosity = 0
    log_level = max(1, logging.WARNING - (verbosity*10) + (terseness*10))
    logger.warning(u"Setting console_lvl to {}".format(log_level))
    Logger(console_lvl=log_level)

    if args.progress or log_level < 30:
        noprogress = False
    else:
        noprogress = True

    cliLogger.debug(u"If you see this: we're verbosely logging!")
    dl_and_comment(ep_count=ep_count, frame_count=frame_count, noprogress=noprogress)
    ### cliLogger.info(u"Would run dl_and_comment with (ep_count={})".format(ep_count))
    ### cliLogger.info(u"and get_a_line() returns: {}".format( get_a_line() ) )

if __name__ == "__main__":
    main()
