# Simplified SearXNG Search Engines

这是一个简化版的 SearXNG 搜索引擎项目，专注于模块化和易于集成的设计。项目保留了原始搜索引擎的一个子集，移除了复杂的异步和线程管理，使引擎脚本变成简单的独立函数，可以被外部异步主进程调用。

## 项目结构

```
google_jules_work/
├── arxiv.py           # ArXiv 学术搜索引擎
├── baidu.py           # 百度搜索引擎
├── bing.py            # 必应搜索引擎
├── ebay.py            # eBay 商品搜索引擎
├── github.py          # GitHub 代码搜索引擎
├── quark.py           # 夸克搜索引擎
├── wikipedia.py       # 维基百科搜索引擎
├── utils.py           # 工具函数库
├── exceptions.py      # 自定义异常类
├── main.py            # 示例主程序
├── requirements.txt   # 项目依赖
├── test_*.py          # 各引擎的测试文件
└── README.md          # 本文档
```

## 特性

*   **精选引擎**: 包含以下搜索引擎:
    *   `arxiv.py` - ArXiv 学术论文搜索
    *   `baidu.py` - 百度网页搜索
    *   `bing.py` - 必应网页搜索
    *   `ebay.py` - eBay 商品搜索
    *   `github.py` - GitHub 代码搜索
    *   `quark.py` - 夸克搜索
    *   `wikipedia.py` - 维基百科搜索

*   **简化逻辑**: 每个引擎都实现为一对 `async` 函数（`request` 和 `parse_response`），分别处理请求构建和响应解析。它们设计为可以轻松集成到任何异步 Python 应用中。

*   **扁平目录结构**: 项目保持浅层目录层次结构，提高可读性和可维护性。

## 安装

1.  **克隆仓库**:

    ```bash
    git clone <repository_url>
    cd google_jules_work
    ```

2.  **安装依赖**:

    ```bash
    pip install -r requirements.txt
    ```

## 使用方法

`main.py` 脚本提供了如何使用简化搜索引擎的示例。它演示了如何并发查询多个引擎并处理其结果。

运行示例:

```bash
python main.py
```

### 将引擎集成到你的项目中

每个引擎都暴露两个 `async` 函数:

*   `async def request(query: str, page_number: int = 1, **kwargs) -> dict:`
    *   为搜索引擎准备请求参数（URL、方法、headers 等）。
    *   `query`: 搜索查询字符串。
    *   `page_number`: 结果页码（默认为 1）。
    *   `**kwargs`: 引擎特定的额外参数（例如，Baidu/Bing/Quark 的 `time_range`，Bing/Wikipedia 的 `language`，Baidu/Quark 的 `category`）。
    *   返回包含 `url`、`method` 和可选 `headers` 的字典，用于 HTTP 请求。

*   `async def parse_response(response_text: str, **kwargs) -> list[dict]:`
    *   解析原始 HTTP 响应文本并提取结构化搜索结果。
    *   `response_text`: HTTP 响应的原始文本内容。
    *   `**kwargs`: 解析可能需要的额外上下文（例如，Baidu/Quark 的 `category`）。
    *   返回字典列表，每个字典代表一个搜索结果（例如，`{'title': '...', 'url': '...', 'content': '...'}`）。

**示例代码片段（来自 `main.py`）**:

```python
import asyncio
import httpx
import importlib

async def search_with_engine(engine_name: str, query: str, page_number: int = 1, **kwargs):
    try:
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
        except Exception as e:
            print(f"Error for {engine_name}: {e}")
    return []
```

## 测试

每个引擎都有对应的测试文件:

```bash
python test_arxiv.py
python test_baidu.py
python test_bing.py
python test_ebay.py
python test_github.py
python test_quark.py
python test_wikipedia.py
```

## 贡献

欢迎贡献！如果你发现了 bug 或想添加另一个简化引擎，请提交 issue 或 pull request。

## 许可证

本项目基于原 SearXNG 项目，遵循相同的开源许可证。 