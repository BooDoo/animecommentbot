import os, sys, glob, json, re
import requests, gzip, io, csv
from random import choice, sample
# from zipfile import ZipFile
# from tempfile import TemporaryFile
import pysrt as srt

from __future__ import unicode_literals, print_function

from videogrep import *
from functools import partial

from imageio import imwrite
from moviepy.video.VideoClip import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

import crunchyroll
from crunchyroll.apis.meta import MetaApi

from utility import *
from mysrt import *
from MyCrunchyroll import *
from PrettyTextClip import PrettyTextClip
from Subtitler import Subtitler

### GLOBALS
verbose=True
queue_separator='====='

""" Establish a simple logger, using print() """
logger = Logger()
log = logger.log
debug = logger.debug
error = logger.error
