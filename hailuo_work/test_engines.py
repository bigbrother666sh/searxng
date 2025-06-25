#!/usr/bin/env python3
"""测试简化版搜索引擎的功能"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from engines import arxiv, wikipedia


def test_single_engine():
    """测试单个引擎的同步调用"""
    print("=== 测试单个引擎（同步调用）===")
    
    # 测试ArXiv引擎
    print("\n--- 测试ArXiv引擎 ---")
    try:
        results = arxiv.search("machine learning", 1)
        print(f"ArXiv返回 {len(results)} 个结果")
        if results:
            print(f"第一个结果: {results[0]['title'][:50]}...")
    except Exception as e:
        print(f"ArXiv引擎失败: {e}")
    
    # 测试Wikipedia引擎
    print("\n--- 测试Wikipedia引擎 ---")
    try:
        results = wikipedia.search("artificial intelligence", 1)
        print(f"Wikipedia返回 {len(results)} 个结果")
        if results:
            print(f"第一个结果: {results[0]['title'][:50]}...")
    except Exception as e:
        print(f"Wikipedia引擎失败: {e}")


async def test_async_engines():
    """测试引擎的异步调用"""
    print("\n=== 测试引擎（异步调用）===")
    
    # 创建异步任务
    tasks = [
        asyncio.to_thread(arxiv.search, "quantum computing", 1),
        asyncio.to_thread(wikipedia.search, "quantum computing", 1),
    ]
    
    try:
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        engine_names = ['ArXiv', 'Wikipedia']
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"{engine_names[i]} 异步调用失败: {result}")
            else:
                print(f"{engine_names[i]} 异步调用成功，返回 {len(result)} 个结果")
                if result:
                    print(f"  第一个结果: {result[0]['title'][:50]}...")
    except Exception as e:
        print(f"异步调用过程中出错: {e}")


async def test_main_orchestrator():
    """测试主编排器"""
    print("\n=== 测试主编排器 ===")
    
    try:
        from main import run_search
        await run_search("python programming")
    except Exception as e:
        print(f"主编排器测试失败: {e}")


if __name__ == "__main__":
    print("开始测试简化版SearXNG引擎...\n")
    
    # 测试同步调用
    test_single_engine()
    
    # 测试异步调用
    print("\n" + "="*50)
    asyncio.run(test_async_engines())
    
    # 测试主编排器
    print("\n" + "="*50)
    asyncio.run(test_main_orchestrator())
    
    print("\n测试完成！")
