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

def add_subripitems(s, o):
    if o.index - s.index > 1:
        raise ValueError("Can only add consecutive items. [tried {}+{}]".format(s.index, o.index))
    else:
        return srt.SubRipItem(
                index = o.index,
                start = s.start,
                end = o.end,
                text = " ".join([s.text, o.text]),
                position = o.position
        )

srt.SubRipItem.get_duration = get_duration
srt.SubRipItem.get_seconds = get_seconds
srt.SubRipItem.__add__ = add_subripitems


# for monkey-patching into srt module itself:
def parse_srt(sub_file=None, **kwargs):
    srtLogger.debug(u"Using {} as SRT".format(sub_file))
    parser = SrtParser(filenames=sub_file)
    return parser.parse(sub_file, **kwargs)

def print_srt(sub_file=None):
    for i,l in enumerate(parse_srt(sub_file)):
        print(i,l)

"""
    move through SubRipItems in `sub_file`,
    grouping them together by sentence.
    e.g.:
    [u"This is the last time\nwe'll see",
    u"each other, you know."] =>
    [u"This is the last time we'll see each other, you know."]
"""
def sentence_reduce(subs, end_re=None):
    end_re = end_re or re.compile("([\.\?\!]+[\"\']*) *$")
    sentence_items = []
    acc = subs[0]
    for sub in subs[1:]:
        if re.search(end_re, acc.text):
            ## re-index for new order:
            acc.index = len(sentence_items) + 1
            sentence_items.append(acc)
            acc = sub
        else:
            acc += sub

    return sentence_items

srt.parse = parse_srt
srt.print_lines = print_srt
srt.sentence_reduce = sentence_reduce

srt.SubRipFile.sentence_reduce = sentence_reduce
