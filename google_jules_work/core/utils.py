#!/usr/bin/env python3

from lxml import html, etree
from lxml.etree import XPath
import random

def html_to_text(html_content):
    """将 HTML 内容转换为纯文本"""
    if html_content is None:
        return ""
    if isinstance(html_content, str):
        return html.fromstring(html_content).text_content().strip()
    return html_content.text_content().strip()

def eval_xpath(dom, xpath_expr):
    """执行 XPath 表达式"""
    return dom.xpath(xpath_expr)

def eval_xpath_list(dom, xpath_expr):
    """执行 XPath 表达式并返回列表"""
    return dom.xpath(xpath_expr)

def eval_xpath_getindex(dom, xpath_expr, index, default=None):
    """执行 XPath 表达式并获取指定索引的元素"""
    result = dom.xpath(xpath_expr)
    if len(result) > index:
        return result[index]
    return default

def extract_text(element):
    """从元素中提取文本内容"""
    if isinstance(element, (list, etree._ElementUnicodeResult)):
        return ' '.join([e.text_content().strip() if hasattr(e, 'text_content') else str(e).strip() for e in element])
    if element is None:
        return ''
    return element.text_content().strip()

def gen_useragent():
    """生成随机用户代理字符串"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]
    return random.choice(user_agents) 