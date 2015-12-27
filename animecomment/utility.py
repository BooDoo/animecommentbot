import os
from future import print_function

""" Take dict of keys/values, assign as defaults to given dict and return it """
def setdefaults(d, **opts):
    if hasattr(d, "iteritems"):
        for (key, value) in d.iteritems():
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

""" Simply changing extension of a given filename """
def change_extension(inputfile, new_ext='srt'):
    dirname, basename = os.path.split(inputfile)
    label, ext = os.path.splitext(basename)
    new_base = '.'.join([label, new_ext])

    return os.path.join(dirname, new_base)

""" Adjustment of corpus line to clean up for composing """
def clean_line(string):
    pattern = r'[<\{].+?[>\}]'

    return re.sub(pattern, '', string)

""" Walk directory tree to find files of a type """
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


