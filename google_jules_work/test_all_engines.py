#!/usr/bin/env python3

import asyncio
import httpx
import importlib

async def test_engine(engine_name: str):
    """测试单个搜索引擎"""
    print(f"\n=== 测试 {engine_name.upper()} 引擎 ===")
    
    # 为不同引擎使用不同的测试查询
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
        
        # 检查引擎是否有必要的函数
        if not hasattr(engine_module, 'request') or not hasattr(engine_module, 'parse_response'):
            raise Exception(f"引擎 {engine_name} 缺少必要的 request 或 parse_response 函数")
        
        print(f"查询内容: '{query}'")
        
        # 构建请求
        request_params = await engine_module.request(query)
        
        print(f"请求 URL: {request_params['url']}")
        print(f"请求方法: {request_params['method']}")
        if request_params.get('headers'):
            print(f"请求头: {list(request_params['headers'].keys())}")
        
        # 发送请求
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        ) as client:
            response = await client.request(
                request_params["method"], 
                request_params["url"], 
                headers=request_params.get("headers")
            )
            
            print(f"响应状态: {response.status_code}")
            
            if response.status_code != 200:
                print(f"⚠️  HTTP 状态码异常: {response.status_code}")
                if response.status_code == 429:
                    print("可能遇到了速率限制，请稍后重试")
                return
            
            # 解析响应
            results = await engine_module.parse_response(response.text)
            
            if not results:
                print("⚠️  未找到搜索结果")
                return
            
            print(f"✅ 找到 {len(results)} 个结果:")
            
            # 显示前3个结果
            for i, result in enumerate(results[:3], 1):
                print(f"  [{i}] 标题: {result.get('title', 'N/A')[:80]}{'...' if len(result.get('title', '')) > 80 else ''}")
                print(f"      链接: {result.get('url', 'N/A')}")
                content = result.get('content', 'N/A')
                if content and len(content) > 120:
                    content = content[:120] + "..."
                print(f"      内容: {content}")
                print()
                
    except httpx.TimeoutException:
        print(f"❌ 请求超时")
        raise
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP 错误: {e.response.status_code}")
        raise
    except Exception as e:
        print(f"❌ 错误: {e}")
        raise

async def main():
    """测试所有引擎"""
    # 所有可用的引擎列表
    engines = ["arxiv", "baidu", "bing", "ebay", "github", "quark", "wikipedia"]
    
    print("开始测试所有搜索引擎...")
    print("=" * 60)
    
    successful_engines = []
    failed_engines = []
    
    for engine in engines:
        try:
            await test_engine(engine)
            successful_engines.append(engine)
            await asyncio.sleep(2)  # 避免请求过于频繁
        except Exception as e:
            print(f"引擎 {engine} 测试失败: {e}")
            failed_engines.append(engine)
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"✅ 成功的引擎 ({len(successful_engines)}): {', '.join(successful_engines)}")
    if failed_engines:
        print(f"❌ 失败的引擎 ({len(failed_engines)}): {', '.join(failed_engines)}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
