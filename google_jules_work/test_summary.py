#!/usr/bin/env python3
"""
简化版搜索引擎测试总结脚本
"""

import asyncio
import httpx
import importlib

async def quick_test_engine(engine_name: str) -> dict:
    """快速测试单个引擎并返回结果"""
    test_queries = {
        "arxiv": "machine learning",
        "baidu": "人工智能", 
        "bing": "python programming",
        "ebay": "laptop computer",
        "github": "tensorflow",
        "quark": "深度学习",
        "wikipedia": "Artificial Intelligence"
    }
    
    query = test_queries.get(engine_name, "python programming")
    
    try:
        engine_module = importlib.import_module(engine_name)
        request_params = await engine_module.request(query)
        
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        ) as client:
            response = await client.request(
                request_params["method"], 
                request_params["url"], 
                headers=request_params.get("headers")
            )
            
            if response.status_code != 200:
                return {
                    'status': 'failed',
                    'error': f'HTTP {response.status_code}',
                    'results_count': 0
                }
            
            results = await engine_module.parse_response(response.text)
            
            return {
                'status': 'success' if results else 'no_results',
                'results_count': len(results),
                'query': query,
                'url': request_params['url']
            }
            
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)[:100],
            'results_count': 0
        }

async def main():
    """运行所有引擎的快速测试"""
    engines = ["arxiv", "baidu", "bing", "ebay", "github", "quark", "wikipedia"]
    
    print("🔍 SearXNG 简化版搜索引擎测试报告")
    print("=" * 60)
    
    results = {}
    for engine in engines:
        print(f"测试 {engine.upper()}...", end=" ")
        result = await quick_test_engine(engine)
        results[engine] = result
        
        if result['status'] == 'success':
            print(f"✅ ({result['results_count']} 个结果)")
        elif result['status'] == 'no_results':
            print("⚠️  (无结果)")
        else:
            print(f"❌ ({result.get('error', 'Unknown error')})")
        
        await asyncio.sleep(1)
    
    # 详细报告
    print("\n" + "=" * 60)
    print("详细测试结果:")
    print("=" * 60)
    
    successful = []
    failed = []
    
    for engine, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "⚠️" if result['status'] == 'no_results' else "❌"
        print(f"{status_icon} {engine.upper():<12} | 结果数: {result['results_count']:<3} | 查询: {result.get('query', 'N/A')}")
        
        if result['status'] == 'success':
            successful.append(engine)
        else:
            failed.append(engine)
    
    print("=" * 60)
    print(f"📊 总结: {len(successful)}/{len(engines)} 个引擎正常工作")
    print(f"✅ 成功: {', '.join(successful)}")
    if failed:
        print(f"❌ 需要修复: {', '.join(failed)}")

if __name__ == "__main__":
    asyncio.run(main())
