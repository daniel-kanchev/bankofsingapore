import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankofsingapore.items import Article
import requests
import json


class bankofsingaporeSpider(scrapy.Spider):
    name = 'bankofsingapore'
    start_urls = ['https://www.bankofsingapore.com/media-listing.html']

    def parse(self, response):
        json_response = json.loads(requests.get("https://www.bankofsingapore.com/managed-resources/json/page-media-sg-en.json").text)
        articles = json_response
        for article in articles:
            link = response.urljoin(article['page'])
            date = article['publish_date']
            title = article['title']
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date, title=title))

    def parse_article(self, response, date, title):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        content = response.xpath('//div[@class="ds-article__article"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
