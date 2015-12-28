from __future__ import unicode_literals, print_function
from random import choice, sample
import os, re
from os import environ as ENV
import glob

verbose=True

""" Take dict of keys/values, assign as defaults to given dict and return it """
def setdefaults(d, **opts):
    if hasattr(d, "iteritems"):
        for (key, value) in opts.iteritems():
            d.setdefault(key, value)
        return d

    else:
        return None

class Logger(object):
    def __init__(self, verbose=False, output=None):
        self.verbose = verbose
        self.output = output or print

    """ Debug/Log/Error for outputting... """
    def debug(self, string):
        if self.verbose:
            self.output(u"[.] {}".format(string))

    def log(self, string):
        self.output(u"[+] {}".format(string))

    def error(self, string):
        self.output(u"[!] {}".format(string))

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

    """ work with or without Logger loaded """

    inputpaths = map(os.path.expanduser, inputpaths)
    found_files = []
    for inputpath in inputpaths:
        isdir = os.path.isdir(inputpath)
        print("FILES_FROM_PATH parsed out: {}, (is directory? {})".format(inputpath, isdir))
        if isdir:
            """Check for valid formats within directory"""
            for root, dirs, files in os.walk(inputpath):
                print(u"Checking {}".format(root))
                for ext in usable_extensions:
                    files = insensitive_glob(os.path.join(root, '*.{}'.format(ext)))
                    if len(files) > 0:
                        print("Found {} files: {}".format(len(files), [os.path.basename(f) for f in files]))
                    found_files.extend(files)
        else:
            error(u"Given file instead of directory; hope that's what you meant to do!")
            found_files.append(inputpath)
    return uniqify(found_files)
