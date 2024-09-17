# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from itemadapter import ItemAdapter
import sqlite3
import os
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem

class ImageDownload(ImagesPipeline):
    """
    Pipeline for downloading images and storing metadata in a SQLite database.

    Inherits from:
        ImagesPipeline: Scrapy's built-in pipeline for handling image downloads.
    """
    def get_media_requests(self, item, info):
        """
        Generates requests for downloading images.

        Args:
            item (dict): The item containing image URLs.
            info (scrapy.utils.project.Info): Information about the spider.

        Yields:
            scrapy.Request: Requests for downloading images.
        """
        for image_url in item.get('image_urls', []):
            yield Request(image_url)

    def item_completed(self, results, item, info):
        """
        Called when the image download is completed. Stores image metadata in the database.

        Args:
            results (list): Results of the image download.
            item (dict): The item containing image data.
            info (scrapy.utils.project.Info): Information about the spider.

        Returns:
            dict: The item containing image data.

        Raises:
            DropItem: If image download fails.
        """
        if not results or not any(x[0] for x in results):
            raise DropItem("Image download failure")
        
        # Get the path of the downloaded image
        image_paths = [x["path"] for ok, x in results if ok]

        self.connection = sqlite3.connect('images_data.db')
        self.cursor = self.connection.cursor()

        # Store image metadata in the SQLite database
        self.cursor.execute('''
            INSERT INTO images_data (category, image_url, image_path) VALUES (?, ?, ?)
        ''', (item.get('category'), item.get('image_urls')[0], image_paths[0]))
        self.connection.commit()
        self.connection.close()

        return item

class ImageScraperPipeline():
    """
    Pipeline for initializing and closing the SQLite database connection.
    """
    def open_spider(self, spider):
        """
        Initializes the SQLite database connection and creates the table if it does not exist.

        Args:
            spider (scrapy.spiders.Spider): The spider instance.
        """
        self.connection = sqlite3.connect('images_data.db')
        self.cursor = self.connection.cursor()

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
        """
        Closes the SQLite database connection when the spider is closed.

        Args:
            spider (scrapy.spiders.Spider): The spider instance.
        """
        self.connection.close()

    def process_item(self, item, spider):
        """
        Processes each item (no specific action in this case).

        Args:
            item (dict): The item to process.
            spider (scrapy.spiders.Spider): The spider instance.

        Returns:
            dict: The processed item.
        """
        return item