# Simplified Wikipedia Engine

import httpx
from urllib.parse import quote
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# Engine-specific settings
BASE_URL = 'https://en.wikipedia.org/api/rest_v1/page/summary/{query}'

def search(query: str, pageno: int) -> list:
    """Search Wikipedia for a summary of the given query."""
    # Wikipedia API doesn't have pages in the same way, so pageno is ignored.
    if pageno > 1:
        return []
        
    search_url = BASE_URL.format(query=quote(query))
    headers = {'User-Agent': config.USER_AGENT}

    try:
        resp = httpx.get(search_url, headers=headers)
        
        if resp.status_code == 404:
            return []
        resp.raise_for_status()

    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return []
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        return []

    try:
        data = resp.json()
    except Exception:
        return []

    if not data or data.get('type') == 'disambiguation':
        return []

    title = data.get('title', '')
    url = data.get('content_urls', {}).get('desktop', {}).get('page', '')
    content = data.get('extract', '')

    if not title or not url:
        return []

    return [{
        'url': url,
        'title': title,
        'content': content
    }]

