from .utility import *
from .parsers import AssParser, SrtParser, TxtParser

class Corpus(object):
    def __init__(self, paths=["corpora"], formats=["ass", "srt", "txt"], parsers=None):
        paths = force_iterable(paths)
        formats = force_iterable(formats)

        self.parsers = {
            "ass": AssParser(paths),
            "srt": SrtParser(paths),
            "txt": TxtParser(paths)
        }
        self.parsers["fallback"] = self.parsers["txt"]
        self.parsers.update(parsers or {})
        self.filenames = files_from_path(paths, formats)

    def parse(self, filename=None, **kwargs):
        filename = filename or choice(self.filenames)
        ext = os.path.splitext(filename)[-1]
        parser = self.parsers.get(ext[1:], self.parsers['fallback'])
        return parser.parse(filename, **kwargs)
