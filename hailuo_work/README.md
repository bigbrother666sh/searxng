# 简化版 SearXNG 搜索引擎

这是一个基于原始 SearXNG 项目的简化版本，专门设计用于轻量级集成和二次开发。

## 特点

- **扁平化架构**：只有两层目录结构，易于理解和维护
- **去异步化引擎**：每个搜索引擎都是简单的同步函数
- **最小依赖**：只依赖 `httpx` 和 `lxml` 两个核心库
- **异步兼容**：可被外部异步架构主流程按需调用
- **标准化输出**：所有引擎返回统一格式的结果

## 支持的搜索引擎

- ArXiv（学术论文）
- Baidu（百度搜索）
- Bing（微软搜索）
- eBay（购物）
- GitHub（代码仓库）
- Quark（夸克搜索）
- Wikipedia（维基百科）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 目录结构

```
simplified_engines/
├── main.py             # 异步调用示例
├── requirements.txt    # 项目依赖
├── config.py           # 通用配置
├── utils.py            # 工具函数
├── README.md           # 说明文档
└── engines/            # 搜索引擎模块
    ├── __init__.py
    ├── arxiv.py
    ├── baidu.py
    ├── bing.py
    ├── ebay.py
    ├── github.py
    ├── quark.py
    └── wikipedia.py
```

## 使用方法

### 基本使用

```python
import asyncio
from simplified_engines import run_search

# 运行搜索
asyncio.run(run_search("python programming"))
```

### 单独使用引擎

```python
from simplified_engines.engines import arxiv

# 同步调用单个引擎
results = arxiv.search("machine learning", pageno=1)
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Content: {result['content']}")
```

### 自定义异步调用

```python
import asyncio
from simplified_engines.engines import arxiv, wikipedia, github

async def custom_search(query):
    # 创建异步任务
    tasks = [
        asyncio.to_thread(arxiv.search, query, 1),
        asyncio.to_thread(wikipedia.search, query, 1),
        asyncio.to_thread(github.search, query, 1)
    ]
    
    # 并发执行
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理结果
    for i, result in enumerate(results):
        engine_names = ['ArXiv', 'Wikipedia', 'GitHub']
        if isinstance(result, Exception):
            print(f"{engine_names[i]} failed: {result}")
        else:
            print(f"{engine_names[i]} found {len(result)} results")

# 运行
asyncio.run(custom_search("artificial intelligence"))
```

## 引擎接口规范

每个引擎都提供统一的 `search` 函数：

```python
def search(query: str, pageno: int) -> list[dict]:
    """
    搜索函数
    
    Args:
        query: 搜索关键词
        pageno: 页码（从1开始）
    
    Returns:
        结果列表，每个结果包含：
        {
            'url': '结果链接',
            'title': '标题',
            'content': '内容描述'
        }
    """
```

## 配置说明

在 `config.py` 中可以修改全局配置：

```python
# 用户代理字符串
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
```

## 扩展开发

### 添加新引擎

1. 在 `engines/` 目录下创建新的 `.py` 文件
2. 实现 `search(query: str, pageno: int) -> list[dict]` 函数
3. 引擎会自动被 `main.py` 发现和调用

### 示例引擎模板

```python
import httpx
from .. import config, utils

def search(query: str, pageno: int) -> list:
    """新引擎的搜索函数"""
    try:
        # 构建搜索URL
        search_url = f"https://example.com/search?q={query}&page={pageno}"
        
        # 发起HTTP请求
        resp = httpx.get(search_url, headers={'User-Agent': config.USER_AGENT})
        resp.raise_for_status()
        
        # 解析结果
        results = []
        # ... 解析逻辑 ...
        
        return results
    except Exception as e:
        print(f"Engine error: {e}")
        return []
```

## 注意事项

- 所有引擎都是同步函数，适合被异步编排器调用
- 错误处理内置在每个引擎中，失败时返回空列表
- 建议在生产环境中添加适当的日志记录
- 遵守各搜索引擎的使用条款和爬虫政策

## 许可证

基于原始 SearXNG 项目的 AGPL-3.0 许可证进行简化和重构。
