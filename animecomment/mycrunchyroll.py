from .utility import *
import crunchyroll
import requests
from crunchyroll.apis.meta import MetaApi
from crunchyroll.models import *
from crunchyroll.util import return_collection
from .mysrt import srt

class Crunchyroll(object):
    TAGS = (
        'action', 'adventure', 'comedy', 'drama', 'ecchi', 'fantasy',
        'historical', 'mecha', 'romance', 'science fiction', 'seinen', 'shoujo',
        'shounen', 'slice of life', 'sports',
        'mystery', 'supernatural',
        'staff picks')
    all_series = None
    api = None
    have_fetched = False
    have_api = False

    # @classmethod
    # def fetch_all(cls):
    #     if cls.have_api is False:
    #         cls.get_api()
    #     cls.all_series = [series.name for series in cls.api.list_anime_series(limit=1000)]
    #     cls.have_fetched = True
    #     return cls.all_series

    # @classmethod
    # def get_api(cls, *args, **kwargs):
    #     cls.api = MetaApi(*args, **kwargs)
    #     cls.have_api = True
    #     return cls.api

    def __init__(self, logger=None, log_level=logging.WARNING, force_fetch=False, force_api=False):
        self.logger = Logger(u'crunchyroll')
        self.debug, self.info, self.error = (self.logger.debug, self.logger.info, self.logger.error)

        if force_api is True or Crunchyroll.have_api is False:
            self.info(u'we don\'t use the API any more!!')
            # self.debug("initiating API object...")
            # Crunchyroll.get_api()

        if force_fetch is True or Crunchyroll.have_fetched is False:
            self.info(u'we can\'t fetch all series names anymore!!')
            # self.debug("fetching series names...")
            # Crunchyroll.fetch_all()

        # self.api = Crunchyroll.api
        # self.series = Crunchyroll.all_series

    # def search_series(self, q):
    #     """
    #         Using `self.series` list of series names, fetch any series
    #         containing 'q' in the name

    #         Our search for `q` is case-insensitive
    #         API search uses Crunchyroll's casing
    #     """
    #     matching_names = filter(lambda name: q.lower() in name.lower(), self.series)
    #     matching_series = list(self.api.search_anime_series(name)[0] for name in matching_names)
    #     return matching_series

    # @return_collection(Series)
    # def get_by_tag(self, tag, limit=5000, offset=0):
    #     tagged_series = self.api._android_api.list_series(
    #         media_type='anime',
    #         filter="tag:{}".format(tag),
    #         limit=limit,
    #         offset=offset)
    #     return tagged_series

    # def get_random_series(self, count=1):
    #    random_series = [self.api.search_anime_series(name)[0] for name in sample(self.series, count)]
    #    return random_series
    #
    # REPLACED BELOW:
    def get_random_series(self, count=1):
        series = []
        while len(series) < count:
            res = requests.get('https://crunchyroll.com/random/anime')
            series.append("/".join(res.url.split("/")[0:-1]))
        return series

    def parse_series(self, series):
        list_soup = BeautifulSoup(requests.get(series).text, 'html.parser')
        eps = list_soup.select("a.episode")
        eps_meta = list(({
            "href": get_ep_href(ep),
            "number": get_ep_number(ep),
            "title": get_ep_title(ep),
            "premium": get_ep_premium_flag(ep)
        } for ep in eps))
        return eps_meta

    def free_eps(self, series=None):
        series = series or self.get_random_series()[0]
        try:
            return [ep for ep in self.parse_series(series) if ep.get("premium") is False]
        except Exception as e:
            self.error(u"Something has gone wrong finding free episodes...\n{}".format(e.message))
            return None

    # NOPE, not anymore...
    # def get_stream(self, episode, quality="720p"):
    #     resolution = int( re.sub(r"\D", "", quality) )

    #     if resolution > 480 and self.api.is_premium("anime") is False:
    #         self.error(u"Not authorized for premium Anime. Reducing to 480p (hls-496)")
    #         quality = "hls-496"
    #         resolution = 480

    #     try:
    #         vid_format, vid_quality = self.api.get_stream_formats(episode).get(quality)
    #         stream = self.api.get_media_stream(episode, vid_format, vid_quality)
    #         return stream
    #     except:
    #         self.error(u"Something has gone wrong getting media stream...")
    #         return None

    # def get_srt_string(self, episode):
    #     stream = self.get_stream(episode)
    #     return stream.default_subtitles.decrypt().get_srt_formatted()

    # def get_srt_items(self, episode):
    #     srt_string = self.get_srt_string(episode)
    #     return srt.from_string(srt_string)

    # def get_res(self, stream):
    #     info = stream.stream_info
    #     width = info.findfirst('.//metadata/width').text
    #     height = info.findfirst('.//metadata/height').text
    #     return (int(width), int(height))

    def get_random_free_episode_urls(self, count=1, series=[None]):
        series = force_iterable(series)
        urls = []
        an_ep = None
        while len(urls) < count:
            try:
                an_ep = choice( self.free_eps(choice(series)) )
                # self.debug(u"working with {}, checking hardsubs...".format(an_ep.url))
                # if len(self.api.get_subtitle_stubs(an_ep)) > 0:
                self.debug(u"appending {}".format(an_ep.get("href")))
                urls.append(an_ep.get("href"))
            except Exception as e:
                self.error("Skipping {} because: hard-coded subs? no free episodes?".format(an_ep.get("href")))
                self.error(e)
        return urls
