# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GovzasurveyItem(scrapy.Item):
    url = scrapy.Field()
    has_wordpress = scrapy.Field()


class RobotsTXTItem(scrapy.Item):
    url = scrapy.Field()
    robotstxt = scrapy.Field()
