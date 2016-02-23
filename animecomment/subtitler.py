from .utility import *
from functools import partial

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from .prettytextclip import PrettyTextClip

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
        settings = setdefaults({}, **default_opts)
        settings.update(kwargs)
        return PrettyTextClip(txt, **settings)

    def compose_subs(self, vid_clip, txt, pos="top"):
        sub_opts = self.make_sub_opts(vid_clip)
        txt_clip = self.sub_generator(txt, **sub_opts)
        return CompositeVideoClip([vid_clip, txt_clip.set_pos(pos)])

    def make_sub_opts(self, vid_clip):
        """Tailor options in the sub_generator for video clip"""
        # decoration_factor is 1 for 480p, 2 for 720p, 3 for 1080p
        # this is used for IM stroke_width and x/y offsets in shadow.
        w, h = vid_clip.size
        decoration_factor = int(round(h / 480.0))

        # render_w/h leaves a margin below rendered subtitles
        # ASSUMING WE DO set_pos("top") WHEN COMPOSITING FRAME
        render_w = int(round(w * 0.95))
        render_h = int(round(h * 0.97))

        # (h / font_factor [@ 19.0]) gets us fontsize=25 at 480p, 38 at 720p, and 57 at 1080p
        #  .... @16 gets fontsize=30 at 480p
        font_factor = 16.0

        sub_opts = {
            "size": ( render_w, render_h ),
            "fontsize": int(round(h / font_factor)),
            "stroke_width": decoration_factor,
            "shadow": (90, 1, decoration_factor, decoration_factor),
        }

        return sub_opts
