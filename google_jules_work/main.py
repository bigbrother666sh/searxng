#!/usr/bin/env python3

import asyncio
import httpx
import importlib

async def search_with_engine(engine_name: str, query: str, page_number: int = 1, **kwargs):
    """使用指定的搜索引擎进行搜索"""
    try:
        # 直接从根目录导入引擎模块（不是从 engines 子目录）
        engine_module = importlib.import_module(engine_name)
    except ImportError:
        print(f"Error: Engine '{engine_name}' not found.")
        return []

    try:
        request_params = await engine_module.request(query, page_number=page_number, **kwargs)
    except Exception as e:
        print(f"Error building request for {engine_name}: {e}")
        return []

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                request_params["method"], 
                request_params["url"], 
                headers=request_params.get("headers")
            )
            response.raise_for_status()
            results = await engine_module.parse_response(response.text, **kwargs)
            return results
        except httpx.HTTPStatusError as e:
            print(f"HTTP error for {engine_name}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request error for {engine_name}: {e}")
        except Exception as e:
            print(f"Error parsing response for {engine_name}: {e}")
    return []

async def main():
    """主函数：演示多引擎搜索"""
    search_query = "Python programming"
    engines_to_use = ["arxiv", "baidu", "bing", "ebay", "github", "quark", "wikipedia"]

    print(f"Searching for: '{search_query}'")
    print("=" * 50)

    tasks = []
    for engine_name in engines_to_use:
        tasks.append(search_with_engine(engine_name, search_query))

    all_results = await asyncio.gather(*tasks)

    for i, engine_name in enumerate(engines_to_use):
        print(f"\n--- Results from {engine_name.capitalize()} ---")
        if all_results[i]:
            for j, result in enumerate(all_results[i][:5], 1):  # Print first 5 results
                print(f"  [{j}] Title: {result.get('title', 'N/A')}")
                print(f"      URL: {result.get('url', 'N/A')}")
                content = result.get('content', 'N/A')
                if content and len(content) > 100:
                    content = content[:100] + "..."
                print(f"      Content: {content}")
                print()
        else:
            print(f"  No results or an error occurred for {engine_name}.")

if __name__ == "__main__":
    asyncio.run(main()) 