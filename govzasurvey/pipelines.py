from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from .models import Scrape, Page, PageObservation, File, FileObservation
from .items import PageItem, FileItem
import hashlib


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
