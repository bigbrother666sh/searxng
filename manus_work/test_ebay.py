
import asyncio
import httpx
import importlib

async def test_ebay():
    try:
        engine_module = importlib.import_module("engines.ebay")
        request_params = await engine_module.request("Python programming")
        async with httpx.AsyncClient() as client:
            response = await client.request(request_params["method"], request_params["url"], headers=request_params.get("headers"))
            response.raise_for_status()
            results = await engine_module.parse_response(response.text)
            for result in results[:5]:
                print(f'  Title: {result.get("title")}')
                print(f'  URL: {result.get("url")}')
                print(f'  Content: {result.get("content", "N/A")[:100]}...')
                print("\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ebay())


