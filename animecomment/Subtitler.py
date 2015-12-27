import os
from utility import *
from os import environ as ENV

from moviepy.video.io.VideoFileClip import VideoFileClip
from PrettyTextClip import PrettyTextClip

font_name= ENV.get('SUBTITLE_FONT', u"Open-Sans-Semibold")

""" Reasonable defaults for 720p input video? """
default_opts = {
    "method": "caption",
    "align": "south",
    "fontsize": 38,
    "color": "white",
    "stroke_color": "black",
    "stroke_width": 2,
    "size": (1280,695),
    "font": font_name,
    "shadow": (90, 1, 2, 2), # Option to disable this for fast render?
    "antialias": 2 # Can be set to False, or to something like 4
}

class Subtitler(object):
    def __init__(self, **kwargs):
        self.settings = setdefaults({}, **default_opts)
        self.settings.update(kwargs)

    def sub_generator(self, txt, **kwargs):
        txt = clean_line(txt)
        return PrettyTextClip(txt, **kwargs)

    def make_sub_opts(self, vidclip):
        """Tailor options in the sub_generator for video clip"""
        # decoration_factor is 1 for 480p, 2 for 720p, 3 for 1080p
        # this is used for IM stroke_width and x/y offsets in shadow.
        w, h = vidclip.size
        decoration_factor = int(round(h / 480.0))

        # render height leaves a margin below rendered subtitles
        render_height = int(round(h * 0.965))

        # font_factor 19.0 gets us fontsize=25 at 480p, 38 at 720p, and 57 at 1080p
        font_factor = 19.0

        sub_opts = {
            "size": ( w, render_height ),
            "fontsize": int(round(h / font_factor)),
            "stroke_width": decoration_factor,
            "shadow": (90, 1, decoration_factor, decoration_factor),
        }

        return sub_opts
