
import base64
import re
import time
from urllib.parse import parse_qs, urlencode, urlparse
from lxml import html, etree

from core.utils import eval_xpath, extract_text, eval_xpath_list, eval_xpath_getindex

base_url = 'https://www.bing.com/search'

def _page_offset(pageno):
    return (int(pageno) - 1) * 10 + 1

async def request(query: str, page_number: int = 1, time_range: str = None, language: str = 'en-US', region: str = 'en-US', **kwargs) -> dict:
    query_params = {
        'q': query,
        'pq': query,
    }

    if page_number > 1:
        query_params['first'] = _page_offset(page_number)
    if page_number == 2:
        query_params['FORM'] = 'PERE'
    elif page_number > 2:
        query_params['FORM'] = f'PERE{page_number - 2}'

    url = f'{base_url}?{urlencode(query_params)}'

    if time_range:
        unix_day = int(time.time() / 86400)
        time_ranges = {'day': '1', 'week': '2', 'month': '3', 'year': f'5_{unix_day-365}_{unix_day}'}
        if time_range in time_ranges:
            url += f'&filters=ex1:"ez{time_ranges[time_range]}"'

    headers = {
        'Cookie': f'_EDGE_CD=m={region}&u={language}; _EDGE_S=mkt={region}&ui={language}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    return {'url': url, 'method': 'GET', 'headers': headers}


async def parse_response(response_text: str, page_number: int = 1, **kwargs) -> list[dict]:
    results = []
    dom = html.fromstring(response_text.encode('utf-8'))

    for result in eval_xpath_list(dom, '//ol[@id="b_results"]/li[contains(@class, "b_algo")]'):
        link = eval_xpath_getindex(result, './/h2/a', 0, None)
        if link is None:
            continue
        url = link.attrib.get('href')
        title = extract_text(link)

        content = eval_xpath(result, './/p')
        for p in content:
            for e in p.xpath('.//span[@class="algoSlug_icon"]'):
                e.getparent().remove(e)
        content = extract_text(content)

        if url.startswith('https://www.bing.com/ck/a?'):
            url_query = urlparse(url).query
            parsed_url_query = parse_qs(url_query)
            param_u = parsed_url_query["u"][0]
            encoded_url = param_u[2:]
            encoded_url = encoded_url + '=' * (-len(encoded_url) % 4)
            try:
                url = base64.urlsafe_b64decode(encoded_url).decode()
            except Exception:
                continue

        results.append({'url': url, 'title': title, 'content': content})

    return results


