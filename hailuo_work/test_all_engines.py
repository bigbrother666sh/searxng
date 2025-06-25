#!/usr/bin/env python3
"""测试所有搜索引擎的功能"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_all_engines_sync():
    """同步测试所有引擎"""
    print("=== 同步测试所有引擎 ===")
    
    engines_to_test = [
        ('ArXiv', 'arxiv', 'machine learning'),
        ('Wikipedia', 'wikipedia', 'artificial intelligence'),
        ('Bing', 'bing', 'python programming'),
        ('GitHub', 'github', 'machine learning'),
        ('Baidu', 'baidu', 'python编程'),
        ('Quark', 'quark', 'AI技术'),
        ('eBay', 'ebay', 'laptop'),
    ]
    
    results = {}
    
    for engine_name, module_name, query in engines_to_test:
        print(f"\n--- 测试 {engine_name} 引擎 ---")
        try:
            # 动态导入引擎模块
            engine_module = __import__(f'engines.{module_name}', fromlist=[module_name])
            
            # 调用搜索函数
            search_results = engine_module.search(query, 1)
            
            print(f"✓ {engine_name} 成功返回 {len(search_results)} 个结果")
            if search_results:
                print(f"  第一个结果: {search_results[0]['title'][:60]}...")
                print(f"  URL: {search_results[0]['url']}")
            
            results[engine_name] = {
                'success': True,
                'count': len(search_results),
                'results': search_results
            }
            
        except Exception as e:
            print(f"✗ {engine_name} 引擎失败: {e}")
            results[engine_name] = {
                'success': False,
                'error': str(e)
            }
    
    return results

async def test_all_engines_async():
    """异步测试所有引擎"""
    print("\n=== 异步测试所有引擎 ===")
    
    engines_to_test = [
        ('ArXiv', 'arxiv', 'quantum computing'),
        ('Wikipedia', 'wikipedia', 'quantum computing'),
        ('Bing', 'bing', 'quantum computing'),
        ('GitHub', 'github', 'quantum computing'),
    ]
    
    # 创建异步任务
    tasks = []
    engine_names = []
    
    for engine_name, module_name, query in engines_to_test:
        try:
            engine_module = __import__(f'engines.{module_name}', fromlist=[module_name])
            tasks.append(asyncio.to_thread(engine_module.search, query, 1))
            engine_names.append(engine_name)
        except Exception as e:
            print(f"✗ 无法导入 {engine_name}: {e}")
    
    if not tasks:
        print("没有可用的引擎进行异步测试")
        return
    
    # 并发执行
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理结果
    for name, result in zip(engine_names, results):
        if isinstance(result, Exception):
            print(f"✗ {name} 异步调用失败: {result}")
        else:
            print(f"✓ {name} 异步调用成功，返回 {len(result)} 个结果")
            if result:
                print(f"  示例: {result[0]['title'][:50]}...")

def print_summary(sync_results):
    """打印测试总结"""
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    successful = [name for name, result in sync_results.items() if result['success']]
    failed = [name for name, result in sync_results.items() if not result['success']]
    
    print(f"✓ 成功的引擎 ({len(successful)}): {', '.join(successful)}")
    if failed:
        print(f"✗ 失败的引擎 ({len(failed)}): {', '.join(failed)}")
    
    print(f"\n总体成功率: {len(successful)}/{len(sync_results)} ({len(successful)/len(sync_results)*100:.1f}%)")
    
    # 显示详细的失败信息
    if failed:
        print("\n失败详情:")
        for name in failed:
            print(f"  {name}: {sync_results[name]['error']}")

if __name__ == "__main__":
    print("开始全面测试简化版SearXNG引擎...\n")
    
    # 同步测试
    sync_results = test_all_engines_sync()
    
    # 异步测试
    try:
        asyncio.run(test_all_engines_async())
    except Exception as e:
        print(f"异步测试过程中出错: {e}")
    
    # 打印总结
    print_summary(sync_results)
    
    print("\n测试完成！")
