from __future__ import unicode_literals, print_function
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

import utility
import mysrt as srt
import corpus
import mycrunchyroll as crunchyroll
from prettytextclip import PrettyTextClip
from subtitler import Subtitler

### GLOBALS
verbose=True
queue_separator='====='

""" Establish a simple logger, using print() """
logger = utility.Logger()
log = logger.log
debug = logger.debug
error = logger.error
