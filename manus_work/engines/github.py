
from urllib.parse import urlencode
from dateutil import parser

async def request(query: str, **kwargs) -> dict:
    search_url = 'https://api.github.com/search/repositories?sort=stars&order=desc&{query}'
    accept_header = 'application/vnd.github.preview.text-match+json'

    return {
        'url': search_url.format(query=urlencode({'q': query})),
        'method': 'GET',
        'headers': {'Accept': accept_header}
    }


async def parse_response(response_text: str, **kwargs) -> list[dict]:
    results = []
    import json

    data = json.loads(response_text)

    for item in data.get('items', []):
        content = [item.get(i) for i in ['language', 'description'] if item.get(i)]

        lic = item.get('license') or {}
        lic_url = None
        if lic.get('spdx_id'):
            lic_url = f"https://spdx.org/licenses/{lic.get('spdx_id')}.html"

        results.append(
            {
                'url': item.get('html_url'),
                'title': item.get('full_name'),
                'content': ' / '.join(content),
                'thumbnail': item.get('owner', {}).get('avatar_url'),
                'package_name': item.get('name'),
                'maintainer': item.get('owner', {}).get('login'),
                'publishedDate': parser.parse(item.get("updated_at") or item.get("created_at")),
                'tags': item.get('topics', []),
                'popularity': item.get('stargazers_count'),
                'license_name': lic.get('name'),
                'license_url': lic_url,
                'homepage': item.get('homepage'),
                'source_code_url': item.get('clone_url'),
            }
        )

    return results


