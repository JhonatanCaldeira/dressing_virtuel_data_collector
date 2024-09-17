import scrapy
from image_scraper.items import ImageScraperItem

class ImagesSpider(scrapy.Spider):
    name = "images"
    start_urls = ['http://localhost:8000/']

    def parse(self, response):
        for image in response.css('div.image-card'):

            item = ImageScraperItem()
            item['category'] = image.css('p::text').get() 
            relative_image = image.css('img::attr(src)').get()
            item['image_urls'] =  [response.urljoin(relative_image)]

            yield item

        # Paginação
        next_page = response.css('a[href*="?page="]::attr(href)').getall()
        for link in next_page:
            if 'page=' in link:
                yield response.follow(link, self.parse)
