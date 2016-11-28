# import os, sys, glob, json, re
# import requests, gzip, io, csv
# from random import choice, sample
# import pysrt as srt

# from videogrep import *
# from functools import partial

# from imageio import imwrite
# from moviepy.video.VideoClip import *
# from moviepy.video.tools.subtitles import SubtitlesClip
# from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# import crunchyroll
# from crunchyroll.apis.meta import MetaApi

from . import utility
from . import mysrt as srt
from . import corpus
from . import mycrunchyroll as crunchyroll
from .prettytextclip import PrettyTextClip
from .subtitler import Subtitler

### GLOBALS
global queue_separator
global logger
queue_separator='====='

logger = utility.logger
