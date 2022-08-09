# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PageItem(scrapy.Item):
    url = scrapy.Field()
    referrer = scrapy.Field()
    etag = scrapy.Field()
    html = scrapy.Field()
    scrape_timestamp = scrapy.Field()


class RobotsTXTItem(scrapy.Item):
    url = scrapy.Field()
    robotstxt = scrapy.Field()


class NetlocItem(scrapy.Item):
    netloc = scrapy.Field()


class FileItem(scrapy.Item):
    url = scrapy.Field()
    label = scrapy.Field()
    path = scrapy.Field()
