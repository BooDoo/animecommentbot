#!/usr/bin/env python3
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
from animecomment.nyer_captions import get_nyer_caption
from animecomment.laphamquotes import get_a_quote, get_quotes

cliLogger = Logger(u"cli", logging.DEBUG)

def get_a_line(source, min_length=30, max_length=90):
    return clean_line(get_tweetable_line(source(),min_length=min_length, max_length=max_length))

def dl_and_comment(ep_count=3,frame_count=5,caption_gen=None,series=None,noprogress=True):
    cr = CR()
    # TODO: No, this is gross.
    debug(u"Before parsing series in dl_and_comment: {}".format(series))
    if series is not None:
        series = flatten([cr.search_series(q) for q in force_iterable(series)])
    debug(u"After parsing series in dl_and_comment: {}".format(series))
    urls = cr.get_random_free_episode_urls(ep_count,series)
    post_dl = partial(make_comment, frame_count=frame_count, caption_gen=caption_gen, out_path="output")
    yt = YT(post_dl, noprogress=noprogress)
    yt.download(urls)

def make_comment(vid_file, out_path="output", frame_count=5, caption_gen=None):
    cliLogger.info(u"Using {} as source...".format(os.path.basename(vid_file)))
    caption_gen = caption_gen or get_text_source()
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
            # TODO: Hoo boy this could be an infinite loop.
            txt = None
            while txt is None:
                try:
                    txt = get_a_line(caption_gen)
                except:
                    cliLogger.error("Failed to get text, trying again...")
                    continue
            cliLogger.warning("Trying to compose clip with... {}".format(txt))
            composed = subber.compose_subs(vid_clip, txt)
            frame = composed.get_frame(choice(valid_range))
            cliLogger.info(u"\tWriting {0} of {1:03d}...".format(n, frame_count) )
            image_path = u"{0}/{1}_{2:03d}.png".format(out_path, label, n)
            imwrite(image_path, frame)
            queue.write(u"{0}{1}{2}\n".format(image_path, queue_separator, txt))

def get_text_source(label=None):
    if label is None:
        corpus = Corpus('corpora')
        text_source = lambda: choice([get_nyer_caption, get_quotes, corpus.parse])()
    elif label == "nyer":
        text_source = get_nyer_caption
    elif label == "lapham":
        text_source = get_quotes
    else:
        corpus = Corpus(label)
        text_source = corpus.parse

    return text_source

def main():
    import argparse

    parser = argparse.ArgumentParser(description=u"Download videos, randomly select frames, put text over them.")
    parser.add_argument('--ep_count', '--eps', '-e', dest='ep_count', type=int, default=5)
    parser.add_argument('--frame_count', '-f', dest='frame_count', type=int, default=5)
    parser.add_argument('--verboser', '-v', dest='verbosity', action='count', default=0)
    parser.add_argument('--terser', '-q', dest='terseness', action='count', default=0)
    parser.add_argument('--progress', '-p', dest='progress', action='store_true', default=False)
    parser.add_argument('--series', '-s', dest='series', default=None) #comma or semi-colon separated
    parser.add_argument('--corpus', '-c', dest='corpus', default=None)

    args = parser.parse_args()
    ep_count = args.ep_count
    frame_count = args.frame_count
    series = args.series
    text_source = args.corpus
    if series is not None:
        series = re.split(r" *[,;] *", series)

    ## Either pick from nyer/lapham/corpora directory, or specify
    caption_gen = get_text_source(text_source)

    # make verbosity and terseness mutex
    # TODO: enforce this in argparser
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
    dl_and_comment(ep_count=ep_count, frame_count=frame_count, series=series, caption_gen=caption_gen, noprogress=noprogress)
    ### cliLogger.info(u"Would run dl_and_comment with (ep_count={})".format(ep_count))
    ### cliLogger.info(u"and get_a_line() returns: {}".format( get_a_line(caption_gen) ) )

if __name__ == "__main__":
    main()
