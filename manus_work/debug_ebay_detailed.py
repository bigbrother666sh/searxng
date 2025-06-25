import asyncio
import httpx
import importlib
from lxml import html
from core.utils import extract_text

async def debug_ebay_detailed():
    try:
        engine_module = importlib.import_module("engines.ebay")
        request_params = await engine_module.request("sungsang 910")
        
        async with httpx.AsyncClient() as client:
            response = await client.request(request_params["method"], request_params["url"], headers=request_params.get("headers"))
            
            dom = html.fromstring(response.text.encode("utf-8"))
            
            # Use the same XPath as in the engine
            results_xpath = '//li[contains(@class, "s-item")]'
            results_dom = dom.xpath(results_xpath)
            
            print(f"Found {len(results_dom)} items with XPath: {results_xpath}")
            
            if results_dom:
                # Check the first few items
                for i, result_dom in enumerate(results_dom[:3]):
                    print(f"\n--- Item {i+1} ---")
                    
                    # Test each XPath individually
                    url_xpath = './/a[@class="s-item__link"]/@href'
                    title_xpath = './/h3[@class="s-item__title"]'
                    content_xpath = './/div[@span="SECONDARY_INFO"]'
                    price_xpath = './/div[contains(@class, "s-item__detail")]/span[@class="s-item__price"][1]/text()'
                    
                    url = extract_text(result_dom.xpath(url_xpath))
                    title = extract_text(result_dom.xpath(title_xpath))
                    content = extract_text(result_dom.xpath(content_xpath))
                    price = extract_text(result_dom.xpath(price_xpath))
                    
                    print(f"URL XPath result: {url}")
                    print(f"Title XPath result: {title}")
                    print(f"Content XPath result: {content}")
                    print(f"Price XPath result: {price}")
                    
                    # Let's also try some alternative XPaths
                    alt_title_xpath = './/h3//text()'
                    alt_price_xpath = './/span[contains(@class, "s-item__price")]//text()'
                    alt_url_xpath = './/a/@href'
                    
                    alt_title = extract_text(result_dom.xpath(alt_title_xpath))
                    alt_price = extract_text(result_dom.xpath(alt_price_xpath))
                    alt_url = extract_text(result_dom.xpath(alt_url_xpath))
                    
                    print(f"Alt Title XPath result: {alt_title}")
                    print(f"Alt Price XPath result: {alt_price}")
                    print(f"Alt URL XPath result: {alt_url}")
                    
                    # Print the raw HTML of this item (first 1000 chars)
                    print(f"Raw HTML (first 1000 chars):")
                    print(html.tostring(result_dom, encoding='unicode')[:1000])
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_ebay_detailed())
