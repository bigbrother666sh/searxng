# Simplified SearXNG Search Engines

This project is a simplified version of the SearXNG search engine, focusing on a modular and easy-to-integrate design. It retains only a subset of the original search engines and removes the complex asynchronous and threading management, making the engine scripts simple, standalone functions that can be called by an external asynchronous main process.

## Project Structure

```
simplified_searxng/
├── engines/             # Contains the simplified search engine scripts
├── core/                # Contains core utility functions
├── main.py              # Example main script to demonstrate engine usage
├── requirements.txt     # Project dependencies
└── README.md            # This README file
```

## Features

*   **Selected Engines**: Only the following search engines are included:
    *   `arxiv.py`
    *   `baidu.py`
    *   `bing.py`
    *   `ebay.py`
    *   `github.py`
    *   `quark.py`
    *   `wikipedia.py`
*   **Simplified Logic**: Each engine is implemented as a pair of `async` functions (`request` and `parse_response`) that handle request building and response parsing, respectively. They are designed to be easily integrated into any asynchronous Python application.
*   **Flat Directory Structure**: The project maintains a shallow directory hierarchy (maximum three levels) for improved readability and maintainability.

## Installation

1.  **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd simplified_searxng
    ```

2.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

The `main.py` script provides an example of how to use the simplified search engines. It demonstrates how to concurrently query multiple engines and process their results.

To run the example:

```bash
python main.py
```

### Integrating Engines into Your Project

Each engine in the `engines/` directory exposes two `async` functions:

*   `async def request(query: str, page_number: int = 1, **kwargs) -> dict:`
    *   Prepares the request parameters (URL, method, headers, etc.) for the search engine.
    *   `query`: The search query string.
    *   `page_number`: The page number for results (defaults to 1).
    *   `**kwargs`: Additional parameters specific to the engine (e.g., `time_range` for Baidu/Bing/Quark, `language` for Bing/Wikipedia, `category` for Baidu/Quark).
    *   Returns a dictionary containing `url`, `method`, and optionally `headers` for the HTTP request.

*   `async def parse_response(response_text: str, **kwargs) -> list[dict]:`
    *   Parses the raw HTTP response text and extracts structured search results.
    *   `response_text`: The raw text content of the HTTP response.
    *   `**kwargs`: Additional context that might be needed for parsing (e.g., `category` for Baidu/Quark).
    *   Returns a list of dictionaries, where each dictionary represents a search result (e.g., `{'title': '...', 'url': '...', 'content': '...'}`).

**Example Snippet (from `main.py`)**:

```python
import asyncio
import httpx
import importlib

async def search_with_engine(engine_name: str, query: str, page_number: int = 1, **kwargs):
    try:
        engine_module = importlib.import_module(f"engines.{engine_name}")
    except ImportError:
        print(f"Error: Engine \'{engine_name}\' not found.")
        return []

    try:
        request_params = await engine_module.request(query, page_number=page_number, **kwargs)
    except Exception as e:
        print(f"Error building request for {engine_name}: {e}")
        return []

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(request_params["method"], request_params["url"], headers=request_params.get("headers"))
            response.raise_for_status()
            results = await engine_module.parse_response(response.text, **kwargs)
            return results
        except httpx.HTTPStatusError as e:
            print(f"HTTP error for {engine_name}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request error for {engine_name}: {e}")
        except Exception as e:
            print(f"Error parsing response for {engine_name}: {e}")
    return []

async def main():
    search_query = "Python programming"
    engines_to_use = ["arxiv", "baidu", "bing", "ebay", "github", "quark", "wikipedia"]

    tasks = []
    for engine_name in engines_to_use:
        tasks.append(search_with_engine(engine_name, search_query))

    all_results = await asyncio.gather(*tasks)

    for i, engine_name in enumerate(engines_to_use):
        print(f"\n--- Results from {engine_name.capitalize()} ---")
        if all_results[i]:
            for result in all_results[i][:5]:  # Print first 5 results
                print(f"  Title: {result.get("title")}")
                print(f"  URL: {result.get("url")}")
                print(f"  Content: {result.get("content", "N/A")[:100]}...")
                print("\n")
        else:
            print(f"  No results or an error occurred for {engine_name}.")

if __name__ == "__main__":
    asyncio.run(main())
```

## Contributing

Contributions are welcome! If you find a bug or want to add another simplified engine, please open an issue or submit a pull request.

