# Utility functions for simplified engines
from __future__ import annotations

import re
import json
from typing import Optional, Union, Any, Set, List, Dict, MutableMapping, Tuple, Callable
from numbers import Number
from random import choice
from html.parser import HTMLParser
from html import escape

from lxml import html
from lxml.etree import ElementBase, XPath, XPathError, XPathSyntaxError

from exceptions import SearxXPathSyntaxException, SearxEngineXPathException

# USER_AGENTS data, copied from searx/data/useragents.json
USER_AGENTS: dict[str, Any] = {
    "os": [
        "Windows NT 10.0; Win64; x64",
        "X11; Linux x86_64"
    ],
    "ua": "Mozilla/5.0 ({os}; rv:{version}) Gecko/20100101 Firefox/{version}",
    "versions": [
        "139.0",
        "138.0"
    ]
}

# XPath-related utilities (copied and adapted from searx/utils.py)
XPathSpecType = Union[str, XPath]
_XPATH_CACHE: Dict[str, XPath] = {}

class _NotSetClass:  # pylint: disable=too-few-public-methods
    pass
_NOTSET = _NotSetClass()

def get_xpath(xpath_spec: XPathSpecType) -> XPath:
    if isinstance(xpath_spec, str):
        result = _XPATH_CACHE.get(xpath_spec, None)
        if result is None:
            try:
                result = XPath(xpath_spec)
            except XPathSyntaxError as e:
                # Use local exception once defined
                raise SearxXPathSyntaxException(f"Syntax error in XPath: '{xpath_spec}'. Original error: {e.msg}") from e
            _XPATH_CACHE[xpath_spec] = result
        return result
    if isinstance(xpath_spec, XPath):
        return xpath_spec
    raise TypeError('xpath_spec must be either a str or a lxml.etree.XPath')

def eval_xpath(element: ElementBase, xpath_spec: XPathSpecType):
    xpath = get_xpath(xpath_spec)
    try:
        return xpath(element)
    except XPathError as e:
        arg = ' '.join([str(i) for i in e.args])
        # Use local exception once defined
        raise SearxEngineXPathException(f"Error evaluating XPath: '{xpath_spec}'. Original error: {arg}") from e

def eval_xpath_list(element: ElementBase, xpath_spec: XPathSpecType, min_len: Optional[int] = None):
    result = eval_xpath(element, xpath_spec)
    if not isinstance(result, list):
        # Use local exception once defined
        raise SearxEngineXPathException(xpath_spec, 'the result is not a list')
    if min_len is not None and min_len > len(result):
        # Use local exception once defined
        raise SearxEngineXPathException(xpath_spec, 'len(xpath_str) < ' + str(min_len))
    return result

def eval_xpath_getindex(elements: ElementBase, xpath_spec: XPathSpecType, index: int, default=_NOTSET):
    result = eval_xpath_list(elements, xpath_spec)
    if -len(result) <= index < len(result):
        return result[index]
    if default == _NOTSET:
        # Use local exception once defined
        raise SearxEngineXPathException(xpath_spec, 'index ' + str(index) + ' not found')
    return default

# HTML processing utilities (copied and adapted from searx/utils.py)
_BLOCKED_TAGS = ('script', 'style')

class _HTMLTextExtractorException(Exception):
    pass

class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == 'br':
            self.result.append(' ')

    def handle_endtag(self, tag):
        if not self.tags:
            return
        if tag != self.tags[-1]:
            raise _HTMLTextExtractorException()
        self.tags.pop()

    def is_valid_tag(self):
        return not self.tags or self.tags[-1] not in _BLOCKED_TAGS

    def handle_data(self, data):
        if not self.is_valid_tag():
            return
        self.result.append(data)

    def handle_charref(self, name):
        if not self.is_valid_tag():
            return
        if name[0] in ('x', 'X'):
            codepoint = int(name[1:], 16)
        else:
            codepoint = int(name)
        self.result.append(chr(codepoint))

    def handle_entityref(self, name):
        if not self.is_valid_tag():
            return
        self.result.append(name) # Simplified from original, might need html.entities.name2codepoint

    def get_text(self):
        return ''.join(self.result).strip()

    def error(self, message):
        raise AssertionError(message)

def html_to_text(html_str: str) -> str:
    if not html_str:
        return ""
    html_str = html_str.replace('\n', ' ').replace('\r', ' ')
    html_str = ' '.join(html_str.split())
    s = _HTMLTextExtractor()
    try:
        s.feed(html_str)
    except AssertionError: # Error during parsing
        s = _HTMLTextExtractor()
        s.feed(escape(html_str, quote=True)) # Try with escaped string
    except _HTMLTextExtractorException: # Custom internal error
        # Potentially log this in a real scenario
        pass # Keep it simple for now
    return s.get_text()

def extract_text(xpath_results, allow_none: bool = False) -> Optional[str]:
    if isinstance(xpath_results, list):
        result = ''
        for e in xpath_results:
            result = result + (extract_text(e) or '')
        return result.strip()
    if isinstance(xpath_results, ElementBase):
        text: str = html.tostring(xpath_results, encoding='unicode', method='text', with_tail=False)
        text = text.strip().replace('\n', ' ')
        return ' '.join(text.split())
    if isinstance(xpath_results, (str, Number, bool)):
        return str(xpath_results)
    if xpath_results is None and allow_none:
        return None
    if xpath_results is None and not allow_none:
        raise ValueError('extract_text(None, allow_none=False)')
    raise ValueError(f'unsupported type: {type(xpath_results)}')

# User agent generation (copied and adapted from searx/utils.py)
def gen_useragent(os_string: Optional[str] = None) -> str:
    """Return a random browser User Agent"""
    return USER_AGENTS['ua'].format(os=os_string or choice(USER_AGENTS['os']), version=choice(USER_AGENTS['versions']))

# Placeholder for network related utilities if needed later
# For now, engines will use 'requests' library directly or similar.

# Placeholder for locale related utilities if needed later
# For now, complex locale logic will be simplified or removed from engines.

# Placeholder for EngineTraits if simple dicts are not enough
# For now, traits will be simplified or inlined if possible.

pass
