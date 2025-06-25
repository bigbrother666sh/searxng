import asyncio
import httpx
import importlib
from lxml import html
from core.utils import extract_text

async def find_title_selector():
    try:
        engine_module = importlib.import_module("engines.ebay")
        request_params = await engine_module.request("sungsang 910")
        
        async with httpx.AsyncClient() as client:
            response = await client.request(request_params["method"], request_params["url"], headers=request_params.get("headers"))
            
            dom = html.fromstring(response.text.encode("utf-8"))
            
            # Get the first item
            results_dom = dom.xpath('//li[contains(@class, "s-item")]')
            if results_dom:
                first_item = results_dom[2]  # Use the 3rd item as it seems to have real data
                
                # Try different title selectors
                title_selectors = [
                    './/h3[@class="s-item__title"]',
                    './/h3[contains(@class, "s-item__title")]',
                    './/span[contains(@class, "s-item__title")]',
                    './/div[contains(@class, "s-item__title")]',
                    './/a[contains(@class, "s-item__link")]//span',
                    './/a[contains(@class, "s-item__link")]//text()[normalize-space()]',
                    './/*[contains(@class, "title")]',
                    './/span[@role="heading"]',
                    './/h3//span//text()',
                    './/span[contains(@class, "BOLD")]'
                ]
                
                print("Testing different title selectors:")
                for selector in title_selectors:
                    try:
                        result = first_item.xpath(selector)
                        if result:
                            text = extract_text(result)
                            if text.strip():
                                print(f"✓ '{selector}' -> '{text[:100]}'")
                            else:
                                print(f"✗ '{selector}' -> empty text")
                        else:
                            print(f"✗ '{selector}' -> no match")
                    except Exception as e:
                        print(f"✗ '{selector}' -> error: {e}")
                
                # Let's also look at the raw HTML structure around links
                print("\n--- Raw HTML structure (first 2000 chars) ---")
                print(html.tostring(first_item, encoding='unicode')[:2000])
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(find_title_selector())
