# Simplified Baidu Engine

import httpx
import json
from urllib.parse import urlencode
from html import unescape
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# Engine-specific settings
BASE_URL = 'https://www.baidu.com/s'
RESULTS_PER_PAGE = 10

def search(query: str, pageno: int) -> list:
    """Search Baidu for general web results."""
    params = {
        "wd": query,
        "rn": RESULTS_PER_PAGE,
        "pn": (pageno - 1) * RESULTS_PER_PAGE,
        "tn": "json",
    }
    search_url = f"{BASE_URL}?{urlencode(params)}"

    try:
        resp = httpx.get(search_url, headers={'User-Agent': config.USER_AGENT})
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return []
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        return []

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return []

    results = []
    if not data.get("feed", {}).get("entry"):
        return []

    for entry in data["feed"]["entry"]:
        if not entry.get("title") or not entry.get("url"):
            continue

        title = unescape(entry["title"])
        url = entry.get("url", "")
        content = unescape(entry.get("abs", ""))
        
        # Skip baidu's own results which are often not useful
        if "baidu.com" in utils.get_url_host(url):
            continue

        results.append({
            'url': url,
            'title': title,
            'content': content
        })

    return results
