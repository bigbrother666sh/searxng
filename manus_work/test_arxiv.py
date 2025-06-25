
import asyncio
import httpx
import importlib

async def test_arxiv():
    try:
        engine_module = importlib.import_module("engines.arxiv")
        request_params = await engine_module.request("Python programming")
        async with httpx.AsyncClient() as client:
            response = await client.request(request_params["method"], request_params["url"], headers=request_params.get("headers"))
            response.raise_for_status()
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_arxiv())


