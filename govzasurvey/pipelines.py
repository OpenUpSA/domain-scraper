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
import boto3
from io import BytesIO

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


def get_response_header_str(response, name):
    value_bytes = response.headers.get(name, None)
    if value_bytes:
        return value_bytes.decode("utf-8")
    else:
        return None


def get_content_disposition_unsafe_filename(response):
    content_disposition = get_response_header_str(response, "content-disposition")
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
    def __init__(
        self, database_url, s3_bucket_name, aws_key_id, aws_key_secret, s3_endpoint_url
    ):
        self.database_url = database_url
        self.download_func = None  # A MediaPipeline expected attribute
        self.handle_httpstatus_list = None  # A MediaPipeline expected attribute
        self.s3_bucket_name = s3_bucket_name
        self.aws_key_id = aws_key_id
        self.aws_key_secret = aws_key_secret
        self.s3_endpoint_url = s3_endpoint_url

    @classmethod
    def from_crawler(cls, crawler):
        cls.crawler = crawler  # a MediaPipeline expectation
        database_url = crawler.settings["DATABASE_URL"]
        return cls(
            database_url=database_url,
            s3_bucket_name=crawler.settings.get("AWS_S3_BUCKET_NAME"),
            aws_key_id=crawler.settings.get("AWS_ACCESS_KEY_ID"),
            aws_key_secret=crawler.settings.get("AWS_SECRET_ACCESS_KEY"),
            s3_endpoint_url=crawler.settings.get("AWS_S3_ENDPOINT_URL"),
        )

    def open_spider(self, spider, *args, **kwargs):
        self.engine = create_engine(self.database_url)
        self.spider = spider
        self.s3 = boto3.client(
            "s3",
            endpoint_url=self.s3_endpoint_url,
            region_name="eu-west-1",
            aws_access_key_id=self.aws_key_id,
            aws_secret_access_key=self.aws_key_secret,
        )
        return super().open_spider(spider, *args, **kwargs)

    def close_spider(self, spider):
        self.engine.dispose()

    def seen_this_scrape(self, session, url):
        return (
            session.query(FileObservation)
            .filter(
                FileObservation.url == url,
                FileObservation.scrape_id == self.spider.scrape_id,
            )
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
        try:
            if isinstance(item, FileItem):
                with Session(self.engine) as session:
                    headers = {}
                    meta = {}

                    if not self.seen_this_scrape(session, item["url"]):
                        latest_observation = self.latest_observation(
                            session, item["url"]
                        )
                        if latest_observation:
                            meta["file"] = latest_observation.file
                            # the scrapy cache seems to be interfering with our etag/if-none-match
                            # submission and we don't need to cache it when using if-none-match
                            # with the etag in the archive anyway
                            if latest_observation.etag:
                                headers["if-none-match"] = latest_observation.etag
                                meta["dont_cache"] = True
                            if latest_observation.last_modified:
                                headers["if-modified-since"] = latest_observation.last_modified
                                meta["dont_cache"] = True
                            logger.debug(f"Requsting {item['url']} {headers}")
                        return [Request(item["url"], headers=headers, meta=meta)]
                    else:
                        logger.debug(f'Skipping {item["url"]} already seen this scrape')
            return []
        except Exception as e:
            logger.exception(f"e", exc_info=True)
            raise e

    def get_file_record(self, session, sha256):
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
        try:
            content_disposition_unsafe_filename = (
                get_content_disposition_unsafe_filename(response)
            )

            with Session(self.engine) as session:
                file_record = None
                etag = None
                last_modified = None

                if response.status == 304:
                    logger.debug("%s already exists and is UP TO DATE", request.url)
                    etag = request.headers.get("if-none-match", None)
                    las_modified = request.headers.get("if-modified-since", None)
                    file_record = response.meta["file"]
                elif response.status == 200:
                    logger.debug("%s didnt exist yet or was NOT up to date", request.url)
                    file_sha256 = hashlib.sha256()
                    file_sha256.update(response.body)
                    file_sha256_digest = file_sha256.hexdigest()

                    file_record = self.get_file_record(session, file_sha256_digest)

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

                etag = get_response_header_str(response, "etag")
                last_modified = get_response_header_str(response, "last-modified")

                file_observation = FileObservation(
                    scrape=self.spider.scrape,
                    file=file_record,
                    url=item["url"],
                    referrer=item["referrer"],
                    etag=etag,
                    last_modified=last_modified,
                    content_disposition_unsafe_filename=content_disposition_unsafe_filename,
                )
                session.add(file_observation)
                session.commit()

        except Exception as e:
            logger.exception(f"e", exc_info=True)
            raise e
