
from datetime import datetime

from lxml import etree
from lxml.etree import XPath


async def request(query: str, page_number: int = 1, **kwargs) -> dict:
    number_of_results = 10
    offset = (page_number - 1) * number_of_results

    base_url = (
        'https://export.arxiv.org/api/query?search_query=all:' + '{query}&start={offset}&max_results={number_of_results}'
    )

    string_args = {'query': query, 'offset': offset, 'number_of_results': number_of_results}

    return {'url': base_url.format(**string_args), 'method': 'GET'}


async def parse_response(response_text: str, **kwargs) -> list[dict]:
    results = []
    try:
        dom = etree.fromstring(response_text.encode('utf-8'))
    except etree.XMLSyntaxError as e:
        print(f"XML parsing error for Arxiv: {e}")
        return []

    arxiv_namespaces = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    for entry in dom.xpath('//atom:entry', namespaces=arxiv_namespaces):
        title_element = entry.xpath('.//atom:title', namespaces=arxiv_namespaces)
        title = title_element[0].text if title_element else None

        url_element = entry.xpath('.//atom:id', namespaces=arxiv_namespaces)
        url = url_element[0].text if url_element else None

        abstract_element = entry.xpath('.//atom:summary', namespaces=arxiv_namespaces)
        abstract = abstract_element[0].text if abstract_element else None

        authors = [author.text for author in entry.xpath('.//atom:author/atom:name', namespaces=arxiv_namespaces)]

        doi_element = entry.xpath('.//arxiv:doi', namespaces=arxiv_namespaces)
        doi = doi_element[0].text if doi_element else None

        pdf_element = entry.xpath('.//atom:link[@title="pdf"]', namespaces=arxiv_namespaces)
        pdf_url = pdf_element[0].attrib.get('href') if pdf_element else None

        journal_element = entry.xpath('.//arxiv:journal_ref', namespaces=arxiv_namespaces)
        journal = journal_element[0].text if journal_element else None

        tag_elements = entry.xpath('.//atom:category/@term', namespaces=arxiv_namespaces)
        tags = [str(tag) for tag in tag_elements]

        comments_elements = entry.xpath('./arxiv:comment', namespaces=arxiv_namespaces)
        comments = comments_elements[0].text if comments_elements else None

        published_date_element = entry.xpath('.//atom:published', namespaces=arxiv_namespaces)
        publishedDate = None
        if published_date_element and published_date_element[0].text:
            publishedDate = datetime.strptime(published_date_element[0].text, '%Y-%m-%dT%H:%M:%SZ')

        res_dict = {
            'url': url,
            'title': title,
            'publishedDate': publishedDate,
            'content': abstract,
            'doi': doi,
            'authors': authors,
            'journal': journal,
            'tags': tags,
            'comments': comments,
            'pdf_url': pdf_url,
        }

        results.append(res_dict)

    return results


