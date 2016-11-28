from .utility import *
import crunchyroll
from crunchyroll.apis.meta import MetaApi
from .mysrt import srt

class Crunchyroll(object):
    all_series = None
    api = None
    have_fetched = False
    have_api = False

    @classmethod
    def fetch_all(cls):
        if cls.have_api is False:
            cls.get_api()
        cls.all_series = [series.name for series in cls.api.list_anime_series(limit=1000)]
        cls.have_fetched = True
        return cls.all_series

    @classmethod
    def get_api(cls, *args, **kwargs):
        cls.api = MetaApi(*args, **kwargs)
        cls.have_api = True
        return cls.api

    def __init__(self, logger=None, log_level=logging.WARNING, force_fetch=False, force_api=False):
        self.logger = Logger(u'crunchyroll')
        self.debug, self.info, self.error = (self.logger.debug, self.logger.info, self.logger.error)

        if force_api is True or Crunchyroll.have_api is False:
            self.debug("initiating API object...")
            Crunchyroll.get_api()

        if force_fetch is True or Crunchyroll.have_fetched is False:
            self.debug("fetching series names...")
            Crunchyroll.fetch_all()

        self.api = Crunchyroll.api
        self.series = Crunchyroll.all_series

    def search_series(self, q):
        """
            Using `self.series` list of series names, fetch any series
            containing 'q' in the name

            Our search for `q` is case-insensitive
            API search uses Crunchyroll's casing
        """
        matching_names = filter(lambda name: q.lower() in name.lower(), self.series)
        matching_series = list(self.api.search_anime_series(name)[0] for name in matching_names)
        return matching_series

    def get_random_series(self, count=1):
        random_series = [self.api.search_anime_series(name)[0] for name in sample(self.series, count)]
        return random_series

    def free_eps(self, series=None):
        series = series or self.get_random_series()[0]
        try:
            return [ep for ep in self.api.list_media(series) if ep.free_available]
        except Exception as e:
            self.error(u"Something has gone wrong finding free episodes...\n{}".format(e.message))
            return None

    def get_stream(self, episode, quality="720p"):
        resolution = int( re.sub(r"\D", "", quality) )

        if resolution > 480 and self.api.is_premium("anime") is False:
            self.error(u"Not authorized for premium Anime. Reducing to 480p")
            quality = "480p"
            resolution = 480

        try:
            vid_format, vid_quality = self.api.get_stream_formats(episode).get(quality)
            stream = self.api.get_media_stream(episode, vid_format, vid_quality)
            return stream
        except:
            self.error(u"Something has gone wrong getting media stream...")
            return None

    def get_srt_string(self, episode):
        stream = self.get_stream(episode)
        return stream.default_subtitles.decrypt().get_srt_formatted()

    def get_srt_items(self, episode):
        srt_string = self.get_srt_string(episode)
        return srt.from_string(srt_string)

    def get_res(self, stream):
        info = stream.stream_info
        width = info.findfirst('.//metadata/width').text
        height = info.findfirst('.//metadata/height').text
        return (int(width), int(height))

    def get_random_free_episode_urls(self, count=1, series=[None]):
        series = force_iterable(series)
        urls = []
        an_ep = None
        while len(urls) < count:
            try:
                an_ep = choice( self.free_eps(choice(series)) )
                self.debug(u"working with {}, checking hardsubs...".format(an_ep.url))
                if len(self.api.get_subtitle_stubs(an_ep)) > 0:
                    self.debug(u"appending {}".format(an_ep.url))
                    urls.append(an_ep.url)
            except Exception as e:
                self.error("Skipping {} because: hard-coded subs? no free episodes?".format(an_ep.url))
                self.error(e)
        return urls
