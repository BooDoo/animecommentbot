import crunchyroll
from crunchyroll.apis.meta import MetaApi
from random import choice, sample

api = MetaApi()
all_series = [series.name for series in api.list_anime_series(limit=1000)]

def search_series(q):
    """
        Using `all_series` list of series names, fetch any series
        containing 'q' in the name

        Our search for `q` is case-insensitive
        API search uses Crunchyroll's casing
    """
    matching_names = filter(lambda name: q.lower() in name.lower(), all_series)
    matching_series = list(api.search_anime_series(name)[0] for name in matching_names)
    return matching_series

def get_random_series(count=1):
    random_series = [api.search_anime_series(name)[0] for name in sample(all_series, count)]
    return random_series

def free_eps(series):
    try:
        return [ep for ep in api.list_media(series) if ep.free_available]
    except:
        error(u"Something has gone wrong finding free episodes...")
        return None

def get_stream(episode, quality="720p"):
    resolution = int( re.sub(r"\D", "", quality) )

    if resolution > 480 and api.is_premium("anime") is False:
        error(u"Not authorized for premium Anime. Reducing to 480p")
        quality = "480p"
        resolution = 480

    try:
        vid_format, vid_quality = api.get_stream_formats(episode).get(quality)
        stream = api.get_media_stream(episode, vid_format, vid_quality)
        return stream
    except:
        error(u"Something has gone wrong getting media stream...")
        return None

def get_res(stream):
    info = stream.stream_info
    width = info.findfirst('.//metadata/width').text
    height = info.findfirst('.//metadata/height').text
    return (int(width), int(height))

def get_random_free_episode_urls(count=1):
    urls = []
    an_ep = {"url": "no url"}
    while len(urls) < count:
        try:
            an_ep = choice( free_eps( get_random_series()[0] ) )
            if len(api.get_subtitle_stubs(an_ep)) > 0:
                urls.append(an_ep.url)
        except:
            error("Skipping {} because: hard-coded subs? no free episodes?".format(an_ep.url))
    return urls
