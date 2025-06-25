# Simplified Quark Engine

import httpx
import json
import re
from urllib.parse import urlencode
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# Engine-specific settings
BASE_URL = 'https://quark.sm.cn/s'

def search(query: str, pageno: int) -> list:
    """Search Quark for general web results."""
    params = {
        'q': query,
        'layout': 'html',
        'page': pageno,
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

    results = []
    pattern = r'<script type="application/json" id="s-data-[^\"]+" data-used-by="hydrate">(.*?)<\/script>'
    matches = re.findall(pattern, resp.text, re.DOTALL)

    for match in matches:
        try:
            data = json.loads(match)
        except json.JSONDecodeError:
            continue

        initial_data = data.get('data', {}).get('initialData', {})
        source_category = data.get('extraData', {}).get('sc')

        # Focus on the most common and simple result type
        if source_category in ('ss_doc', 'ss_text', 'nature_result'):
            title = utils.extract_text(initial_data.get('titleProps', {}).get('content', '') or initial_data.get('title', ''))
            url = initial_data.get('sourceProps', {}).get('dest_url', '') or initial_data.get('url', '')
            content = utils.extract_text(
                initial_data.get('summaryProps', {}).get('content', '') or 
                initial_data.get('message', {}).get('replyContent', '') or 
                initial_data.get('desc', '')
            )

            if title and url:
                results.append({
                    'url': url,
                    'title': title,
                    'content': content
                })

    return results

