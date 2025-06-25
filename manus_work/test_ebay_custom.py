import asyncio
import httpx
import importlib

async def test_ebay_custom():
    try:
        engine_module = importlib.import_module("engines.ebay")
        request_params = await engine_module.request("sungsang 910")
        
        print(f"Request URL: {request_params['url']}")
        print(f"Request Method: {request_params['method']}")
        print(f"Request Headers: {request_params.get('headers', 'None')}")
        print("\n")
        
        async with httpx.AsyncClient() as client:
            response = await client.request(request_params["method"], request_params["url"], headers=request_params.get("headers"))
            print(f"Response Status: {response.status_code}")
            response.raise_for_status()
            
            results = await engine_module.parse_response(response.text)
            print(f"Found {len(results)} results:")
            
            for i, result in enumerate(results[:10]):  # Show first 10 results
                print(f"\n--- Result {i+1} ---")
                print(f'  Title: {result.get("title")}')
                print(f'  URL: {result.get("url")}')
                print(f'  Price: {result.get("price", "N/A")}')
                print(f'  Content: {result.get("content", "N/A")[:150]}...')
                
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ebay_custom())
