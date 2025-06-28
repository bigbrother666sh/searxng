# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Standalone Bing Search Script

This script extracts the Bing search functionality from the SearXNG project
and allows it to be run independently to fetch search results directly from Bing.

It supports basic web searches, pagination, language/region selection, and time-range filtering.
"""

import base64
import re
import time
import json # Not strictly used in this version, but was in original engine
from urllib.parse import parse_qs, urlencode, urlparse
from lxml import html
import requests # For making HTTP requests
# enum is not strictly necessary for this version as it's a simple script.
# from enum import Enum # Was present in initial template, but not used.

# --- Configuration & Globals ---

# Placeholder for EngineTraits functionality, adapted for standalone use.
# In SearXNG, EngineTraits dynamically fetches and manages capabilities like
# supported languages and regions for various engines. Here, it's simplified
# to hold user-specified or default values for language and region.
class EngineTraits:
    """
    A simplified placeholder for SearXNG's EngineTraits class.
    It stores language and region settings for the Bing request.
    """
    def __init__(self):
        self.languages = {}  # Map of locale string to Bing language code
        self.regions = {}    # Map of locale string to Bing market code
        self.all_locale = 'en-us' # Default Bing market/language code

    def get_region(self, locale_str, default_region_code):
        """Gets the Bing market code for a given locale string."""
        # locale_str is expected e.g. "en-US"
        # default_region_code is e.g. "en-us"
        return self.regions.get(locale_str, default_region_code)

    def get_language(self, locale_str, default_language_code):
        """Gets the Bing language code for a given locale string."""
        # locale_str is expected e.g. "en-US"
        # default_language_code is e.g. "en" (though Bing uses "en-us")
        return self.languages.get(locale_str, default_language_code)

traits = EngineTraits() # Global instance

# Simplified logger. For more advanced logging, Python's `logging` module could be used.
class Logger:
    """A basic logger class for debug, warning, and error messages."""
    def debug(self, msg, *args):
        """Prints a debug message if uncommented."""
        # print(f"DEBUG: {msg}" % args) # Uncomment for verbose debug output
        pass

    def warning(self, msg, *args):
        """Prints a warning message."""
        print(f"WARNING: {msg}" % args)

    def error(self, msg, *args):
        """Prints an error message."""
        print(f"ERROR: {msg}" % args)

logger = Logger()


# --- Utility Functions (adapted from searx.utils) ---

def eval_xpath(element, xpath_query):
    """
    Evaluates an XPath query on an lxml element.
    Returns a list of matching elements or an empty list on error or if element is None.
    """
    if element is None:
        # logger.warning(f"eval_xpath called with None element for query: {xpath_query}")
        return []
    try:
        return element.xpath(xpath_query)
    except Exception as e: # Catching generic Exception as lxml can raise various errors
        logger.error(f"XPath evaluation error: {e} for query: '{xpath_query}' on element: {type(element)}")
        return []

def extract_text(element_or_list):
    """
    Extracts and concatenates text content from an lxml element or a list of elements.
    Handles elements, strings, and lxml text results.
    Returns a single string.
    """
    if element_or_list is None:
        return ""

    elements = element_or_list if isinstance(element_or_list, list) else [element_or_list]

    text_parts = []
    for item in elements:
        if hasattr(item, 'text_content'): # Standard lxml elements
            text_parts.append(item.text_content())
        elif isinstance(item, str): # Plain strings
            text_parts.append(item)
        elif hasattr(item, 'is_text') and item.is_text: # lxml.etree._ElementUnicodeResult
             text_parts.append(str(item))

    return " ".join(text_parts).strip()

def eval_xpath_list(element, xpath_query):
    """
    Alias for eval_xpath. In the context of lxml, xpath() typically returns a list.
    This function ensures a list is returned, even if XPath theoretically could return a single value.
    """
    result = eval_xpath(element, xpath_query)
    return result if isinstance(result, list) else [result] if result is not None else []


def eval_xpath_getindex(element, xpath_query, index=0, default=None):
    """
    Evaluates an XPath query and returns the element at a specific index from the result list.
    Returns a default value if the index is out of bounds or no elements are found.
    """
    results = eval_xpath(element, xpath_query) # eval_xpath already returns a list
    if results and isinstance(results, list) and len(results) > index:
        return results[index]
    return default

# --- Custom Exception ---
class SearxEngineAPIException(Exception):
    """Custom exception for engine-related API errors (not strictly used for raising in this script)."""
    pass

# --- Bing Search Engine Logic (adapted from searx/engines/bing.py) ---

# Engine specific constants and configurations, largely from original SearXNG engine file.
categories = ['general', 'web']  # Supported search categories by this script's focus
paging = True  # Indicates if the engine supports pagination
max_page = 200  # Theoretical maximum number of pages Bing might provide
"""Original SearXNG comment: 200 pages maximum (``&first=1991``)"""

time_range_support = True  # Indicates if filtering by time range is supported by Bing
safesearch = True  # Bing results are generally SafeSearch filtered by default from SearXNG's perspective
"""Original SearXNG comment: Bing results are always SFW. To get NSFW links from bing some age
verification by a cookie is needed / thats not possible in SearXNG.
"""

base_url = 'https://www.bing.com/search'  # Base URL for Bing web search
"""Original SearXNG comment: Bing (Web) search URL"""


def _page_offset(pageno):
    """
    Calculates the 'first' parameter value for Bing's pagination.
    Bing uses a 1-based index for the first result to display on a page.
    Each page typically shows 10 results by default in this parsing logic.
    - Page 1: first=1
    - Page 2: first=11
    - Page 3: first=21
    """
    return (int(pageno) - 1) * 10 + 1


def set_bing_cookies(params, engine_language_code, engine_market_code):
    """
    Sets the necessary cookies for Bing to respect language and region (market) settings.
    These cookies influence the language of the UI and the regional relevance of results.

    Args:
        params (dict): The request parameters dictionary, modified in-place.
        engine_language_code (str): The language-region code (e.g., 'en-us') for UI.
        engine_market_code (str): The market code (e.g., 'en-us') for regional results.
    """
    if 'cookies' not in params:
        params['cookies'] = {}
    # _EDGE_CD: Sets market (m) and UI language (u)
    params['cookies']['_EDGE_CD'] = f'm={engine_market_code}&u={engine_language_code}'
    # _EDGE_S: Also sets market (mkt) and UI language (ui) - often set by Bing, included for completeness
    params['cookies']['_EDGE_S'] = f'mkt={engine_market_code}&ui={engine_language_code}'
    logger.debug("Bing cookies set: %s", params['cookies'])


def request(query, params):
    """
    Assembles the parameters (URL, headers, cookies) for a Bing Web search request.

    Args:
        query (str): The search query.
        params (dict): A dictionary containing operational parameters like 'pageno',
                       'searxng_locale' (e.g., 'en-US'), and optionally 'time_range'.
                       This dictionary is modified in-place to include the full request details.

    Returns:
        dict: The modified params dictionary with 'url', 'headers', and 'cookies'.
    """
    # Determine Bing's market and language codes using the simplified EngineTraits.
    # 'searxng_locale' (e.g., 'en-US') is used as a key to get specific Bing codes (e.g., 'en-us').
    # traits.all_locale provides a default if the specific locale isn't mapped in our simple traits.
    bing_market_code = traits.get_region(params.get('searxng_locale', 'en-US'), traits.all_locale)
    # Bing often uses the market code (e.g., 'en-us') for language as well in cookies.
    bing_language_code = traits.get_language(params.get('searxng_locale', 'en-US'), bing_market_code)
    set_bing_cookies(params, bing_language_code, bing_market_code)

    page = params.get('pageno', 1)
    query_params = {
        'q': query,  # The search query
        'pq': query, # Previous query term, aids pagination consistency according to original comments
    }

    # Pagination parameters: 'first' (result offset) and 'FORM' (page state marker)
    if page > 1:
        query_params['first'] = _page_offset(page)
    if page == 2:
        query_params['FORM'] = 'PERE'  # Specific value for page 2
    elif page > 2:
        query_params['FORM'] = 'PERE%s' % (page - 2) # PERE1 for page 3, PERE2 for page 4, etc.

    params['url'] = f'{base_url}?{urlencode(query_params)}' # Construct the full URL

    # Time range filtering: appends a filter to the URL if 'time_range' is specified.
    if params.get('time_range'):
        unix_day = int(time.time() / 86400) # Number of days since Unix epoch
        # Mapping from user-friendly time range names to Bing's specific filter codes
        time_ranges_map = {
            'day': '1',  # Last 24 hours
            'week': '2', # Past week
            'month': '3',# Past month
            'year': f'5_{unix_day-365}_{unix_day}' # Past year (approximated using current date)
        }
        time_range_filter_value = time_ranges_map.get(params['time_range'])
        if time_range_filter_value:
            params['url'] += f'&filters=ex1:"ez{time_range_filter_value}"'
        else:
            logger.warning(f"Unsupported time_range specified: {params['time_range']}")

    # Set default HTTP headers if they are not already provided in the input params.
    if 'headers' not in params:
        params['headers'] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5", # Prioritize US English for requests
            "Accept-Encoding": "gzip, deflate, br", # Declare support for common compressions
            "DNT": "1", # Do Not Track header
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1", # Signal preference for HTTPS
            "Sec-GPC": "1", # Global Privacy Control header
            "Cache-Control": "max-age=0", # Request fresh version, avoid intermediary caches
        }
    return params


def response(resp_text, requested_pageno):
    """
    Parses the HTML response from Bing to extract search results and total count.

    Args:
        resp_text (str): The HTML content of the Bing search results page.
        requested_pageno (int): The page number that was originally requested.
                                Used to verify if Bing returned the correct page.

    Returns:
        list: A list of dictionaries, where each dictionary represents a search result
              (with 'url', 'title', 'content'). The last item in this list is a special
              dictionary containing 'number_of_results' (the total estimated results).
              Returns an empty list if Bing seems to have returned an unexpected page
              (e.g., due to rate limiting or requesting a page beyond available results),
              or if no results are found on the page.
    """
    # pylint: disable=too-many-locals # Standard for parsing functions with many temp vars

    results = []
    total_results_count = 0

    dom = html.fromstring(resp_text) # Parse HTML text into an lxml DOM tree

    # XPath to find main result items: list items (<li>) with class 'b_algo'
    # inside an ordered list (<ol>) with id 'b_results'.
    result_elements = eval_xpath_list(dom, '//ol[@id="b_results"]/li[contains(@class, "b_algo")]')
    logger.debug(f"Found {len(result_elements)} potential result items using primary XPath.")

    for result_item_element in result_elements:
        # Extract title and URL. These are typically within an <h2> containing an <a> tag.
        link_element = eval_xpath_getindex(result_item_element, './/h2/a', 0, None)
        if link_element is None:
            logger.debug("Skipping a result item: main link element (h2/a) not found.")
            continue

        url = link_element.attrib.get('href')
        title = extract_text(link_element)

        # Extract the descriptive snippet, usually found in <p> elements.
        content_paragraph_elements = eval_xpath(result_item_element, './/p')
        # Clean up snippets by removing any embedded "Web" badges or similar icons.
        for p_elem in content_paragraph_elements:
            for icon_element in p_elem.xpath('.//span[@class="algoSlug_icon"]'): # Common class for such icons
                if icon_element.getparent() is not None:
                    icon_element.getparent().remove(icon_element)
        content = extract_text(content_paragraph_elements)

        # Decode Bing's tracking/redirect URLs if present.
        # These URLs start with 'https://www.bing.com/ck/a?' and contain a base64 encoded target URL
        # in the 'u' parameter (after the initial 'a1').
        if url and url.startswith('https://www.bing.com/ck/a?'):
            url_query_string = urlparse(url).query
            parsed_url_params = parse_qs(url_query_string)
            param_u_values = parsed_url_params.get("u") # 'u' parameter list
            if param_u_values:
                encoded_url_with_prefix = param_u_values[0]
                actual_encoded_url = encoded_url_with_prefix[2:] # Skip 'a1' prefix
                # Ensure correct padding for base64 decoding
                actual_encoded_url_padded = actual_encoded_url + '=' * (-len(actual_encoded_url) % 4)
                try:
                    url = base64.urlsafe_b64decode(actual_encoded_url_padded).decode()
                except Exception as e:
                    logger.error(f"Error decoding Bing redirect URL: {e}. Original URL: {url}")
                    # If decoding fails, retain the original redirect URL as a fallback.
            else:
                logger.warning(f"Could not parse 'u' parameter from Bing redirect URL: {url}")

        results.append({'url': url, 'title': title, 'content': content})

    # Attempt to parse the total number of results and check for pagination consistency.
    if result_elements: # Only proceed if some individual result items were found on the page
        # Total results count is usually in a <span> with class 'sb_count'.
        # Example: <span class="sb_count">About 1,230,000 results</span>
        # Or: <span class="sb_count">1-10 of 1,230,000 results</span>
        result_count_span_texts = eval_xpath(dom, '//span[@class="sb_count"]//text()')
        result_count_container_str = "".join(result_count_span_texts).strip()
        logger.debug(f"Raw result count container string from page: '{result_count_container_str}'")

        # Determine the start index of results as displayed on the page (e.g., "1" from "1-10 of ...")
        current_page_start_index = 1 # Default assumption

        # Bing's count string format can vary.
        if "-" in result_count_container_str: # Format like "1-10 of 100 results"
            # Try to extract the first number (start index on page)
            # Regex splits "1-10 of ..." into ["1", " of ..."] using "-\d+" as delimiter
            parts = re.split(r'-\d+', result_count_container_str, maxsplit=1)
            first_part_numeric = re.sub(r'[^0-9]', '', parts[0]) # Extract numbers from first part
            if first_part_numeric.isdigit():
                 current_page_start_index = int(first_part_numeric)
            # Extract the total count (the number after "of " or the last numeric part)
            potential_total_count_str = result_count_container_str.split('of')[-1] if 'of' in result_count_container_str else parts[-1]
            numeric_part_of_total_count = re.sub(r'[^0-9]', '', potential_total_count_str)
        else: # Format like "About 1,234,567 results" or just "1,234,567 results"
            numeric_part_of_total_count = re.sub(r'[^0-9]', '', result_count_container_str)

        if len(numeric_part_of_total_count) > 0:
            try:
                total_results_count = int(numeric_part_of_total_count)
            except ValueError:
                logger.warning(
                    f"Could not parse total_results_count from: '{numeric_part_of_total_count}' "
                    f"(derived from raw string: '{result_count_container_str}')"
                )
                # total_results_count remains 0 if parsing fails

        # Verify if Bing returned the expected page of results.
        expected_page_start_offset = _page_offset(requested_pageno)

        # If the start index reported on the page doesn't match what we expected for this pageno,
        # it might indicate an issue (e.g., Bing returning page 1 for an out-of-bounds request, or rate limiting).
        # A simple check: if we requested page > 1, but Bing shows results starting from 1 (or a number not matching expected offset), it's a mismatch.
        if requested_pageno > 1 and current_page_start_index != expected_page_start_offset :
            # This can happen if requested page is beyond available results, Bing might return page 1.
            if expected_page_start_offset > total_results_count and total_results_count > 0 and current_page_start_index == 1:
                logger.warning(
                    f"Bing returned page 1 instead of requested page {requested_pageno}. "
                    f"Expected start offset: {expected_page_start_offset}, but page shows start at {current_page_start_index}. "
                    f"This might be because the requested page is beyond the total available results ({total_results_count})."
                )
                return [] # Return empty list: no valid results for the *requested* page.

            # Log other mismatches as warnings. For a standalone script, we might still want the results.
            logger.warning(
                f"Page number mismatch detected: Requested page {requested_pageno} (expected offset {expected_page_start_offset}), "
                f"but the content seems to be from a page starting at offset {current_page_start_index}."
            )

    results.append({'number_of_results': total_results_count}) # Append total count as the last item
    return results

# --- Main Execution & CLI ---

def perform_search(query, pageno=1, language='en', region='US', time_range=None):
    """
    Orchestrates the Bing search: prepares parameters, makes the HTTP request,
    and parses the response.

    Args:
        query (str): The search query.
        pageno (int, optional): Page number to retrieve. Defaults to 1.
        language (str, optional): Two-letter language code (e.g., 'en'). Defaults to 'en'.
        region (str, optional): Two-letter region code (e.g., 'US'). Defaults to 'US'.
        time_range (str, optional): Time range filter ('day', 'week', 'month', 'year').
                                    Defaults to None (no time filter).

    Returns:
        list or None: A list of search result dictionaries if successful,
                      None if the HTTP request fails.
    """
    # Prepare the parameter dictionary for the 'request' function
    req_params = {
        'pageno': pageno,
        # Construct 'searxng_locale' (e.g., 'en-US') which our simplified EngineTraits uses
        # as a key to determine Bing-specific market/language codes.
        'searxng_locale': f"{language.lower()}-{region.upper()}"
    }
    if time_range:
        req_params['time_range'] = time_range

    # Configure the global 'traits' instance for this specific request.
    # Bing typically uses lowercase market codes like 'en-us'.
    global traits #pylint: disable=global-statement
    bing_market_lang_code = f"{language.lower()}-{region.lower()}"
    # The key for traits.languages/regions is the 'searxng_locale' format
    locale_key = f"{language.lower()}-{region.upper()}"
    traits.languages = {locale_key: bing_market_lang_code}
    traits.regions = {locale_key: bing_market_lang_code}
    traits.all_locale = bing_market_lang_code # Set the default/fallback for EngineTraits methods

    # Get the full request details (URL, headers, cookies)
    search_request_details = request(query, req_params)

    # Make the HTTP GET request
    try:
        http_response = requests.get(
            search_request_details['url'],
            headers=search_request_details['headers'],
            cookies=search_request_details.get('cookies'), # Use cookies if set by request()
            timeout=10  # Set a timeout for the request (seconds)
        )
        http_response.raise_for_status()  # Raise an HTTPError for bad responses (4XX or 5XX)
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request failed: {e}")
        return None # Indicate failure

    # Parse the HTML response text
    # Pass the originally requested pageno for consistency checks within the 'response' function.
    parsed_results = response(http_response.text, search_request_details.get('pageno', 1))
    return parsed_results


if __name__ == '__main__':
    import argparse

    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Standalone Bing Search Script. Fetches search results directly from Bing.",
        formatter_class=argparse.RawTextHelpFormatter, # Allows for more control over help text formatting
        epilog="""\
Examples:
  python bing_search.py "latest AI research"
  python bing_search.py "python web frameworks" -p 2
  python bing_search.py "오늘의 날씨" -l ko -r KR
  python bing_search.py "tech news" -t week
"""
    )
    parser.add_argument("query", help="The search query text.")
    parser.add_argument(
        "-p", "--page", type=int, default=1,
        help="Page number to retrieve (default: 1)."
    )
    parser.add_argument(
        "-l", "--lang", type=str, default="en",
        help="Two-letter language code for the search (e.g., 'en', 'de', default: 'en')."
    )
    parser.add_argument(
        "-r", "--region", type=str, default="US",
        help="Two-letter region code for the search (e.g., 'US', 'GB', 'DE', default: 'US')."
    )
    parser.add_argument(
        "-t", "--timerange", type=str, choices=['day', 'week', 'month', 'year'],
        help="Time range for the search results (day, week, month, year)."
    )

    args = parser.parse_args() # Parse the command-line arguments

    # Log the search parameters being used (if debug is enabled in Logger)
    logger.debug(
        f"Initiating search for: '{args.query}', Page: {args.page}, "
        f"Lang: {args.lang}, Region: {args.region}, TimeRange: {args.timerange}"
    )

    # Prepare parameters for the perform_search function
    search_execution_params = {
        'pageno': args.page,
        'language': args.lang,
        'region': args.region
    }
    if args.timerange: # Add time_range only if specified
        search_execution_params['time_range'] = args.timerange

    # Execute the search
    search_results = perform_search(args.query, **search_execution_params)

    # Print the results to the console
    if search_results:
        print(f"\nResults for '{args.query}' (Page {args.page}, TimeRange: {args.timerange or 'Any'}):")
        actual_result_item_count = 0
        for item in search_results:
            if 'number_of_results' in item: # This is the summary item with total count
                # Check if it's the only item and count is 0, meaning no actual results found on page
                if len(search_results) == 1 and item['number_of_results'] == 0 and actual_result_item_count == 0:
                    print("No results found for this query or page.")
                    # Avoid printing "Total estimated results: 0" if no other items were processed
                    continue
                print(f"\nTotal estimated results: {item['number_of_results']}")
            else: # These are the actual search result items
                actual_result_item_count += 1
                print(f"\n{actual_result_item_count}. Title: {item.get('title', 'N/A')}")
                print(f"   URL: {item.get('url', 'N/A')}")
                print(f"   Content: {item.get('content', 'N/A')}")

        # If loop finishes and no actual items were printed (e.g. results was just [{'number_of_results': 0}])
        if actual_result_item_count == 0 and not any('url' in item for item in search_results):
             print("No individual results found on this page.")
    else:
        # This case handles if perform_search returned None (e.g. HTTP error)
        # or if it returned an empty list (e.g. page mismatch returning [])
        print("Failed to retrieve search results or no results found.")
