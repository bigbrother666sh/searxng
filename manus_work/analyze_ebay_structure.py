#!/usr/bin/env python3

import asyncio
import httpx
from lxml import html
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.utils import gen_useragent

async def analyze_ebay_structure():
    query = "iphone"
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}&_sacat=1"
    
    headers = {
        'User-Agent': gen_useragent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse HTML
            tree = html.fromstring(response.text)
            
            # Find all items
            items = tree.xpath('//li[contains(@class, "s-item")]')
            print(f"Found {len(items)} items")
            
            if len(items) > 0:
                # Skip the first few items as they might be ads, analyze items 3-6
                start_index = 2  # Skip first 2 items
                end_index = min(6, len(items))  # Analyze up to 4 real items
                
                for i in range(start_index, end_index):
                    item = items[i]
                    print(f"\n=== ANALYZING ITEM {i+1} ===")
                    
                    # Get the raw HTML for this item
                    item_html = html.tostring(item, encoding='unicode')
                    
                    # Look for different possible title selectors
                    title_selectors = [
                        './/h3[@class="s-item__title"]',
                        './/h3[@class="s-item__title"]//text()',
                        './/h3//text()',
                        './/span[@role="heading"]',
                        './/span[@role="heading"]//text()',
                        './/a[contains(@class, "s-item__link")]/@title',
                        './/a[contains(@class, "s-item__link")]//text()',
                        './/*[contains(@class, "title")]//text()',
                        './/*[contains(@class, "s-item__title")]//text()',
                        './/div[contains(@class, "s-item__title")]//text()',
                        './/span[contains(@class, "s-item__title")]//text()',
                    ]
                    
                    print("Testing different title selectors:")
                    for selector in title_selectors:
                        try:
                            results = item.xpath(selector)
                            if results:
                                print(f"  ✓ {selector}: {results[:3]}")  # Show first 3 results
                            else:
                                print(f"  ✗ {selector}: No results")
                        except Exception as e:
                            print(f"  ✗ {selector}: Error - {e}")
                    
                    # Look for all text content in the item
                    print("\nAll text content in item:")
                    all_text = item.xpath('.//text()')
                    meaningful_text = [text.strip() for text in all_text if text.strip() and len(text.strip()) > 3]
                    for j, text in enumerate(meaningful_text[:10]):  # Show first 10 meaningful texts
                        print(f"  {j+1}: {text}")
                    
                    # Look for specific patterns that might be titles
                    print("\nLooking for potential title patterns:")
                    
                    # Check for aria-label attributes
                    aria_labels = item.xpath('.//@aria-label')
                    if aria_labels:
                        print(f"  aria-label attributes: {aria_labels}")
                    
                    # Check for title attributes
                    title_attrs = item.xpath('.//@title')
                    if title_attrs:
                        print(f"  title attributes: {title_attrs}")
                    
                    # Look for links that might contain titles
                    links = item.xpath('.//a')
                    print(f"  Found {len(links)} links in this item")
                    for k, link in enumerate(links[:3]):
                        link_text = ' '.join(link.xpath('.//text()')).strip()
                        link_title = link.get('title', '')
                        link_aria = link.get('aria-label', '')
                        if link_text or link_title or link_aria:
                            print(f"    Link {k+1}:")
                            if link_text:
                                print(f"      Text: {link_text}")
                            if link_title:
                                print(f"      Title attr: {link_title}")
                            if link_aria:
                                print(f"      Aria-label: {link_aria}")
                    
                    print("-" * 80)
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_ebay_structure())
