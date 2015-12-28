#!/usr/bin/env python2

#### TODO:
# - ... more corpora?
# - Get it straight from CrunchyRoll! (yeah right...)

import os, sys, glob, json, re
import requests, gzip, io, csv
from random import choice, sample
from zipfile import ZipFile
from tempfile import TemporaryFile
import pysrt as srt

from videogrep import *
from functools import partial

from imageio import imwrite
from moviepy.video.VideoClip import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

import crunchyroll
from crunchyroll.apis.meta import MetaApi

import youtube_dl

### GLOBALS
verbose=True
font_name='Open-Sans-Semibold'
queue_separator='====='

## For Crunchyroll:
api = MetaApi()
all_series = [series.name for series in api.list_anime_series(limit=1000)]

## REGULAR EXPRESIONS:
# Throw out junk strings (sound effects, speaker labels...)
junk_re = re.compile("^\d+\. |^\s*[\-\>\#]+| ?[A-Z]+: | \-+ |[\<\[\(].+?[\]\)\>]| \>\>")

# Split on meaningful punctuation followed by a space
# TODO: Avoid false splits like 'Dr.' and 'Mrs.'
split_re = re.compile("([\.\?\!]+\"?) +")

#################################################################
# ____  ____  ____  _  _   ___     _     _  _  ____  __  __
#(    \(  __)(  _ \/ )( \ / __)   ( )   / )( \(_  _)(  )(  )
# ) D ( ) _)  ) _ () \/ (( (_ \  (_ _)  ) \/ (  )(   )( / (_/\
#(____/(____)(____/\____/ \___/   (_)   \____/ (__) (__)\____/
#
#################################################################

def debug(string):
    if verbose:
        print(u"[.] {}".format(string))


def log(string):
    print(u"[+] {}".format(string))


def error(string):
    print(u"[!] {}".format(string))


def change_extension(inputfile, new_ext='srt'):
    dirname, basename = os.path.split(inputfile)
    label, ext = os.path.splitext(basename)
    new_base = '.'.join([label, new_ext])

    return os.path.join(dirname, new_base)

def clean_line(string):
    pattern = r'[<\{].+?[>\}]'

    return re.sub(pattern, '', string)

def aa_scale(src, factor):
    try:
        return tuple([x*factor for x in src])
    except TypeError:
        return src*factor


#################################################################
#  __   _  _  ____  ____  ____  __  ____  ____  ____     _
# /  \ / )( \(  __)(  _ \(  _ \(  )(    \(  __)/ ___)   ( )
#(  O )\ \/ / ) _)  )   / )   / )(  ) D ( ) _) \___ \  (_ _)
# \__/  \__/ (____)(__\_)(__\_)(__)(____/(____)(____/   (_)
# ____  __  ___   ___  _  _  ____   __    ___  __ _  ____
#(  _ \(  )/ __) / __)( \/ )(  _ \ / _\  / __)(  / )/ ___)
# ) __/ )(( (_ \( (_ \ )  /  ) _ (/    \( (__  )  ( \___ \
#(__)  (__)\___/ \___/(__/  (____/\_/\_/ \___)(__\_)(____/
#
#################################################################

### our PrettyTextClip is like a TextClip but supports drop shadow and antialiased rendering
### TODO: THERE'S GOT TO BE A BETTER WAY (clean up for a PR against moviepy? some kind of decorator?)
class PrettyTextClip(TextClip):
    def __init__(self, txt=None, filename=None, size=None, color='black',
                 bg_color='transparent', fontsize=None, font='Courier',
                 stroke_color=None, stroke_width=1, method='label',
                 kerning=None, align='center', interline=None,
                 tempfilename=None, temptxt=None,
                 transparent=True, remove_temp=True,
                 shadow=None, antialias=4,
                 print_cmd=False):

        import tempfile
        import subprocess as sp

        from moviepy.tools import subprocess_call
        from moviepy.config import get_setting

        # from moviepy.video.VideoClip import *

        aa_factor= 1 if not antialias else antialias

        if txt is not None:
            if temptxt is None:
                temptxt_fd, temptxt = tempfile.mkstemp(suffix='.txt')
                try:  # only in Python3 will this work
                    os.write(temptxt_fd, bytes(txt, 'UTF8'))
                except TypeError:  # oops, fall back to Python2
                    os.write(temptxt_fd, txt.encode("UTF-8"))
                os.close(temptxt_fd)
            txt = '@' + temptxt
        else:
            # use a file instead of a text.
            txt = "@%" + filename

        if size is not None:
            size = ('' if size[0] is None else size[0],
                    '' if size[1] is None else size[1])

        if shadow is not None:
            shadow = (80 if shadow[0] is None else shadow[0],
                       1 if shadow[1] is None else shadow[1],
                       2 if shadow[2] is None else shadow[2],
                       2 if shadow[3] is None else shadow[3])

        cmd = ( [get_setting("IMAGEMAGICK_BINARY"),
               "-density", str(aa_scale(72, aa_factor)),
               "-background", bg_color,
               "-fill", color,
               "-font", font])

        if fontsize is not None:
            cmd += ["-pointsize", "%d" % fontsize]
        if kerning is not None:
            cmd += ["-kerning", "%0.1f" % aa_scale(kerning, aa_factor)]
        if stroke_color is not None:
            cmd += ["-stroke", stroke_color, "-strokewidth",
                    "%.01f" % aa_scale(stroke_width, aa_factor)]
        if size is not None:
            cmd += ["-size", "%sx%s" % aa_scale(size, aa_factor)]
        if align is not None:
            cmd += ["-gravity", align]
        if interline is not None:
            cmd += ["-interline-spacing", "%d" % interline]

        if tempfilename is None:
            tempfile_fd, tempfilename = tempfile.mkstemp(suffix='.png')
            os.close(tempfile_fd)

        if shadow is not None:
            shadow_cmd = ( ["(", "+clone",
                          "-shadow", "%sx%s+%s+%s" % (tuple([shadow[0]]) + aa_scale(shadow[1:], aa_factor)),
                          ")",
                          "-compose", "DstOver",
                          "-flatten"])

        cmd += ["%s:%s" % (method, txt)]
        cmd += shadow_cmd
        cmd += ["-resample", "72"]
        cmd += ["-type", "truecolormatte", "PNG32:%s" % tempfilename]

        if print_cmd:
            print( " ".join(cmd) )

        try:
            subprocess_call(cmd, verbose=verbose)
        except (IOError,OSError) as err:
            error = ("MoviePy Error: creation of %s failed because "
              "of the following error:\n\n%s.\n\n."%(filename, str(err))
               + ("This error can be due to the fact that "
                    "ImageMagick is not installed on your computer, or "
                    "(for Windows users) that you didn't specify the "
                    "path to the ImageMagick binary in file conf.py, or."
                    "that the path you specified is incorrect" ))
            raise IOError(error)

        ImageClip.__init__(self, tempfilename, transparent=transparent)
        self.txt = txt
        self.color = color
        self.stroke_color = stroke_color

        if remove_temp:
            if os.path.exists(tempfilename):
                os.remove(tempfilename)
            if os.path.exists(temptxt):
                os.remove(temptxt)

#################################################################
#  ___  __  ____  ____
# / __)/  \(  _ \(  __)
#( (__(  O ))   / ) _)
# \___)\__/(__\_)(____)
# _  _  ____  ____  _  _   __  ____  ____
#( \/ )(  __)(_  _)/ )( \ /  \(    \/ ___)
#/ \/ \ ) _)   )(  ) __ ((  O )) D (\___ \
#\_)(_/(____) (__) \_)(_/ \__/(____/(____/
#
#################################################################

def sub_generator(txt, **kwargs):
    """ Reasonable defaults for 720p input video """
    kwargs.setdefault('method', 'caption')
    kwargs.setdefault('align', 'south')
    kwargs.setdefault('fontsize', 38)
    kwargs.setdefault('color', 'white')
    kwargs.setdefault('stroke_color', 'black')
    kwargs.setdefault('stroke_width', 2)
    kwargs.setdefault('size', (1280,695))
    kwargs.setdefault('font', font_name)
    kwargs.setdefault('shadow', (90, 1, 2, 2)) # Need option to disable this for fast render
    kwargs.setdefault('antialias', 2) # Can be set to False, or to something like 4

    txt = clean_line(txt)
    return PrettyTextClip(txt, **kwargs)

def make_sub_opts(vidclip):
    """Tailor options in the sub_generator for video clip"""
    # decoration_factor is 1 for 480p, 2 for 720p, 3 for 1080p
    # this is used for IM stroke_width and x/y offsets in shadow.
    w, h = vidclip.size
    decoration_factor = int(round(h / 480.0))

    # render height leaves a margin below rendered subtitles
    render_height = int(round(h * 0.965))

    # font_factor 19.0 gets us fontsize=25 at 480p, 38 at 720p, and 57 at 1080p
    font_factor = 19.0

    sub_opts = {
        "size": ( w, render_height ),
        "fontsize": int(round(h / font_factor)),
        "stroke_width": decoration_factor,
        "shadow": (90, 1, decoration_factor, decoration_factor),
    }

    return sub_opts

def compose_subs(vid_file, sub_file):
    vidclip = VideoFileClip(vid_file)
    # Scale effects to input video:
    sub_opts = make_sub_opts(vidclip)
    generator = partial(sub_generator, **sub_opts)

    txtclip = SubtitlesClip(sub_file, generator)
    return CompositeVideoClip([vidclip, txtclip])

def get_mid_frame(clip):
    return clip.get_frame(clip.duration * .5)

def write_mid_frame(clip, outpath):
    imwrite(outpath, get_mid_frame(clip))
    return outpath

#################################################################
#
#
#  Acquisition/corpus building tools:
#
#
#################################################################

## Fetching SRTs when we know season+episode count and a naming convention
def fetch_srts(seasons, episodes, file_template, base_url, target_dir="./corpus"):
    written = []
    for season in range(1,seasons+1):
        for episode in range(1,episodes+1):
            filename = file_template % (season, episode)
            url = os.path.join(base_url, filename)
            write_target = os.path.join(target_dir, filename)
            with open(write_target, 'w') as f:
                f.write(requests.get(url).content)
                written.append(write_target)
                debug(u"wrote to {}".format(write_target))
    return written

#################################################################
#
#
# Selecting/parsing SRTs from ./corpora:
#
#
#################################################################


def get_random_srt(inputpath="corpora"):
    return choice(files_from_path(inputpath, "srt"))

def get_random_mkv(inputpath="/mnt/Media/Videos"):
    return choice(files_from_path(inputpath, "mkv"))

def files_from_path(inputpath, ext):
    """Take directory or file path and return list of valid video files (*.{ext})"""
    inputpath = os.path.expanduser(inputpath)
    isdir = os.path.isdir(inputpath)
    found_files = []
    debug("FILES_FROM_PATH parsed out: {}, (is directory? {})".format(inputpath, isdir))
    if isdir:
        """Check for valid formats within directory"""
        """TODO: Be case-insensitive? Would need to rewrite glob.glob()"""
        for root, dirs, files in os.walk(inputpath):
            debug(u"Checking {}".format(root))
            files = glob.glob(os.path.join(root, "*.{}".format(ext) ) )
            if len(files) > 0:
                debug(u"Found {} files: {}".format(len(files), [os.path.basename(f) for f in files]))
            found_files.extend(files)
            ## TODO: Restore suport for muliple extensions?
            # for ext in usable_extensions:
            #     files = glob.glob(os.path.join(root, '*.{}'.format(ext)))
            #     if len(files) > 0:
            #         debug("Found {} files: {}".format(len(files), [os.path.basename(f) for f in files]))
            #     found_files.extend(files)
    else:
        error(u"Given file instead of directory; hope that's what you meant to do!")
        found_files.append(inputpath)
    return found_files

def parse_srt(sub_file=None):
    sub_file = sub_file or get_random_srt()

    debug(u"Using {} as SRT".format(sub_file))

    try:
        subs = srt.open(sub_file)
    except:
        subs = srt.open(sub_file, "latin1")

    flat_subs = subs.text.replace("\n", " ")
    clean_subs = junk_re.sub(" ", flat_subs)
    piece_iter = iter(split_re.split(clean_subs))
    split_subs = [l+next(piece_iter, '').strip() for l in piece_iter]

    return split_subs

def get_tweetable_lines(src=None, **kwargs):
    min_length = kwargs.pop('min_length', 1)
    max_length = kwargs.pop('max_length', 140)
    length_range = range(min_length, max_length+1)

    try:
        src = parse_srt(src)
    except:
        error(u"Couldn't parse as SRT source: {}".format(src))

    return list(l for l in src if len(l) in length_range)

def get_tweetable_line(src=None, **kwargs):
    try:
        return choice(get_tweetable_lines(src, **kwargs))
    except IndexError:
        error(u"No suitable line found in SRT, trying another...")
        return get_tweetable_line(src, **kwargs)

def print_srt(sub_file=None):
    for i,l in enumerate(parse_srt(sub_file)):
        print(i,l)

###################################################################
#
#
#  MAIN BEHAVIOR
#
#
###################################################################

def make_comment(count=1, out_path="output", vid_file=None):
    vid_file = vid_file or get_random_mkv()
    log(u"Using {} as source...".format(os.path.basename(vid_file)))
    label = os.path.basename(vid_file).split(".")[0].replace(" ","").lower()
    vid_clip = VideoFileClip(vid_file)
    earliest = int(vid_clip.duration * 0.1)
    latest = int(vid_clip.duration * 0.9)
    valid_range = range(earliest, latest+1)

    sub_opts = make_sub_opts(vid_clip);

    with open("queue.txt", "a") as queue:
        for n in range(1, count+1):
            txt_line = get_tweetable_line(min_length=30, max_length=90)
            debug(u"Using {} as subtitle...".format(txt_line))
            txt_clip = sub_generator(txt_line, **sub_opts)

            composed = CompositeVideoClip([vid_clip, txt_clip])
            frame = composed.get_frame(choice(valid_range))
            log(u"\tWriting {0} of {1:03d}...".format(n, count) )
            image_path = u"{0}/{1}_{2:03d}.png".format(out_path, label, n)
            imwrite(image_path, frame)
            queue.write(u"{0}{1}{2}\n".format(image_path, queue_separator, txt_line).encode('utf8', 'replace') )

###############################################################
#
#
# CrunchyRoll stuff!
#
#
###############################################################

def search_series(q):
    """
        Using `all_series` list of series names, fetch any series
        containing 'q' in the name

        Our search for `q` is case-insensitive
        API search uses Crunchyroll's casing
    """
    matching_names = filter(lambda name: q.lower() in name.lower(), all_series)
    matching_series = list(api.search_anime_series(name)[0] for name in matching_names)
    return matching_series

def get_random_series(count=1):
    random_series = [api.search_anime_series(name)[0] for name in sample(all_series, count)]
    return random_series

def free_eps(series):
    try:
        return [ep for ep in api.list_media(series) if ep.free_available]
    except:
        error(u"Something has gone wrong finding free episodes...")
        return None

def get_stream(episode, quality="720p"):
    resolution = int( re.sub(r"\D", "", quality) )

    if resolution > 480 and api.is_premium("anime") is False:
        error(u"Not authorized for premium Anime. Reducing to 480p")
        quality = "480p"
        resolution = 480

    try:
        vid_format, vid_quality = api.get_stream_formats(episode).get(quality)
        stream = api.get_media_stream(episode, vid_format, vid_quality)
        return stream
    except:
        error(u"Something has gone wrong getting media stream...")
        return None

def get_res(stream):
    info = stream.stream_info
    width = info.findfirst('.//metadata/width').text
    height = info.findfirst('.//metadata/height').text
    return (int(width), int(height))

#################################################################################
#
#
#  Youtube-dl things!
#
#
#################################################################################

class MyLogger(object):
    def debug(self, msg):
        debug(msg)
    def warning(self, msg):
        log(msg)
    def error(self, msg):
        error(msg)

def comment_hook(d):
    if d['status'] == 'finished':
        log(u"Done downloading, wrote to {}".format(d["filename"]))
        log(u"Let's try to get some screenshots...")
        make_comment(5, 'output', d["filename"])
        log(u"Deleting {}...".format(d["filename"]))
        os.unlink(d["filename"])

## Some other ydl_opts:
# mutex:
# |  outtmpl            ## output file name template
# |  useid              ## use video id for output filename
#
# 
# other:
#   download_archive    ## ????
#   username / password ## duh
#   max_filesize

ydl_opts = {
    'logger': MyLogger(),
    'progress_hooks': [comment_hook],
    'format': '480p' ## '720p-0'  # ???
    # 'postprocessors': [{ }] # ???
        }

def dl_and_comment(urls):
    if type(urls) is not list:
        urls = [urls]
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(urls)
        except youtube_dl.DownloadError as e:
            error("Trouble downloading {}?".format(urls))


#######################################################
#
#
# When run as a script...
#
#
#######################################################

def main():
    import argparse
    global verbose

    parser = argparse.ArgumentParser(description=u"Download videos, randomly select frames, put text over them.")
    parser.add_argument('--count', '-c', dest='count', type=int, default=5)
    parser.add_argument('--verbose', '-v', dest='verbose', action="store_true", default=False)

    args = parser.parse_args()
    verbose = args.verbose
    count = args.count

    try:
        urls = [choice( free_eps(series) ).url for series in get_random_series(count)]
    except:
        urls = []
        raise

    dl_and_comment(urls)

if __name__ == "__main__":
    main()
