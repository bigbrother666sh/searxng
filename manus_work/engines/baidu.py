
from urllib.parse import urlencode
from lxml import html
from core.utils import extract_text

async def request(query: str, page_number: int = 1, time_range: str = None, category: str = None, **kwargs) -> dict:
    base_url = "https://www.baidu.com/s"
    params = {
        "wd": query,
        "rn": 10,  # results per page
        "pn": (page_number - 1) * 10,
        "tn": "json" # Request JSON format if possible, though Baidu often returns HTML
    }

    if time_range:
        # Baidu time range mapping is complex and not directly exposed via simple params
        # This part might need more advanced handling or be removed if not critical
        pass

    if category:
        # Baidu category mapping is also complex and not directly exposed
        pass

    return {
        "url": f"{base_url}?{urlencode(params)}",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }
    }

async def parse_response(response_text: str, **kwargs) -> list[dict]:
    results = []
    try:
        dom = html.fromstring(response_text)
    except Exception as e:
        print(f"HTML parsing error for Baidu: {e}")
        return []

    # Check for CAPTCHA or other redirects
    if "wappass.baidu.com/static/captcha" in response_text:
        print("Baidu CAPTCHA detected. Cannot parse results.")
        return []

    # Attempt to parse results from the HTML structure
    for result in dom.xpath("//div[@id=\"content_left\"]/div[contains(@class, \"result\")]"):
        title_element = result.xpath(".//h3/a")
        url_element = result.xpath(".//h3/a")
        content_element = result.xpath(".//div[@class=\"c-abstract\"]")

        title = extract_text(title_element) if title_element else None
        url = url_element[0].get("href") if url_element else None
        content = extract_text(content_element) if content_element else None

        if title and url:
            results.append({"title": title, "url": url, "content": content})

    return results


