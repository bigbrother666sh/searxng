# Simplified Bing Engine

import httpx
from lxml import html
from urllib.parse import urlencode, urlparse, parse_qs
import base64
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# Engine-specific settings
BASE_URL = 'https://www.bing.com/search'

def search(query: str, pageno: int) -> list:
    """Search Bing for web results."""
    params = {
        'q': query,
        'first': (pageno - 1) * 10 + 1
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

    dom = html.fromstring(resp.text)
    results = []

    for result in dom.xpath('//ol[@id="b_results"]/li[contains(@class, "b_algo")]'):
        link = result.find('.//h2/a')
        if link is None:
            continue

        url = link.attrib.get('href')
        title = utils.extract_text(''.join(link.itertext()))

        content_element = result.find('.//p')
        content = utils.extract_text(''.join(content_element.itertext())) if content_element is not None else ''

        # Decode the URL if it's a Bing redirect
        if url and url.startswith('https://www.bing.com/ck/a?'):
            try:
                parsed_url = urlparse(url)
                parsed_query = parse_qs(parsed_url.query)
                encoded_url = parsed_query["u"][0][2:]
                encoded_url += '=' * (-len(encoded_url) % 4)
                url = base64.urlsafe_b64decode(encoded_url).decode()
            except (KeyError, IndexError, Exception):
                pass  # Keep the original URL if decoding fails

        results.append({
            'url': url,
            'title': title,
            'content': content
        })

    return results
