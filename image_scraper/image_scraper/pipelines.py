# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
import os
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem

class ImageDownload(ImagesPipeline):
    def get_media_requests(self, item, info):
        # Download images
        for image_url in item.get('image_urls', []):
            yield Request(image_url)

    def item_completed(self, results, item, info):
        # Check if the download was completed
        if not results or not any(x[0] for x in results):
            raise DropItem("Image download failure")
        
        # Obtém o caminho da imagem
        image_paths = [x["path"] for ok, x in results if ok]

        self.connection = sqlite3.connect('images_data.db')
        self.cursor = self.connection.cursor()

        # Add image in the DB
        self.cursor.execute('''
            INSERT INTO images_data (category, image_url, image_path) VALUES (?, ?, ?)
        ''', (item.get('category'), item.get('image_urls')[0], image_paths[0]))
        self.connection.commit()
        self.connection.close()

        return item

class ImageScraperPipeline():

    def open_spider(self, spider):
        # SQLite Connection
        self.connection = sqlite3.connect('images_data.db')
        self.cursor = self.connection.cursor()

        # Table Creation
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS images_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                image_url TEXT,
                image_path TEXT
            )
        ''')
        self.connection.commit()

    def close_spider(self, spider):
        # Close DB Connection
        self.connection.close()

    def process_item(self, item, spider):
        return item