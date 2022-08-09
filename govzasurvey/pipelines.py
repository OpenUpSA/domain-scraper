from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from .models import Scrape, Page, PageObservation, File, FileObservation
from .items import PageItem, FileItem
import hashlib
from scrapy.pipelines.files import FilesPipeline
from scrapy.http import Request
import logging
from scrapy.pipelines.media import MediaPipeline
from urllib.parse import urlparse
from os.path import splitext
import cgi

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


def get_content_disposition_unsafe_filename(response):
    content_disposition = response.headers["content-disposition"]
    if content_disposition:
        value, params = cgi.parse_header(content_disposition)
        if "filename" in params:
            return params["filename"]
    return None

def make_key(sha256, content_disposition_unsafe_filename, url):
    if content_disposition_unsafe_filename:
        path, ext = splitext(content_disposition_unsafe_filename)
        if ext:
            return sha256 + ext

    parsed = urlparse(url)
    path, ext = splitext(parsed.path)
    if ext:
        return sha256 + ext

    return sha256


class FilePipeline(MediaPipeline):
    def __init__(self, database_url, s3_bucket_name, aws_key_id, aws_key_secret):
        self.database_url = database_url
        self.download_func = None  # A MediaPipeline expected attribute
        self.handle_httpstatus_list = None  # A MediaPipeline expected attribute
        self.s3_bucket_name = s3_bucket_name
        self.aws_key_id = aws_key_id
        self.aws_key_secret = aws_key_secret

    @classmethod
    def from_crawler(cls, crawler):
        cls.crawler = crawler  # a MediaPipeline expectation
        database_url = crawler.settings["DATABASE_URL"]
        return cls(
            database_url=database_url,
            s3_bucket_name=crawler.settings.get("S3_BUCKET_NAME"),
            aws_key_id=crawler.settings.get("AWS_KEY_ID"),
            aws_key_secret=crawler.settings.get("AWS_KEY_SECRET"),
        )

    def open_spider(self, spider, *args, **kwargs):
        self.engine = create_engine(self.database_url)
        return super().open_spider(spider, *args, **kwargs)

    def close_spider(self, spider):
        self.engine.dispose()

    def seen_this_scrape(self, session, url):
        return (
            session.query(FileObservation)
            .filter(FileObservation.url == url, FileObservation.scrape == self.scrape)
            .one_or_none()
        )

    def latest_observation(self, session, url):
        return (
            session.query(FileObservation)
            .filter(FileObservation.url == url)
            .order_by(FileObservation.created_at.desc())
            .first()
        )

    def get_media_requests(self, item, info):
        if isinstance(item, FileItem):
            with Session(self.engine) as session:
                headers = {}

                if not self.seen_this_scrape(item["url"]):
                    latest_observation = self.latest_observation(item["url"])
                    if latest_observation:
                        if latest_observation.etag:
                            headers["If-None-Match"] = latest_observation.etag

                    return [Request(item["url"], headers=headers)]
                else:
                    logger.debug(f'Skipping {item["url"]} already seen this scrape')
        return []

    def get_file_record(self, sha256):
        return session.query(File).filter(File.sha256 == sha256).one_or_none()

    def upload_file(self, key, content, content_type):
        self.s3.put_object(
            ACL="public-read",
            Key=key,
            Bucket=self.s3_bucket_name,
            ContentType=content_type,
            Body=BytesIO(content),
        )

    def media_downloaded(self, response, request, info, item=None):
        content_disposition_unsafe_filename = get_content_disposition_unsafe_filename(
            response
        )

        try:
            with Session(self.engine) as session:

                if response.status == 304:
                    logger.info("%s already exists and is up to date", key_str)
                elif response.status == 200:
                    file_sha256 = hashlib.sha256()
                    file_sha256.update(response.body)
                    file_sha256_digest = file_sha256.hexdigest()

                    file_record = self.get_file_record(file_sha256_digest)

                    if not file_record:
                        content_type = response.headers["content-type"].decode("utf-8")
                        key = make_key(
                            file_sha256_digest,
                            content_disposition_unsafe_filename,
                            item["url"],
                        )
                        self.upload_file(key, response.body, content_type)
                        file_record = File(
                            content_type=content_type,
                            sha256=file_sha256_digest,
                            key=key,
                        )
                        session.add(file_record)

                file_observation = FileObservation(
                    scrape=self.scrape,
                    file=file_record,
                    url=item["url"],
                    referrer=item["referrer"],
                    etag=etag,
                    content_disposition_unsafe_filename=content_disposition_unsafe_filename,
                )
                session.add(file_observation)

        except Exception as e:
            logger.exception(f"e", exc_info=True)
            raise e
