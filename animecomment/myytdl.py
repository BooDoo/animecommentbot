import youtube_dl
import os
from .utility import *

class YTDownloader(object):
    """
    example:
        urls = [..., ..., ...]
        post_dl = partial(make_comment, count:5, 'output')
        ydl = YTDownloader(post_dl, logger=logger, noprogress=False, vidformat="720p")
        ydl.download(urls)
    """
    def __init__(self, callback, logger=None, log_level=logging.WARNING, progress_hooks=None, keepfile=False, noprogress=True, vidformat='480p'):
        self.logger = Logger(u"ytdl")
        self.keepfile = keepfile
        self.debug, self.info, self.error = (self.logger.debug, self.logger.info, self.logger.error)
        ### callback should be generated by a partial() call
        self.callback = callback
        ### only flag verbose if we're on TRACE log_level
        self.verbose = log_level < 10
        self.info(u"Setting noprogress to {}".format(noprogress))
        self.opts = {
            'logger': self.logger,
            'verbose': self.verbose,
            'progress_hooks': [self.finished_hook] + (progress_hooks or []),
            'format': vidformat,
            'writeinfojson': True,
            'noprogress': noprogress
        }

    # TODO: Add my own progress_hook
    ### see: https://github.com/rg3/youtube-dl/blob/d800609c62703e4e6edd2891a8432306462e4db3/youtube_dl/downloader/common.py#L234

    def finished_hook(self, d):
        if d['status'] == 'finished':
            filename = d["filename"]
            info_file = change_extension(filename, 'info.json')
            self.info(u"Done downloading, wrote to {}".format(filename))
            self.debug(u"calling {} with {} for {}".format(self.callback.func.__name__, self.callback.keywords, filename))
            self.callback(filename)
            if self.keepfile is False:
                self.info(u"Deleting {}...".format(filename))
                os.unlink(filename)
                self.info(u"Deleting {}...".format(info_file))
                os.unlink(info_file)
        else:
            pass

    def download(self, urls):
        urls = force_iterable(urls)
        with youtube_dl.YoutubeDL(self.opts) as ydl:
            try:
                ydl.download(urls)
            except youtube_dl.DownloadError as e:
                self.error(u"Trouble downloading {}?".format(urls))
                self.error(e)

