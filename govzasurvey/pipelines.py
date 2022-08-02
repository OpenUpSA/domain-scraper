from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from govzasurvey.models import Scrape, Page, PageObservation, File, FileObservation


class ArchivePipeline(object):
    def __init__(self, database_url):
        self.database_url = database_url

    @classmethod
    def from_crawler(cls, crawler):
        database_url = crawler.settings['DATABASE_URL']
        return cls(database_url=database_url)

    def open_spider(self, spider):
        self.engine = create_engine(self.database_url)

        session = Session(self.engine)
        self.scrape = Scrape()
        session.add(self.scrape)
        session.commit()
        session.close()

    def close_spider(self, spider):
        self.engine.dispose()

    def process_item(self, item, spider):
        return item
