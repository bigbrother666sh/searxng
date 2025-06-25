
import urllib.parse
import json

from core.utils import html_to_text

rest_v1_summary_url = 'https://{wiki_netloc}/api/rest_v1/page/summary/{title}'

async def request(query: str, language: str = 'en', **kwargs) -> dict:
    if query.islower():
        query = query.title()

    # Simplified wiki_netloc mapping for common languages
    wiki_netloc_map = {
        'en': 'en.wikipedia.org',
        'zh': 'zh.wikipedia.org',
        'zh-CN': 'zh.wikipedia.org',
        'zh-TW': 'zh.wikipedia.org',
        'zh-HK': 'zh.wikipedia.org',
        'de': 'de.wikipedia.org',
        'fr': 'fr.wikipedia.org',
        'es': 'es.wikipedia.org',
        'ja': 'ja.wikipedia.org',
        'ru': 'ru.wikipedia.org',
    }
    wiki_netloc = wiki_netloc_map.get(language, 'en.wikipedia.org')

    title = urllib.parse.quote(query)
    url = rest_v1_summary_url.format(wiki_netloc=wiki_netloc, title=title)

    headers = {
        'Accept-Language': language # This header is important for LanguageConverter
    }

    return {'url': url, 'method': 'GET', 'headers': headers}


async def parse_response(response_text: str, **kwargs) -> list[dict]:
    results = []
    try:
        api_result = json.loads(response_text)
    except json.JSONDecodeError:
        return []

    if api_result.get('type') == 'https://mediawiki.org/wiki/HyperSwitch/errors/bad_request' and \
       api_result.get('detail') == 'title-invalid-characters':
        return []

    title = html_to_text(api_result.get('titles', {}).get('display') or api_result.get('title'))
    wikipedia_link = api_result.get('content_urls', {}).get('desktop', {}).get('page')

    if not wikipedia_link or not title:
        return []

    # Always return as a list item for simplicity, infobox handling is external
    results.append({
        'url': wikipedia_link,
        'title': title,
        'content': api_result.get('extract', ''),
        'thumbnail': api_result.get('thumbnail', {}).get('source'),
    })

    return results


