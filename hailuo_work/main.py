# Main orchestrator for simplified search engines

import asyncio
import importlib
import pkgutil
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engines

async def run_search(query):
    """Asynchronously run all search engines and aggregate results."""
    # 直接导入引擎模块
    engine_modules = []
    try:
        from engines import arxiv, wikipedia, bing, github
        engine_modules = [
            ('ArXiv', arxiv),
            ('Wikipedia', wikipedia),
            ('Bing', bing),
            ('GitHub', github),
        ]
    except ImportError as e:
        print(f"Failed to import engines: {e}")
        return

    # Create a list of coroutines to run in parallel
    tasks = []
    engine_names = []
    for name, engine in engine_modules:
        if hasattr(engine, 'search'):
            tasks.append(asyncio.to_thread(engine.search, query, 1))
            engine_names.append(name)

    if not tasks:
        print("No engines available")
        return

    # Run all tasks concurrently and wait for them to complete
    all_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process and print results
    print(f"--- Search Results for '{query}' ---")
    for name, results in zip(engine_names, all_results):
        if isinstance(results, Exception):
            print(f"\nEngine '{name}' failed: {results}")
        else:
            print(f"\n--- Results from {name} ---")
            if results:
                for result in results[:3]:  # 只显示前3个结果
                    print(f"  Title: {result['title']}")
                    print(f"  URL: {result['url']}")
                    print(f"  Content: {result['content'][:150]}...")
                    print("--")
                print(f"  ... and {len(results)} total results")
            else:
                print("No results found.")

if __name__ == "__main__":
    import sys
    
    # 获取搜索关键词
    if len(sys.argv) > 1:
        search_query = " ".join(sys.argv[1:])
    else:
        search_query = "artificial intelligence"
    
    print(f"Starting search for: '{search_query}'")
    asyncio.run(run_search(search_query))
