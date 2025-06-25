#!/usr/bin/env python3
"""交互式测试脚本"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_single_engine(engine_name, query):
    """测试单个引擎"""
    print(f"\n=== 测试 {engine_name} 引擎 ===")
    print(f"搜索关键词: {query}")
    
    try:
        # 动态导入引擎
        engine_module = __import__(f'engines.{engine_name.lower()}', fromlist=[engine_name.lower()])
        
        # 执行搜索
        results = engine_module.search(query, 1)
        
        print(f"✓ 找到 {len(results)} 个结果")
        
        # 显示前3个结果
        for i, result in enumerate(results[:3], 1):
            print(f"\n结果 {i}:")
            print(f"  标题: {result['title']}")
            print(f"  链接: {result['url']}")
            print(f"  内容: {result['content'][:100]}...")
        
        if len(results) > 3:
            print(f"\n... 还有 {len(results) - 3} 个结果")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")

def main():
    """主函数"""
    print("简化版SearXNG引擎交互式测试")
    print("="*50)
    
    # 预定义的测试用例
    test_cases = [
        ("arxiv", "machine learning"),
        ("wikipedia", "artificial intelligence"),
        ("bing", "python programming"),
        ("github", "tensorflow"),
    ]
    
    for engine, query in test_cases:
        test_single_engine(engine, query)
        print("\n" + "-"*50)
    
    print("\n交互式测试完成！")

if __name__ == "__main__":
    main()
