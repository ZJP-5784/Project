# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# class AmazonpagePipeline:
#     def process_item(self, item, spider):
#         print(f'item:',item)
#         # return item


import pymongo
from amazonpage.items import AsinItem


class MongoDBPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        cls.connection_string = crawler.settings.get('MONGODB_CONNECTION_STRING')
        cls.database = crawler.settings.get('MONGODB_DATABASE')
        cls.collection = crawler.settings.get('MONGODB_COLLECTION')
        return cls()

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.connection_string)
        self.db = self.client[self.database]

    def process_item(self, item, spider):
        self.db[self.collection].update_one({
            'asin': item['asin']
        }, {
            '$set': dict(item)
        }, upsert=True)

    def close_spider(self, spider):
        self.client.close()
