# Simplified Ebay Engine

import httpx
from lxml import html
from urllib.parse import quote, urlencode
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# Engine-specific settings
BASE_URL = 'https://www.ebay.com/sch/i.html'

def search(query: str, pageno: int) -> list:
    """Search Ebay for products."""
    params = {
        '_nkw': query,
        '_sacat': pageno
    }
    search_url = BASE_URL + '?' + quote(urlencode(params))

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

    for result in dom.xpath('//li[contains(@class, "s-item")]'):
        url_element = result.find('.//a[@class="s-item__link"]')
        title_element = result.find('.//h3[@class="s-item__title"]')

        if url_element is None or title_element is None:
            continue

        url = url_element.attrib.get('href', '')
        title = utils.extract_text(''.join(title_element.itertext()))

        content_elements = result.xpath('.//div[contains(@class, "s-item__detail")]//span')
        content = ' '.join([utils.extract_text(''.join(el.itertext())) for el in content_elements])

        results.append({
            'url': url,
            'title': title,
            'content': content
        })

    return results
