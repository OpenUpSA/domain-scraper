from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from .models import Scrape, Page, PageObservation, File, FileObservation
from .items import PageItem, FileItem
import hashlib
from scrapy.pipelines.files import FilesPipeline
from scrapy.http import Request
import logging
from scrapy.pipelines.media import MediaPipeline


logger = logging.getLogger(__name__)


class PagePipeline(object):
    def __init__(self, database_url):
        self.database_url = database_url

    @classmethod
    def from_crawler(cls, crawler):
        database_url = crawler.settings["DATABASE_URL"]
        return cls(database_url=database_url)

    def open_spider(self, spider):
        self.engine = create_engine(self.database_url)

    def close_spider(self, spider):
        self.engine.dispose()

    def process_item(self, item, spider):
        if isinstance(item, PageItem):
            return self.process_page_item(item, spider)

        return item

    def process_page_item(self, item, spider):
            item["html"] = item["html"].replace("\x00", "")

            page_sha256 = hashlib.sha256()
            page_sha256.update(item["html"].encode("utf-8"))
            page_sha256_digest = page_sha256.hexdigest()

            with Session(self.engine) as session:
                page = (
                    session.query(Page)
                    .filter(Page.sha256 == page_sha256_digest)
                    .one_or_none()
                )
                if not page:
                    page = Page(html=item["html"], sha256=page_sha256_digest)
                    session.add(page)
                observation = PageObservation(
                    scrape=spider.scrape,
                    page=page,
                    url=item["url"],
                    referrer=item["referrer"],
                    etag=item["etag"],
                )
                session.add(observation)
                session.commit()

            return item


class FilePipeline(MediaPipeline):
    def __init__(self, database_url):
        self.database_url = database_url
        self.download_func = None  # A MediaPipeline expected attribute
        self.handle_httpstatus_list = None  # A MediaPipeline expected attribute

    @classmethod
    def from_crawler(cls, crawler):
        cls.crawler = crawler # a MediaPipeline expectation
        database_url = crawler.settings["DATABASE_URL"]
        return cls(database_url=database_url)

    def open_spider(self, spider, *args, **kwargs):
        self.engine = create_engine(self.database_url)
        return super().open_spider(spider, *args, **kwargs)

    def close_spider(self, spider):
        self.engine.dispose()

    def get_media_requests(self, item, info):
        if isinstance(item, FileItem):
            with Session(self.engine) as session:
                headers = {}

                latest_observation = (
                    session.query(FileObservation)
                    .filter(FileObservation.url == item["url"])
                    .order_by(FileObservation.created_at.desc())
                    .first()
                )
                if latest_observation:
                    if latest_observation.etag:
                        headers['If-None-Match'] = latest_observation.etag

                return [Request(item['url'], headers=headers)]

        return []

    def media_downloaded(self, response, request, info, item=None):
        if response.status == 304:
            logger.info("%s already exists and is up to date", key_str)
        elif response.status == 200:
            logger.info(f"Uploading {item['path']}")
            content_type = response.headers['content-type'].decode("utf-8")
            print(item["url"], content_type)
