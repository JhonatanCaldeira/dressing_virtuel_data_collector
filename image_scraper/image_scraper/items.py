# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ImageScraperItem(scrapy.Item):
    """
    Defines the fields for the items scraped by the ImageScraper spider.

    Fields:
        image_urls (list of str): List of image URLs to be downloaded.
        images (list of dict): List of dictionaries containing image download details.
        category (str): Category of the image.
        image_path (str): File path where the image is saved.
    """
    # URL image fields
    image_urls = scrapy.Field()
    images = scrapy.Field()

    # Category and Path fields
    category = scrapy.Field()
    image_path = scrapy.Field()
