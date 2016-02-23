from __future__ import unicode_literals, print_function
from random import choice, sample
from functools import partial
import os, re, logging
from os import environ as ENV
import glob
from slurfilter import blacklisted

def Logger(name=None, lvl=1, console_lvl=None, fmt_string=None):
    if name:
        logger = logging.getLogger(u"acb.{}".format(name))
    else:
        logger = logging.getLogger(u"acb")

    logger.setLevel(lvl)

    fmt_string = fmt_string or u'%(name)-14s - %(levelname)-8s - %(message)s'
    formatter = logging.Formatter(fmt_string)

    if name is None:
        if len(logger.handlers):
            ch = [h for h in logger.handlers if type(h) is logging.StreamHandler][0]
        else:
            ch = logging.StreamHandler()

        if fmt_string:
            ch.setFormatter(formatter)
        if console_lvl:
            ch.setLevel(console_lvl)

    # only add handler if we don't already have one
        if not len(logger.handlers):
            print(u"Adding a handler for {} logger...".format(name))
            logger.addHandler(ch)

    return logger

""" Take dict of keys/values, assign as defaults to given dict and return it """
def setdefaults(d, **opts):
    if hasattr(d, "iteritems"):
        for (key, value) in opts.iteritems():
            d.setdefault(key, value)
        return d

    else:
        return None

""" Change extension of given filename """
def change_extension(inputfile, new_ext='srt'):
    dirname, basename = os.path.split(inputfile)
    label, ext = os.path.splitext(basename)
    new_base = '.'.join([label, new_ext])

    return os.path.join(dirname, new_base)

""" Adjustment of corpus line to clean up for composing """
# TODO: Redundant with .mysrt.junk_re?
def clean_line(string):
    pattern = r'[<\{].+?[>\}]'

    return re.sub(pattern, '', string)

# from Geoffrey Irving:
# http://stackoverflow.com/a/10886685
def insensitive_glob(pattern):
    def either(c):
        return "[{}{}]".format(c.lower(), c.upper()) if c.isalpha() else c
    return glob.glob(''.join(map(either,pattern)))

# from peterbe.com
# http://www.peterbe.com/plog/uniqifiers-benchmark
def uniqify(seq, idfun=None):
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

def force_iterable(val):
    if hasattr(val, '__iter__'):
        return val
    else:
        return [val]

""" Walk directory tree to find files of a type """
def files_from_path(inputpaths, usable_extensions):

    """ force iterable paths/extensions """
    inputpaths = force_iterable(inputpaths)
    usable_extensions = force_iterable(usable_extensions)

    inputpaths = map(os.path.expanduser, inputpaths)
    found_files = []
    for inputpath in inputpaths:
        isdir = os.path.isdir(inputpath)
        logger.debug("FILES_FROM_PATH parsed out: {}, (is directory? {})".format(inputpath, isdir))
        if isdir:
            """Check for valid formats within directory"""
            for root, dirs, files in os.walk(inputpath):
                logger.debug(u"Checking {}".format(root))
                for ext in usable_extensions:
                    files = insensitive_glob(os.path.join(root, '*.{}'.format(ext)))
                    if len(files) > 0:
                        logger.trace("Found {} files: {}".format(len(files), [os.path.basename(f) for f in files]))
                    found_files.extend(files)
        else:
            logger.error(u"Given file instead of directory; hope that's what you meant to do!")
            found_files.append(inputpath)
    return uniqify(found_files)

def get_tweetable_lines(src=None,min_length=1,max_length=127,count=None,use_filter=True):
    length_range = range(min_length, max_length+1)

    candidates = [l for l in src if len(l) in length_range]

    if use_filter:
        candidates = [l for l in candidates if blacklisted(l) == False]

    if count is None:
        return candidates
    else:
        return sample(candidates, count)

def get_tweetable_line(src=None, *args, **kwargs):
    try:
        return choice(get_tweetable_lines(src, *args, **kwargs))
    except IndexError:
        logger.error(u"No suitable line found...")

""" establish a basic module-level logger """
logging.addLevelName(1,u"TRACE")
logger = Logger(console_lvl=logging.DEBUG)
logger.trace = partial(logger.log,1)
info = logger.info
debug = logger.debug
error = logger.error
trace = logger.trace
logger.debug(u"Established module-level logger")
