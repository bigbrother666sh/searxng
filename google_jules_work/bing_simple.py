# 简化版 Bing 搜索引擎
from urllib.parse import urlencode

async def request(query: str, page_number: int = 1, **kwargs) -> dict:
    """构建 Bing 搜索请求"""
    params = {
        'q': query,
        'first': (page_number - 1) * 10 + 1,
        'count': 10
    }
    
    url = f"https://www.bing.com/search?{urlencode(params)}"
    
    return {
        'url': url,
        'method': 'GET',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }

async def parse_response(response_text: str, **kwargs) -> list[dict]:
    """解析 Bing 搜索响应"""
    from lxml import html
    
    results = []
    doc = html.fromstring(response_text)
    
    # 简化的解析逻辑
    for result in doc.xpath('//li[@class="b_algo"]'):
        title_elem = result.xpath('.//h2/a')[0] if result.xpath('.//h2/a') else None
        if title_elem is not None:
            title = title_elem.text_content().strip()
            url = title_elem.get('href', '')
            
            content_elem = result.xpath('.//p')[0] if result.xpath('.//p') else None
            content = content_elem.text_content().strip() if content_elem is not None else ''
            
            results.append({
                'title': title,
                'url': url,
                'content': content
            })
    
    return results
