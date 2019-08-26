# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class JungatherItem(Item):
    # define the fields for your item here like:
    # name = Field()
    title = Field()
    poster = Field()
    status = Field()
    alias = Field()
    director = Field()
    actor = Field()
    videotype = Field()
    area = Field()
    language = Field()
    length = Field()
    update = Field()
    released = Field()
    plot = Field()
    plays = Field()
    downloads = Field()
