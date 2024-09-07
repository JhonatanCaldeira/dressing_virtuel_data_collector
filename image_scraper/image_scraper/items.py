# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ImageScraperItem(scrapy.Item):
    # URL image fields
    image_urls = scrapy.Field()
    images = scrapy.Field()

    # Category and Path fields
    category = scrapy.Field()
    image_path = scrapy.Field()
