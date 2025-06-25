#!/usr/bin/env python3

import asyncio
import httpx
import importlib

async def test_baidu():
    """测试百度搜索引擎"""
    try:
        engine_module = importlib.import_module("baidu")
        request_params = await engine_module.request("Python编程")
        
        print(f"Request URL: {request_params['url']}")
        print(f"Request Method: {request_params['method']}")
        print("Request Headers:", request_params.get('headers', 'None'))
        print("-" * 50)
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                request_params["method"], 
                request_params["url"], 
                headers=request_params.get("headers")
            )
            response.raise_for_status()
            
            results = await engine_module.parse_response(response.text)
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results[:3], 1):  # Show first 3 results
                print(f"\n[{i}] Title: {result.get('title', 'N/A')}")
                print(f"    URL: {result.get('url', 'N/A')}")
                print(f"    Content: {result.get('content', 'N/A')[:200]}...")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_baidu()) 