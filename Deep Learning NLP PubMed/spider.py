import pandas as pd
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
import datetime
import json


remedies_table = pd.read_csv("data/natural_health.csv")
remedies_list = list(remedies_table.iloc[:, 0])
illn = 'dermatitis'

class PubMedArticles(CrawlSpider):
    name = 'pubmed'
    allowed_domains = ['pubmed.ncbi.nlm.nih.gov']
    start_urls = ['https://pubmed.ncbi.nlm.nih.gov']

    custom_settings = {
        "DOWNLOAD_DELAY": 5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2
    }

    def start_requests(self):

        queries = remedies_list


        for query in queries:
            url = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + query + '+' + illn
            # try:
            yield scrapy.Request(url=url, callback=self.parse, meta={'query':query})
            # except:
            #     continue

    def parse(self, response):

        if not response.css('.query-error-message').getall():
            if not response.css('.no-results-query').getall():

                query = response.meta['query']

                articles_list_urls = response.css('.docsum-content a::attr(href)').getall()
                if articles_list_urls:
                    for article_url in articles_list_urls:
                    # url = response.urljoin(article_url)
                        url = 'https://pubmed.ncbi.nlm.nih.gov' + article_url
                        yield scrapy.Request(url=url, callback=self.parse_article, meta={'query':query})

                    next_page = response.css(".results-chunk::attr(data-next-page-url)").getall()
                    if next_page:
                        next_page = next_page[0][5:]
                        # next_page = response.urljoin(next_page)
                        next_page = 'https://pubmed.ncbi.nlm.nih.gov' + next_page
                        yield scrapy.Request(url=next_page, callback=self.parse, meta={'query':query})


    def parse_article(self, response):

        quer = response.meta['query']

        title = response.css('title::text').get()
        article_id = response.css(".article-page::attr(data-article-pmid)").get()
        texts_list = response.css('.abstract p::text').getall()
        text = ' '.join(texts_list).lower().strip()
        if quer.lower().strip() in text:
            yield {
                'title': title,
                'article_id': article_id,
                'text': text,
                'query': quer
            }

x = datetime.datetime.now()
file_path = f"pubmed_{x.strftime('%H-%M_%d_%B_%Y')}.csv"

process = CrawlerProcess(settings={
    "FEEDS": {
        file_path: {"format": "csv"},
    },
})

process.crawl(PubMedArticles)
process.start()