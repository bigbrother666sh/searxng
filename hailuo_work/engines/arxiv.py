# Simplified ArXiv Engine

import httpx
from lxml import etree
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# Engine-specific settings
BASE_URL = 'https://export.arxiv.org/api/query?search_query=all:{query}&start={offset}&max_results={limit}'
LIMIT = 10

# XPath definitions
ARXIV_NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

def search(query: str, pageno: int) -> list:
    """Search ArXiv for scientific preprints."""
    offset = (pageno - 1) * LIMIT
    search_url = BASE_URL.format(query=query, offset=offset, limit=LIMIT)
    
    try:
        resp = httpx.get(search_url, headers={'User-Agent': config.USER_AGENT})
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return []
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        return []

    dom = etree.fromstring(resp.content)
    results = []

    for entry in dom.xpath('//atom:entry', namespaces=ARXIV_NAMESPACES):
        title_element = entry.xpath('.//atom:title', namespaces=ARXIV_NAMESPACES)
        url_element = entry.xpath('.//atom:id', namespaces=ARXIV_NAMESPACES)
        content_element = entry.xpath('.//atom:summary', namespaces=ARXIV_NAMESPACES)

        if not all([title_element, url_element, content_element]):
            continue

        title = title_element[0].text.strip()
        url = url_element[0].text.strip()
        content = content_element[0].text.strip()

        results.append({
            'url': url,
            'title': title,
            'content': content
        })

    return results
