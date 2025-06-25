# SPDX-License-Identifier: AGPL-3.0-or-later
"""This module implements the Wikipedia engine.  Some of this implementations
are shared by other engines:

- :ref:`wikidata engine`

The list of supported languages is :py:obj:`fetched <fetch_wikimedia_traits>` from
the article linked by :py:obj:`list_of_wikipedias`.

Unlike traditional search engines, wikipedia does not support one Wikipedia for
all languages, but there is one Wikipedia for each supported language. Some of
these Wikipedias have a LanguageConverter_ enabled
(:py:obj:`rest_v1_summary_url`).

A LanguageConverter_ (LC) is a system based on language variants that
automatically converts the content of a page into a different variant. A variant
is mostly the same language in a different script.

- `Wikipedias in multiple writing systems`_
- `Automatic conversion between traditional and simplified Chinese characters`_

PR-2554_:
  The Wikipedia link returned by the API is still the same in all cases
  (`https://zh.wikipedia.org/wiki/出租車`_) but if your browser's
  ``Accept-Language`` is set to any of ``zh``, ``zh-CN``, ``zh-TW``, ``zh-HK``
  or .. Wikipedia's LC automatically returns the desired script in their
  web-page.

  - You can test the API here: https://reqbin.com/gesg2kvx

.. _https://zh.wikipedia.org/wiki/出租車:
   https://zh.wikipedia.org/wiki/%E5%87%BA%E7%A7%9F%E8%BB%8A

To support Wikipedia's LanguageConverter_, a SearXNG request to Wikipedia uses
:py:obj:`get_wiki_params` and :py:obj:`wiki_lc_locale_variants' in the
:py:obj:`fetch_wikimedia_traits` function.

To test in SearXNG, query for ``!wp 出租車`` with each of the available Chinese
options:

- ``!wp 出租車 :zh``    should show 出租車
- ``!wp 出租車 :zh-CN`` should show 出租车
- ``!wp 出租車 :zh-TW`` should show 計程車
- ``!wp 出租車 :zh-HK`` should show 的士
- ``!wp 出租車 :zh-SG`` should show 德士

.. _LanguageConverter:
   https://www.mediawiki.org/wiki/Writing_systems#LanguageConverter
.. _Wikipedias in multiple writing systems:
   https://meta.wikimedia.org/wiki/Wikipedias_in_multiple_writing_systems
.. _Automatic conversion between traditional and simplified Chinese characters:
   https://en.wikipedia.org/wiki/Chinese_Wikipedia#Automatic_conversion_between_traditional_and_simplified_Chinese_characters
.. _PR-2554: https://github.com/searx/searx/pull/2554

"""

import urllib.parse
import babel

from lxml import html
import requests # For making HTTP requests

import utils
# from searx import network as _network # Removed
# from searx import locales # Removed
# from searx.enginelib.traits import EngineTraits # Removed

# traits: EngineTraits # Removed

# about
about = {
    "website": 'https://www.wikipedia.org/',
    "wikidata_id": 'Q52',
    "official_api_documentation": 'https://en.wikipedia.org/api/',
    "use_official_api": True,
    "require_api_key": False,
    "results": 'JSON',
}

display_type = ["infobox"]
"""A list of display types composed from ``infobox`` and ``list``.  The latter
one will add a hit to the result list.  The first one will show a hit in the
info box.  Both values can be set, or one of the two can be set."""

send_accept_language_header = True
"""The HTTP ``Accept-Language`` header is needed for wikis where
LanguageConverter_ is enabled."""

list_of_wikipedias = 'https://meta.wikimedia.org/wiki/List_of_Wikipedias'
"""`List of all wikipedias <https://meta.wikimedia.org/wiki/List_of_Wikipedias>`_
"""

wikipedia_article_depth = 'https://meta.wikimedia.org/wiki/Wikipedia_article_depth'
"""The *editing depth* of Wikipedia is one of several possible rough indicators
of the encyclopedia's collaborative quality, showing how frequently its articles
are updated.  The measurement of depth was introduced after some limitations of
the classic measurement of article count were realized.
"""

rest_v1_summary_url = 'https://{wiki_netloc}/api/rest_v1/page/summary/{title}'
"""
`wikipedia rest_v1 summary API`_:
  The summary response includes an extract of the first paragraph of the page in
  plain text and HTML as well as the type of page. This is useful for page
  previews (fka. Hovercards, aka. Popups) on the web and link previews in the
  apps.

HTTP ``Accept-Language`` header (:py:obj:`send_accept_language_header`):
  The desired language variant code for wikis where LanguageConverter_ is
  enabled.

.. _wikipedia rest_v1 summary API:
   https://en.wikipedia.org/api/rest_v1/#/Page%20content/get_page_summary__title_

"""

wiki_lc_locale_variants = {
    "zh": (
        "zh-CN",
        "zh-HK",
        "zh-MO",
        "zh-MY",
        "zh-SG",
        "zh-TW",
    ),
    "zh-classical": ("zh-classical",),
}
"""Mapping rule of the LanguageConverter_ to map a language and its variants to
a Locale (used in the HTTP ``Accept-Language`` header). For example see `LC
Chinese`_.

.. _LC Chinese:
   https://meta.wikimedia.org/wiki/Wikipedias_in_multiple_writing_systems#Chinese
"""

wikipedia_script_variants = {
    "zh": (
        "zh_Hant",
        "zh_Hans",
    )
}

# Simplified: Removed get_wiki_params, traits, and complex locale logic.
# The request function will now take an optional 'lang' parameter (e.g., "en", "de").
# Defaulting to "en.wikipedia.org".
# The send_accept_language_header is kept, assuming the caller might want to set it.

async def request(query: str, page_number: int = 1, **kwargs) -> dict:
    """构建 Wikipedia 搜索请求"""
    if query.islower():
        query = query.title()

    lang = kwargs.get('language', 'en')
    wiki_netloc = f"{lang}.wikipedia.org"

    title = urllib.parse.quote(query)
    url = rest_v1_summary_url.format(wiki_netloc=wiki_netloc, title=title)
    
    headers = {}
    if send_accept_language_header:
        headers['Accept-Language'] = f'{lang}'

    return {
        'url': url,
        'method': 'GET',
        'headers': headers if headers else None
    }


async def parse_response(response_text: str, **kwargs) -> list[dict]:
    """解析 Wikipedia 搜索响应"""
    import json
    
    results = []
    
    try:
        api_result = json.loads(response_text)
    except json.JSONDecodeError:
        return []

    # Check for error responses
    if 'type' in api_result and api_result['type'] == 'https://mediawiki.org/wiki/HyperSwitch/errors/not_found':
        return []

    # Extract basic information
    title = utils.html_to_text(api_result.get('titles', {}).get('display') or api_result.get('title', ''))
    wikipedia_link = api_result.get('content_urls', {}).get('desktop', {}).get('page', '')
    
    # Get description/content
    description = api_result.get('description', '')
    extract = api_result.get('extract', '')
    content = extract if extract else description
    
    # Get thumbnail if available
    thumbnail = None
    if 'thumbnail' in api_result:
        thumbnail = api_result['thumbnail'].get('source', '')
        # Convert http to https for thumbnails
        if thumbnail and thumbnail.startswith('http:'):
            thumbnail = thumbnail.replace('http:', 'https:')

    # Check if we should display this result
    if "list" in display_type or api_result.get('type') != 'standard':
        # show item in the result list if 'list' is in the display options or it
        # is a item that can't be displayed in a infobox.
        result = {
            'url': wikipedia_link, 
            'title': title, 
            'content': content
        }
        
        # Add thumbnail if available
        if thumbnail:
            result['thumbnail'] = thumbnail
            
        # Add additional metadata if available
        if 'coordinates' in api_result:
            coords = api_result['coordinates']
            result['coordinates'] = f"{coords.get('lat', '')}, {coords.get('lon', '')}"
        
        results.append(result)

    # Also add infobox result if requested
    if "infobox" in display_type and api_result.get('type') == 'standard':
        infobox_result = {
            'infobox': title,
            'id': wikipedia_link,
            'content': content,
            'urls': [{'title': 'Wikipedia', 'url': wikipedia_link}]
        }
        
        if thumbnail:
            infobox_result['img_src'] = thumbnail
            
        results.append(infobox_result)

    return results


# Nonstandard language codes
#
# These Wikipedias use language codes that do not conform to the ISO 639
# standard (which is how wiki subdomains are chosen nowadays).

# lang_map and fetch_traits/fetch_wikimedia_traits removed for simplification.
# The language for Wikipedia (e.g., "en", "de") should be passed as a 'lang'
# parameter to the request function.
