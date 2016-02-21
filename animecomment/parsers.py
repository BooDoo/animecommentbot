from .utility import *
from .mysrt import srt
from .myass import ass

class Parser(object):
    """ uses:
        split_re, junk_re,
        __init__, load, flatten, clean, split, parse
    """
    split_re = None
    junk_re = None

    def __init__(self, paths=None, split_re=None, junk_re=None, filenames=None):
        pass

    def load(self, sub_file):
        pass

    def flatten(self, subs):
        pass

    def clean(self, subs, junk_re=None):
        pass

    def split(self, subs, split_re=None):
        pass

    def parse(self, sub_file, subs, flatten, clean, split):
        pass

class TxtParser(Parser):
    # TODO: Avoid false splits like 'Dr.' and 'Mrs.'
    split_re = re.compile("([\.\?\!]+[\"\']?) +")
    junk_re = re.compile("^\s+|\s+$|^\d+\. |^\s*[\-\>\#]+| ?[A-Z]+: | \-+ |[\<\[\(\{].+?[\]\)\>\}]| \>\>")

    def __init__(self, path=None, split_re=None, junk_re=None, filenames=None):
        self.split_re = split_re or TxtParser.split_re
        self.junk_re = junk_re or TxtParser.junk_re
        if filenames:
            self.filenames = force_iterable(filenames)
        else:
            self.filenames = files_from_path(path, "txt")

    def load(self, sub_file):
        with open(sub_file) as f:
            subs = f.readlines()

        if len(subs) > 0:
            return subs
        else:
            raise AttributeError("No lines to use in {}".format(sub_file))
            return None

    def flatten(self, subs):
        flat_subs = " ".join(subs).replace("\n", " ")
        return flat_subs

    def clean(self, subs, junk_re=None):
        junk_re = junk_re or self.junk_re
        subs = force_iterable(subs)

        clean_subs = [junk_re.sub("", sub) for sub in subs]

        return clean_subs if len(clean_subs) > 1 else clean_subs[0]

    def split(self, subs, split_re=None):
        split_re = split_re or self.split_re

        piece_iter = iter(split_re.split(subs))
        try:
            split_subs = [line+ (next(piece_iter, '') or '').strip() for line in piece_iter]
        except AttributeError:
            split_subs = subs
        return split_subs

    def parse(self, sub_file=None, subs=None, flatten=False, clean=True, split=False):
        if subs is None:
            sub_file = sub_file or choice(self.filenames)
            subs = self.load(sub_file)

        flatten = True if split else flatten

        subs = self.flatten(subs) if flatten else subs
        subs = self.clean(subs) if clean else subs
        subs = self.split(subs) if split else subs

        return subs

class AssParser(Parser):
    split_re = re.compile("([\.\?\!]+[\"\']?) +")
    junk_re = re.compile("^\s+|\s+$|^\d+\. |^\s*[\-\>\#]+| ?[A-Z]+: | \-+ |[\<\[\(\{].+?[\]\)\>\}]|\>")

    def __init__(self, paths=None, split_re=None, junk_re=None, filenames=None):
        self.split_re = split_re or AssParser.split_re
        self.junk_re = junk_re or AssParser.junk_re
        if filenames:
            self.filenames = force_iterable(filenames)
        else:
            self.filenames = files_from_path(path, "ass")


    def load(self, sub_file):
        with open(sub_file) as f:
            subs = ass.parse(f)

        if len(subs) > 0:
            return subs
        else:
            raise AttributeError("No lines to use in {}".format(sub_file))
            return None

    def flatten(self, subs):
        ## "\N replacement" FOR ASS TYPE:
        ## TODO: move to ass.document.Document.text?
        flat_subs = subs.text.replace("\N", "\n").replace("\n", " ")
        return flat_subs

    def clean(self, subs, junk_re=None):
        junk_re = junk_re or self.junk_re
        subs = force_iterable(subs)

        try:
            clean_subs = [junk_re.sub("", sub.text).replace("\N", "\n") for sub in subs]
        except AttributeError:
            clean_subs = [junk_re.sub("", sub) for sub in subs]

        ## "\N replacement" FOR ASS TYPE:
        ## TODO: move to ass.document.Document.text?
        clean_subs = [sub.replace("\N", "\n") for sub in clean_subs]

        return clean_subs if len(clean_subs) > 1 else clean_subs[0]

    def split(self, subs, split_re=None):
        split_re = split_re or self.split_re

        piece_iter = iter(split_re.split(subs))
        split_subs = [line+next(piece_iter, '').strip() for line in piece_iter]
        return split_subs

    def parse(self, sub_file, subs, flatten, clean, split):
        if subs is None:
            sub_file = sub_file or choice(self.filenames)
            subs = self.load(sub_file)

        flatten = True if split else flatten

        subs = self.flatten(subs) if flatten else subs
        subs = self.clean(subs) if clean else subs
        subs = self.split(subs) if split else subs

        return subs

class SrtParser(Parser):
    # TODO: Avoid false splits like 'Dr.' and 'Mrs.'
    split_re = re.compile("([\.\?\!]+[\"\']?) +")
    junk_re = re.compile("^\s+|\s+$|^\d+\. |^\s*[\-\>\#]+| ?[A-Z]+: | \-+ |[\<\[\(].+?[\]\)\>]| \>\>")

    def __init__(self, path=None, split_re=None, junk_re=None, filenames=None):
        self.split_re = split_re or SrtParser.split_re
        self.junk_re = junk_re or SrtParser.junk_re
        if filenames:
            self.filenames = force_iterable(filenames)
        else:
            self.filenames = files_from_path(path, "srt")

    def load(self, sub_file):
        try:
            subs = srt.open(sub_file)
        except:
            subs = srt.open(sub_file, "latin1")

        return subs

    def flatten(self, subs):
        flat_subs = subs.text.replace("\n", " ")
        return flat_subs

    def clean(self, subs, junk_re=None):
        junk_re = junk_re or self.junk_re
        subs = force_iterable(subs)

        try:
            clean_subs = [junk_re.sub("", sub.text) for sub in subs]
        except AttributeError:
            clean_subs = [junk_re.sub("", sub) for sub in subs]

        return clean_subs if len(clean_subs) > 1 else clean_subs[0]

    def split(self, subs, split_re=None):
        split_re = split_re or self.split_re

        piece_iter = iter(split_re.split(subs))
        split_subs = [line+next(piece_iter, '').strip() for line in piece_iter]
        return split_subs

    def parse(self, sub_file=None, subs=None, flatten=True, clean=True, split=True):
        if subs is None:
            sub_file = sub_file or choice(self.filenames)
            subs = self.load(sub_file)

        flatten = True if split else flatten

        subs = self.flatten(subs) if flatten else subs
        subs = self.clean(subs) if clean else subs
        subs = self.split(subs) if split else subs

        return subs
