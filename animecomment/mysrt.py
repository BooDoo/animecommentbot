import pysrt as srt
from .utility import *

## REGULAR EXPRESIONS:
# Throw out junk strings (sound effects, speaker labels...)
junk_re = re.compile("^\d+\. |^\s*[\-\>\#]+| ?[A-Z]+: | \-+ |[\<\[\(\{].+?[\]\)\>\}]| \>\>")

# Split on meaningful punctuation followed by a space
# TODO: Avoid false splits like 'Dr.' and 'Mrs.'
#       Avoid truncating within a quotation.
split_re = re.compile("([\.\?\!]+\"?) +")

def parse_srt(sub_file=None):
    # random sourcing now handled in the Corpus class:
    # sub_file = sub_file or get_random_srt()

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


srt.parse_srt = parse_srt
srt.get_tweetable_lines = get_tweetable_lines
srt.get_tweetable_line = get_tweetable_line
srt.print_srt = print_srt
