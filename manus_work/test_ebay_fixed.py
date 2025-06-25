#!/usr/bin/env python3

import asyncio
import httpx
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engines.ebay import request, parse_response
from core.utils import gen_useragent

async def test_ebay_fixed():
    query = "sungsang 910"
    
    print(f"Testing eBay search with query: '{query}'")
    print("=" * 50)
    
    try:
        # Get request parameters
        request_params = await request(query)
        print(f"Request URL: {request_params['url']}")
        print(f"Request Method: {request_params['method']}")
        
        # Make the request
        headers = {
            'User-Agent': gen_useragent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                request_params["method"], 
                request_params["url"], 
                headers=headers
            )
            response.raise_for_status()
            
            print(f"HTTP Status: {response.status_code}")
            print(f"Response length: {len(response.text)} characters")
            
            # Parse the response
            results = await parse_response(response.text)
            
            print(f"\nFound {len(results)} results:")
            print("=" * 50)
            
            for i, result in enumerate(results[:5], 1):  # Show first 5 results
                print(f"\nResult {i}:")
                print(f"  Title: {result.get('title', 'N/A')}")
                print(f"  URL: {result.get('url', 'N/A')}")
                print(f"  Price: {result.get('price', 'N/A')}")
                print(f"  Content: {result.get('content', 'N/A')}")
                print(f"  Shipping: {result.get('shipping', 'N/A')}")
                print(f"  Source Country: {result.get('source_country', 'N/A')}")
                print("-" * 40)
            
            if len(results) > 5:
                print(f"\n... and {len(results) - 5} more results")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ebay_fixed())
