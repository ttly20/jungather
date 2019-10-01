# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient 

class JungatherPipeline(object):

    def __init__(self):
        self.connect = MongoClient("mongodb://localhost:27017/")
        self.db = self.connect["videos"]
        self.video = self.db.video

    def process_item(self, item, spider):
        self.video.update({"title": item["title"]}, {"$set": item}, True)
        return item

