import scrapy
from image_scraper.items import ImageScraperItem

class ImagesSpider(scrapy.Spider):
    name = "images"
    start_urls = ['http://localhost:8000/']

    def parse(self, response):
        """
        Parses the response from the start URLs to extract image data.

        Args:
            response (scrapy.http.Response): The response object containing the HTML of the page.
        
        Yields:
            ImageScraperItem: An item containing image data including category and image URL.
        """
        for image in response.css('div.image-card'):

            item = ImageScraperItem()
            item['category'] = image.css('p::text').get() 
            relative_image = image.css('img::attr(src)').get() 
            item['image_urls'] =  [response.urljoin(relative_image)] 

            yield item

        # Pagination
        # Extracts and follows pagination links to scrape multiple pages
        next_page = response.css('a[href*="?page="]::attr(href)').getall()
        for link in next_page:
            if 'page=' in link:
                yield response.follow(link, self.parse)
