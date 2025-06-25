# Simplified utils from SearXNG

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

def get_url_host(url):
    return urlsplit(url).netloc

def get_url_scheme(url):
    return urlsplit(url).scheme

def get_url_query(url):
    return urlsplit(url).query

def get_url_path(url):
    return urlsplit(url).path

def new_url(scheme=None, netloc=None, path=None, query=None, fragment=None, url=None):
    if url is not None:
        (scheme, netloc, path, _, fragment) = urlsplit(url, scheme='https')

    if isinstance(query, dict):
        query = urlencode(query, doseq=True)

    return urlunsplit((scheme, netloc, path, query, fragment))

def clean_url(url):
    scheme, netloc, path, query, fragment = urlsplit(url)
    query_params = [k for k, v in parse_qsl(query) if not k.startswith('utm_')]
    return urlunsplit((scheme, netloc, path, urlencode(query_params, doseq=True), fragment))

def extract_text(html_content):
    # A very basic way to extract text, consider using a more robust library if needed
    return re.sub(r'<[^>]+>', '', html_content)
