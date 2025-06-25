
from lxml import html, etree
from lxml.etree import XPath
import random

def html_to_text(html_content):
    if html_content is None:
        return ""
    if isinstance(html_content, str):
        return html.fromstring(html_content).text_content().strip()
    return html_content.text_content().strip()

def eval_xpath(dom, xpath_expr):
    return dom.xpath(xpath_expr)

def eval_xpath_list(dom, xpath_expr):
    return dom.xpath(xpath_expr)

def eval_xpath_getindex(dom, xpath_expr, index, default=None):
    result = dom.xpath(xpath_expr)
    if len(result) > index:
        return result[index]
    return default

def extract_text(element):
    if isinstance(element, (list, etree._ElementUnicodeResult)):
        return ' '.join([e.text_content().strip() if hasattr(e, 'text_content') else str(e).strip() for e in element])
    if element is None:
        return ''
    return element.text_content().strip()

def gen_useragent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]
    return random.choice(user_agents)


