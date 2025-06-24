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

from . import utils
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

def request(query, params):
    """Assemble a request (`wikipedia rest_v1 summary API`_).
    'params' is expected to be a dictionary that will be modified.
    It can contain 'lang' (str, e.g., "en", "de", defaults to "en")
    for the Wikipedia language domain.
    The `params` dict should also accommodate `headers` if `send_accept_language_header` is true.
    """
    if query.islower():
        query = query.title()

    lang = params.get('lang', 'en')
    wiki_netloc = f"{lang}.wikipedia.org"

    # For LanguageConverter support, the caller should set 'Accept-Language' in params['headers']
    # e.g., params['headers'] = {'Accept-Language': 'zh-CN'} for simplified Chinese.
    # The send_accept_language_header variable suggests this behavior.
    # If send_accept_language_header is True, and 'headers' not in params, initialize it.
    if send_accept_language_header and 'headers' not in params:
        params['headers'] = {} # Ensure headers dict exists
        # Default Accept-Language can be set here if desired, e.g. based on 'lang'
        # For simplicity, we assume the caller handles specific Accept-Language header values.

    title = urllib.parse.quote(query)
    params['url'] = rest_v1_summary_url.format(wiki_netloc=wiki_netloc, title=title)

    # These were specific to searx's network handling, can be removed or handled by the caller
    # params['raise_for_httperror'] = False
    # params['soft_max_redirects'] = 2

    return params


# get response from search-request
def response(resp):

    results = []
    if resp.status_code == 404:
        return []
    if resp.status_code == 400:
        try:
            api_result = resp.json()
        except Exception:  # pylint: disable=broad-except
            pass
        else:
            if (
                api_result['type'] == 'https://mediawiki.org/wiki/HyperSwitch/errors/bad_request'
                and api_result['detail'] == 'title-invalid-characters'
            ):
                return []

    # _network.raise_for_httperror(resp) # Removed, caller should check resp.ok or use requests' raise_for_status()
    if not resp.ok:
        # Basic error handling, can be expanded by the caller
        # For example, raise an exception from .exceptions
        print(f"Wikipedia request failed with status {resp.status_code}: {resp.text}")
        # Or, using a custom exception:
        # from .exceptions import SearxEngineAPIException
        # raise SearxEngineAPIException(f"Wikipedia error {resp.status_code}: {resp.text}")
        return []


    api_result = resp.json()
    title = utils.html_to_text(api_result.get('titles', {}).get('display') or api_result.get('title'))
    wikipedia_link = api_result['content_urls']['desktop']['page']

    if "list" in display_type or api_result.get('type') != 'standard':
        # show item in the result list if 'list' is in the display options or it
        # is a item that can't be displayed in a infobox.
        results.append({'url': wikipedia_link, 'title': title, 'content': api_result.get('description', '')})

    if "infobox" in display_type:
        if api_result.get('type') == 'standard':
            results.append(
                {
                    'infobox': title,
                    'id': wikipedia_link,
                    'content': api_result.get('extract', ''),
                    'img_src': api_result.get('thumbnail', {}).get('source'),
                    'urls': [{'title': 'Wikipedia', 'url': wikipedia_link}],
                }
            )

    return results


# Nonstandard language codes
#
# These Wikipedias use language codes that do not conform to the ISO 639
# standard (which is how wiki subdomains are chosen nowadays).

# lang_map and fetch_traits/fetch_wikimedia_traits removed for simplification.
# The language for Wikipedia (e.g., "en", "de") should be passed as a 'lang'
# parameter to the request function.
