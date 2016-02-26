import requests
from HTMLParser import HTMLParser

ny_endpoint = "http://www.newyorker.com/cartoons/random/randomAPI1"
html_parser = HTMLParser()

def unescape(*args, **kwargs):
    return html_parser.unescape(*args, **kwargs)

def get_nyer_caption(min_length=30, max_length=90):
    caption = ""
    while (len(caption) < min_length) or (len(caption) > max_length):
        caption = unescape(requests.get(ny_endpoint).json()[0]['caption'])
        # remove the fancy quotes on either side of the actual caption
        caption = caption[1:-1]
    return caption
