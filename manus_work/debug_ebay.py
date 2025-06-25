import asyncio
import httpx
import importlib
from lxml import html

async def debug_ebay():
    try:
        engine_module = importlib.import_module("engines.ebay")
        request_params = await engine_module.request("sungsang 910")
        
        print(f"Request URL: {request_params['url']}")
        
        async with httpx.AsyncClient() as client:
            response = await client.request(request_params["method"], request_params["url"], headers=request_params.get("headers"))
            print(f"Response Status: {response.status_code}")
            
            # Save the raw HTML for inspection
            with open("ebay_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Raw HTML saved to ebay_response.html")
            
            # Try to find what elements are actually present
            dom = html.fromstring(response.text.encode("utf-8"))
            
            # Check for different possible selectors
            selectors_to_try = [
                '//li[contains(@class, "s-item")]',
                '//div[contains(@class, "s-item")]',
                '//div[contains(@class, "srp-item")]',
                '//div[contains(@class, "item")]',
                '//li[contains(@class, "srp-item")]',
                '//div[@data-testid="item-card"]',
                '//div[contains(@class, "result")]'
            ]
            
            for selector in selectors_to_try:
                elements = dom.xpath(selector)
                print(f"Selector '{selector}': Found {len(elements)} elements")
                if elements:
                    # Print first element's HTML for inspection
                    print(f"First element HTML (first 500 chars):")
                    print(html.tostring(elements[0], encoding='unicode')[:500])
                    break
            
            # Also check the page title to make sure we got the right page
            title_elements = dom.xpath('//title/text()')
            if title_elements:
                print(f"Page title: {title_elements[0]}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_ebay())
