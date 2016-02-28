import pysrt as srt
from .utility import *
from .parsers import SrtParser

srtLogger = Logger('srt')

### For monkey-patching onto SubRipItem:
def get_duration(self):
    try:
        return self.end - self.start
    except (AttributeError, TypeError):
        return NotImplemented

def get_seconds(self):
    return self.get_duration().ordinal / 1000.

srt.SubRipItem.get_duration = get_duration
srt.SubRipItem.get_seconds = get_seconds


# for monkey-patching into srt module itself:
def parse_srt(sub_file=None, **kwargs):
    srtLogger.debug(u"Using {} as SRT".format(sub_file))
    parser = SrtParser(filenames=sub_file)
    return parser.parse(sub_file, **kwargs)

def print_srt(sub_file=None):
    for i,l in enumerate(parse_srt(sub_file)):
        print(i,l)

def item_per_sentence(sub_file=None):
    pass

srt.parse = parse_srt
srt.print_lines = print_srt
srt.item_per_sentence = item_per_sentence
