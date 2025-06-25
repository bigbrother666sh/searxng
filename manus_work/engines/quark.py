
from urllib.parse import urlencode
from datetime import datetime
import re
import json

from core.utils import html_to_text, gen_useragent

CAPTCHA_PATTERN = r'\{[^{]*?"action"\s*:\s*"captcha"\s*,\s*"url"\s*:\s*"([^"]+)"[^{]*?\}'

def is_alibaba_captcha(html_content):
    return bool(re.search(CAPTCHA_PATTERN, html_content))

async def request(query: str, page_number: int = 1, time_range: str = None, category: str = 'general', **kwargs) -> dict:
    time_range_dict = {'day': '4', 'week': '3', 'month': '2', 'year': '1'}

    if category not in ('general', 'images'):
        raise Exception(f"Unsupported category: {category}")

    category_config = {
        'general': {
            'endpoint': 'https://quark.sm.cn/s',
            'params': {
                "q": query,
                "layout": "html",
                "page": page_number,
            },
        },
        'images': {
            'endpoint': 'https://vt.sm.cn/api/pic/list',
            'params': {
                "query": query,
                "limit": 10,
                "start": (page_number - 1) * 10,
            },
        },
    }

    query_params = category_config[category]['params']
    query_url = category_config[category]['endpoint']

    if time_range_dict.get(time_range) and category == 'general':
        query_params["tl_request"] = time_range_dict.get(time_range)

    headers = {
        "User-Agent": gen_useragent(),
    }

    return {'url': f"{query_url}?{urlencode(query_params)}", 'method': 'GET', 'headers': headers}


def _parse_addition(data):
    return {
        "title": html_to_text(data.get('title', {}).get('content')),
        "url": data.get('source', {}).get('url'),
        "content": html_to_text(data.get('summary', {}).get('content')),
    }


def _parse_ai_page(data):
    results = []
    for item in data.get('list', []):
        content = (
            " | ".join(map(str, item.get('content', [])))
            if isinstance(item.get('content'), list)
            else str(item.get('content'))
        )

        try:
            published_date = datetime.fromtimestamp(int(item.get('source', {}).get('time')))
        except (ValueError, TypeError):
            published_date = None

        results.append(
            {
                "title": html_to_text(item.get('title')),
                "url": item.get('url'),
                "content": html_to_text(content),
                "publishedDate": published_date,
            }
        )
    return results


def _parse_baike_sc(data):
    return {
        "title": html_to_text(data.get('data', {}).get('title')),
        "url": data.get('data', {}).get('url'),
        "content": html_to_text(data.get('data', {}).get('abstract')),
        "thumbnail": data.get('data', {}).get('img').replace("http://", "https://"),
    }


def _parse_finance_shuidi(data):
    content = " | ".join(
        (
            info
            for info in [
                data.get('establish_time'),
                data.get('company_status'),
                data.get('controled_type'),
                data.get('company_type'),
                data.get('capital'),
                data.get('address'),
                data.get('business_scope'),
            ]
            if info
        )
    )
    return {
        "title": html_to_text(data.get('company_name')),
        "url": data.get('title_url'),
        "content": html_to_text(content),
    }


def _parse_kk_yidian_all(data):
    content_list = []
    for section in data.get('list_container', []):
        for item in section.get('list_container', []):
            if 'dot_text' in item:
                content_list.append(item['dot_text'])

    return {
        "title": html_to_text(data.get('title')),
        "url": data.get('title_url'),
        "content": html_to_text(' '.join(content_list)),
    }


def _parse_life_show_general_image(data):
    results = []
    for item in data.get('image', []):
        try:
            published_date = datetime.fromtimestamp(int(item.get("publish_time")))
        except (ValueError, TypeError):
            published_date = None

        results.append(
            {
                "url": item.get("imgUrl"),
                "thumbnail_src": item.get("img"),
                "img_src": item.get("bigPicUrl"),
                "title": item.get("title"),
                "source": item.get("site"),
                "resolution": f"{item['width']} x {item['height']}",
                "publishedDate": published_date,
            }
        )
    return results


def _parse_med_struct(data):
    return {
        "title": html_to_text(data.get('title')),
        "url": data.get('message', {}).get('statistics', {}).get('nu'),
        "content": html_to_text(data.get('message', {}).get('content_text')),
        "thumbnail": data.get('message', {}).get('video_img').replace("http://", "https://"),
    }


def _parse_music_new_song(data):
    results = []
    for item in data.get('hit3', []):
        results.append(
            {
                "title": f"{item['song_name']} | {item['song_singer']}",
                "url": item.get("play_url"),
                "content": html_to_text(item.get("lyrics")),
                "thumbnail": item.get("image_url").replace("http://", "https://"),
            }
        )
    return results


def _parse_nature_result(data):
    return {"title": html_to_text(data.get('title')), "url": data.get('url'), "content": html_to_text(data.get('desc'))}


def _parse_news_uchq(data):
    results = []
    for item in data.get('feed', []):
        try:
            published_date = datetime.strptime(item.get('time'), "%Y-%m-%d")
        except (ValueError, TypeError):
            published_date = None

        results.append(
            {
                "title": html_to_text(item.get('title')),
                "url": item.get('url'),
                "content": html_to_text(item.get('summary')),
                "thumbnail": item.get('image').replace("http://", "https://"),
                "publishedDate": published_date,
            }
        )
    return results


def _parse_ss_doc(data):
    published_date = None
    try:
        timestamp = int(data.get('sourceProps', {}).get('time'))
        if timestamp != 0:
            published_date = datetime.fromtimestamp(timestamp)
    except (ValueError, TypeError):
        pass

    try:
        thumbnail = data.get('picListProps', [])[0].get('src').replace("http://", "https://")
    except (ValueError, TypeError, IndexError):
        thumbnail = None

    return {
        "title": html_to_text(
            data.get('titleProps', {}).get('content')
            or data.get('title')
        ),
        "url": data.get('sourceProps', {}).get('dest_url')
        or data.get('normal_url')
        or data.get('url'),
        "content": html_to_text(
            data.get('summaryProps', {}).get('content')
            or data.get('message', {}).get('replyContent')
            or data.get('show_body')
            or data.get('desc')
        ),
        "publishedDate": published_date,
        "thumbnail": thumbnail,
    }


def _parse_ss_note(data):
    try:
        published_date = datetime.fromtimestamp(int(data.get('source', {}).get('time')))
    except (ValueError, TypeError):
        published_date = None

    return {
        "title": html_to_text(data.get('title', {}).get('content')),
        "url": data.get('source', {}).get('dest_url'),
        "content": html_to_text(data.get('summary', {}).get('content')),
        "publishedDate": published_date,
    }


def _parse_travel_dest_overview(data):
    return {
        "title": html_to_text(data.get('strong', {}).get('title')),
        "url": data.get('strong', {}).get('baike_url'),
        "content": html_to_text(data.get('strong', {}).get('baike_text')),
    }


def _parse_travel_ranking_list(data):
    return {
        "title": html_to_text(data.get('title', {}).get('text')),
        "url": data.get('title', {}).get('url'),
        "content": html_to_text(data.get('title', {}).get('title_tag')),
    }


async def parse_response(response_text: str, category: str = 'general', **kwargs) -> list[dict]:
    results = []

    if is_alibaba_captcha(response_text):
        raise Exception("Alibaba CAPTCHA detected. Please try again later.")

    if category == 'images':
        data = json.loads(response_text)
        for item in data.get('data', {}).get('hit', {}).get('imgInfo', {}).get('item', []):
            try:
                published_date = datetime.fromtimestamp(int(item.get("publish_time")))
            except (ValueError, TypeError):
                published_date = None

            results.append(
                {
                    "url": item.get("imgUrl"),
                    "thumbnail_src": item.get("img"),
                    "img_src": item.get("bigPicUrl"),
                    "title": item.get("title"),
                    "source": item.get("site"),
                    "resolution": f"{item['width']} x {item['height']}",
                    "publishedDate": published_date,
                }
            )

    if category == 'general':
        source_category_parsers = {
            'addition': _parse_addition,
            'ai_page': _parse_ai_page,
            'baike_sc': _parse_baike_sc,
            'finance_shuidi': _parse_finance_shuidi,
            'kk_yidian_all': _parse_kk_yidian_all,
            'life_show_general_image': _parse_life_show_general_image,
            'med_struct': _parse_med_struct,
            'music_new_song': _parse_music_new_song,
            'nature_result': _parse_nature_result,
            'news_uchq': _parse_news_uchq,
            'ss_note': _parse_ss_note,
            'ss_doc': _parse_ss_doc,
            'ss_kv': _parse_ss_doc,
            'ss_pic': _parse_ss_doc,
            'ss_text': _parse_ss_doc,
            'ss_video': _parse_ss_doc,
            'baike': _parse_ss_doc,
            'structure_web_novel': _parse_ss_doc,
            'travel_dest_overview': _parse_travel_dest_overview,
            'travel_ranking_list': _parse_travel_ranking_list,
        }

        pattern = r'<script\s+type="application/json"\s+id="s-data-[^"]+"\s+data-used-by="hydrate">(.*?)</script>'
        matches = re.findall(pattern, response_text, re.DOTALL)

        for match in matches:
            data = json.loads(match)
            initial_data = data.get('data', {}).get('initialData', {})
            extra_data = data.get('extraData', {})

            source_category = extra_data.get('sc')

            parsers = source_category_parsers.get(source_category)
            if parsers:
                parsed_results = parsers(initial_data)
                if isinstance(parsed_results, list):
                    results.extend(parsed_results)
                else:
                    results.append(parsed_results)

    return results


