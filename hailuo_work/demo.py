#!/usr/bin/env python3
"""简化版SearXNG引擎演示脚本"""

import asyncio
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """测试模块导入是否正常"""
    print("=== 测试模块导入 ===")
    try:
        import config
        print("✓ config模块导入成功")
        
        import utils
        print("✓ utils模块导入成功")
        
        from engines import arxiv
        print("✓ arxiv引擎导入成功")
        
        from engines import wikipedia
        print("✓ wikipedia引擎导入成功")
        
        print("✓ 所有核心模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_single_engine():
    """测试单个引擎的同步调用"""
    print("\n=== 测试单个引擎（同步调用）===")
    
    try:
        from engines import arxiv
        print("测试ArXiv引擎...")
        results = arxiv.search("python", 1)
        print(f"✓ ArXiv引擎测试成功，返回 {len(results)} 个结果")
        if results:
            print(f"  示例结果: {results[0]['title'][:50]}...")
        return True
    except Exception as e:
        print(f"✗ 引擎测试失败: {e}")
        return False

async def test_async_call():
    """测试异步调用"""
    print("\n=== 测试异步调用 ===")
    
    try:
        from engines import arxiv, wikipedia
        
        # 创建异步任务
        tasks = [
            asyncio.to_thread(arxiv.search, "machine learning", 1),
            asyncio.to_thread(wikipedia.search, "machine learning", 1),
        ]
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        for i, result in enumerate(results):
            engine_name = ['ArXiv', 'Wikipedia'][i]
            if isinstance(result, Exception):
                print(f"✗ {engine_name} 异步调用失败: {result}")
            else:
                print(f"✓ {engine_name} 异步调用成功，返回 {len(result)} 个结果")
                success_count += 1
        
        return success_count > 0
    except Exception as e:
        print(f"✗ 异步调用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("简化版SearXNG引擎功能测试\n")
    print("=" * 50)
    
    # 测试导入
    if not test_import():
        print("\n测试失败：模块导入错误")
        return
    
    # 测试单引擎
    if not test_single_engine():
        print("\n测试失败：单引擎调用错误")
        return
    
    # 测试异步调用
    try:
        success = asyncio.run(test_async_call())
        if not success:
            print("\n测试失败：异步调用错误")
            return
    except Exception as e:
        print(f"\n异步测试过程中出错: {e}")
        return
    
    print("\n" + "=" * 50)
    print("✓ 所有测试通过！系统运行正常。")
    print("\n使用方法:")
    print("  python main.py [搜索关键词]")
    print("  python demo.py")

if __name__ == "__main__":
    main()
