from govzasurvey.spiders.govza import GovzaSpider
from govzasurvey.models import Scrape
from scrapy.http import Request, HtmlResponse

def mock_response(url, body):
    meta = {"source": ""}
    request = Request(url, meta=meta)

    headers = dict()
    return HtmlResponse(
        url,
        status=200,
        headers=headers,
        body=body,
        encoding="utf-8",
        request=request,
    )


def test_recursive_relative_paths():
    """
    When a link (<a>) has a relative URL, and occurs with the same path on each
    page of the site (e.g. in the footer or nav), even when the page is in a 
    subdirectory of the site, that subdirectory recursively becomes part of the
    link, and crawling can become infinite. This only works when routing in the
    site behaves as though these nested paths exist (i.e. serve a 200 response status).

    e.g. https://www.umngeni.gov.za/ links to 
    "mngeni/documents.php?category=Public%20Notices&sub=Tarrifs"

    https://www.umngeni.gov.za/mngeni/documents.php?category=Public%20Notices&sub=Tarrifs"
    links to "mngeni/documents.php?category=Public%20Notices&sub=Tarrifs"
    which when qualified to be absolute, becomes
    https://www.umngeni.gov.za/mngeni/mngeni/documents.php?category=Public%20Notices&sub=Tarrifs
    
    
    This is a problem for trying to crawl a site comprehensively, because
    it makes it appear as though there are many more pages than there
    actually are.
    
    There are many more sites than just umngeni where this occurs.
    """
    url = "https://www.umngeni.gov.za/mngeni/documents.php?category=Public%20Notices&sub=Tarrifs"
    with open("tests/test_spider_files/recursive_relative_paths_mngeni.html") as body_file:
        response = mock_response(url, body_file.read())

        spider = GovzaSpider(Scrape(), 1)

        for item in spider.parse(response):
            if type(item) == Request:
                assert "/mngeni/mngeni/" not in item.url 
