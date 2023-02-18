import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
import datetime

class AllAloHouses(CrawlSpider):
    name = 'alo'
    allowed_domains = ['www.alo.bg']
    start_urls = ['https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/']

    rules = (
        Rule(LinkExtractor(allow='byregion')),
        Rule(LinkExtractor(allow='location_ids'), callback='parse')
    )

    custom_settings = {
        "DOWNLOAD_DELAY": 5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2
    }

    def parse(self, response, **kwargs):

        #The code below is needed due to 429 error
        delay = self.crawler.engine.downloader.slots["www.alo.bg"].delay
        concurrency = self.crawler.engine.downloader.slots["www.alo.bg"].concurrency
        self.log("Delay {}, concurrency {} for request {}".format(delay, concurrency, response.request))

        imoti_list_urls = response.css('div.listvip-item-header a::attr(href)').getall()
        for imot_url in imoti_list_urls:
            url = response.urljoin(imot_url)
            yield scrapy.Request(url=url, callback=self.parse_estate)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        next_page = response.urljoin(next_page)

        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_estate(self, response):

        location = response.css("div [style='font-size:16px;']::text").getall()

        #get the additional information, given by real estate agents and sellers in the form of text
        text_info = response.css('p.word-break-all.highlightable::text').getall()

        # Sometimes the information about house`s price is missing, so it is not useful. It is a condition for going forward
        #Price usually contains "\xa0"
        price = response.css('div.ads-params-price::text').get()

        if "\xa0" in price:
            price = price.replace("\xa0", "")
            if "EUR" in price:
                price = price.replace("EUR", "")

            # In some cases part of the the data below is missing (usually floors)
            params = response.css('span.ads-params-single::text').getall()
            if len(params) == 3:
                floors, size, yard = params
                if "\xa0кв.м РЗП" in size:
                    size = size.replace("\xa0кв.м РЗП", "")
                if "\xa0кв.м двор" in yard:
                    yard = yard.replace("\xa0кв.м двор", "")
            else:
                size = 0
                yard = 0
                floors = "?"
                for parameter in params:
                    if "\xa0кв.м РЗП" in parameter:
                        size = parameter.replace("\xa0кв.м РЗП", "")
                    elif "\xa0кв.м двор" in parameter:
                        yard = parameter.replace("\xa0кв.м двор", "")
                    else:
                        floors = parameter

            # Many houses have additional benefits
            advantages = {"sewerage": '?', "power": "?", "water_supply": "?", "garage": "no", "view": "no", "detached_house": "no", "bbq_gazebo": "no", "heating_system": "no", "pool": "no", "gated_community": "no", "water_well": "no", "solar_panels": "no", "fireplace": "no"}
            pros = response.css('span.ads-params-multi::text').getall()
            if 'Канализация' in pros:
                advantages["sewerage"] = 'yes'
            if 'Ток' in pros:
                advantages["power"] = "yes"
            if 'Вода' in pros:
                advantages["water_supply"] = "yes"
            if 'Гараж' in pros:
                advantages["garage"] = "yes"
            if 'Панорама' in pros or 'Панорамна' in pros or 'Гледка' in pros:
                advantages["view"] = "yes"
            if 'Самостоятелна' in pros:
                advantages["detached_house"] = "yes"
            if "Барбекю" in pros or "Беседка" in pros:
                advantages["bbq_gazebo"] = "yes"
            if "Локално отопление" in pros:
                advantages["heating_system"] = 'yes'
            if "Басейн" in pros:
                advantages["pool"] = "yes"
            if "В затворен комплекс" in pros:
                advantages["gated_community"] = "yes"
            if "Кладенец" in pros:
                advantages["water_well"] = "yes"
            if "Слънчеви колектори" in pros:
                advantages["solar_panels"] = "yes"
            if "Камина" in pros:
                advantages["fireplace"] = "yes"


            yield {
                'location': location,
                'price': price,
                'floors': floors,
                'size': size,
                'yard': yard,
                'sewerage': advantages["sewerage"],
                'power': advantages["power"],
                'water_supply': advantages["water_supply"],
                'garage': advantages["garage"],
                'view': advantages["view"],
                'detached_house': advantages["detached_house"],
                'bbq_gazebo': advantages["bbq_gazebo"],
                'heating_system': advantages["heating_system"],
                'pool': advantages["pool"],
                'gated_community': advantages["gated_community"],
                'water_well': advantages["water_well"],
                'solar_panels': advantages["solar_panels"],
                'fireplace': advantages["fireplace"],
                'text': text_info,
                'url': response.url
            }

x = datetime.datetime.now()
file_path = f"alo_{x.strftime('%H-%M_%d_%B_%Y')}.csv"

process = CrawlerProcess(settings={
    "FEEDS": {
        file_path: {"format": "csv"},
    },
})

process.crawl(AllAloHouses)
process.start()