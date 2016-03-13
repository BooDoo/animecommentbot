from random import choice, sample
from .utility import *

import requests
from bs4 import BeautifulSoup

quotes_endpoint = "http://www.laphamsquarterly.org/archive/quotes&page={}"
quote_selector = "div.module-content > p" ### more specifically, we could add :nth-child(2)

def get_page_num(min_page=0, max_page=81):
    return choice(range(min_page, max_page))

def fetch_page(page_num=None):
    page_num = page_num or get_page_num()
    url = quotes_endpoint.format(page_num)
    return requests.get(url)

def parse_html(response):
    doc = BeautifulSoup(response.content, 'html.parser')
    return doc

def extract_text(doc, selector=None):
    selector = selector or quote_selector
    targets = doc.select(selector)
    texts = [target.text.strip() for target in targets]
    return texts

def get_quotes(count=4):
    texts = extract_text( parse_html( fetch_page( get_page_num() ) ) )
    if count > len(texts):
        count = len(texts)
        warn(u"Only found {} quotes. Reducing count.".format(len(texts)) )
    return sample(texts, count)

def get_a_quote():
    return get_quotes(1)[0]
