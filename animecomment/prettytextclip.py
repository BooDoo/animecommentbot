from .utility import *
import tempfile
import subprocess as sp

from imageio import imread

from moviepy.tools import subprocess_call
from moviepy.config import get_setting
from moviepy.video.VideoClip import *

""" Anti-alias scaling factor """
def aa_scale(src, factor):
    try:
        return tuple([x*factor for x in src])
    except TypeError:
        return src*factor

### PrettyTextClip is like a TextClip but supports drop shadow and antialiased rendering
class PrettyTextClip(TextClip):
    default_opts = {
            "txt": None, "filename": None, "size": None, "color": 'black',
            "bg_color": 'transparent', "fontsize": None, "font": 'Courier',
            "stroke_color": None, "stroke_width": 1, "method": 'label',
            "kerning": None, "align": 'center', "interline": None,
            "tempfilename": None, "temptxt": None,
            "transparent": True, "remove_temp": True,
            "shadow": None, "antialias": 4,
            "print_cmd": False
    }

    def __init__(self, txt=None, filename=None, size=None, color='black',
                 bg_color='transparent', fontsize=None, font='Courier',
                 stroke_color=None, stroke_width=1, method='label',
                 kerning=None, align='center', interline=None,
                 tempfilename=None, temptxt=None,
                 transparent=True, remove_temp=True,
                 shadow=None, antialias=4,
                 print_cmd=False):

        # ADDED Antialiasing
        aa_factor= 1 if not antialias else antialias

        if txt is not None:
            if temptxt is None:
                temptxt_fd, temptxt = tempfile.mkstemp(suffix='.txt')
                try:  # only in Python3 will this work
                    os.write(temptxt_fd, bytes(txt, 'UTF8'))
                except TypeError:  # oops, fall back to Python2
                    os.write(temptxt_fd, txt.encode("UTF-8"))
                os.close(temptxt_fd)
            txt = '@' + temptxt
        else:
            # use a file instead of a text.
            txt = "@%" + filename

        if size is not None:
            size = ('' if size[0] is None else size[0],
                    '' if size[1] is None else size[1])

        if shadow is not None:
            shadow = (80 if shadow[0] is None else shadow[0],
                       1 if shadow[1] is None else shadow[1],
                       2 if shadow[2] is None else shadow[2],
                       2 if shadow[3] is None else shadow[3])

        cmd = ( [get_setting("IMAGEMAGICK_BINARY"),
               "-density", str(aa_scale(72, aa_factor)), # ADDED Anti-aliasing
               "-background", bg_color,
               "-fill", color,
               "-font", font])

        if fontsize is not None:
            cmd += ["-pointsize", "%d" % fontsize]
        if kerning is not None:
            cmd += ["-kerning", "%0.1f" % aa_scale(kerning, aa_factor)]
        if stroke_color is not None:
            cmd += ["-stroke", stroke_color, "-strokewidth",
                    "%.01f" % aa_scale(stroke_width, aa_factor)]
        if size is not None:
            cmd += ["-size", "%sx%s" % aa_scale(size, aa_factor)]
        if align is not None:
            cmd += ["-gravity", align]
        if interline is not None:
            cmd += ["-interline-spacing", "%d" % interline]

        if tempfilename is None:
            tempfile_fd, tempfilename = tempfile.mkstemp(suffix='.png')
            os.close(tempfile_fd)

        # ADDED Dropshadow rendering
        if shadow is not None:
            shadow_cmd = ( ["(", "+clone",
                          "-shadow", "%sx%s+%s+%s" % (tuple([shadow[0]]) + aa_scale(shadow[1:], aa_factor)),
                          ")",
                          "-compose", "DstOver",
                          "-flatten"])
        else:
            shadow_cmd = []

        cmd += ["%s:%s" % (method, txt)]
        cmd += shadow_cmd
        cmd += ["-resample", "72"]
        cmd += ["-type", "truecolormatte", "PNG32:%s" % tempfilename]

        if print_cmd:
            print( " ".join(cmd) )
        try:
            subprocess_call(cmd, verbose=True)
        except (IOError,OSError) as err:
            error = ("MoviePy Error: creation of %s failed because "
              "of the following error:\n\n%s.\n\n."%(filename, str(err))
               + ("This error can be due to the fact that "
                    "ImageMagick is not installed on your computer, or "
                    "(for Windows users) that you didn't specify the "
                    "path to the ImageMagick binary in file conf.py, or."
                    "that the path you specified is incorrect" ))
            raise IOError(error)

        # WORKAROUND: Weird error when tempfilename is Unicode instead of str, so...
        temp_img = imread(tempfilename)
        ImageClip.__init__(self, temp_img, transparent=transparent)
        # END WORKAROUND
        self.txt = txt
        self.color = color
        self.stroke_color = stroke_color
        self.cmd = cmd # ADDED store cmd list

        if remove_temp:
            if os.path.exists(tempfilename):
                os.remove(tempfilename)
            if os.path.exists(temptxt):
                os.remove(temptxt)


