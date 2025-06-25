# Simplified GitHub Engine

import httpx
from urllib.parse import urlencode
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# Engine-specific settings
BASE_URL = 'https://api.github.com/search/repositories'
ACCEPT_HEADER = 'application/vnd.github.preview.text-match+json'

def search(query: str, pageno: int) -> list:
    """Search GitHub for repositories."""
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'page': pageno
    }
    search_url = f"{BASE_URL}?{urlencode(params)}"
    headers = {
        'User-Agent': config.USER_AGENT,
        'Accept': ACCEPT_HEADER
    }

    try:
        resp = httpx.get(search_url, headers=headers)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return []
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        return []

    try:
        response_json = resp.json()
    except Exception:
        return []

    results = []
    for item in response_json.get('items', []):
        title = item.get('full_name')
        url = item.get('html_url')
        content = item.get('description', '')

        if not title or not url:
            continue

        results.append({
            'url': url,
            'title': title,
            'content': content
        })

    return results
