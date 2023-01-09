import scrapy
import json
import re


class SearchSpider(scrapy.Spider):
    name = "search"
    # by newest
    # url_base = 'https://www.hemnet.se/bostader?by=creation&order=desc&'
    url_base = 'https://www.hemnet.se/bostader?by=creation&order=desc&'

    def start_requests(self):
        yield scrapy.Request(url=self.url_base,
                             callback=self.parse)

    def parse(self, response):
        dl_line = response.css('script').re_first(
            r'dataLayer = \[{"page":{"type":"standard"}}.*?\].+')
        if dl_line:
            matched_str = re.findall(r'\[.*\]', dl_line)[0]
            if matched_str:
                payload = json.loads(matched_str)[2].get('results')
                if payload:
                    results = payload.get('product_features')
                    for result in results:
                        listing_id = result.get('id')
                        upgrade_url = f'https://www.hemnet.se/saljkollen/{listing_id}'
                        yield scrapy.Request(url=upgrade_url,
                                                callback=self.parse_upgrade_page)
                        listing_url = f'https://www.hemnet.se/bostad/{listing_id}'
                        yield scrapy.Request(url=listing_url,
                                             callback=self.parse_listing_page)
                    page_index = payload.get('page_index')
                    page_total = payload.get('page_total')
                    if page_index != page_total:
                        next_url = self.url_base + f'page={page_index + 1}'
                        yield response.follow(next_url, self.parse)

    def parse_upgrade_page(self, response):
        dl_line = response.css('script').re_first(
            r'dataLayer = \[{"page":{"type":"standard"}}.*?\].+')
        if dl_line:
            matched_str = re.findall(r'\[.*\]', dl_line)[0]
            if matched_str:
                payload = json.loads(matched_str)
                if payload:
                    property_detail = payload[2].get('property')
                    listing_id = property_detail.get('id')
                    listing_publication_date = property_detail.get('publication_date')
                    for payload in response.css('div.js-sellers-page-react-root'):
                        details = json.loads(payload.attrib['data-initial-data'])
                        if details:
                            raketen = details.get('toplistingOffering')
                            plus = details.get('packageOfferings').get('plusOffering')
                            premium = details.get('packageOfferings').get('premiumOffering')
                            yield {
                                'listing_id': listing_id,
                                'publication_date' : listing_publication_date,
                                'raketen': raketen,
                                'plus': plus,
                                'premium': premium,
                                'data_type': 'upgrade_price'
                            }

    def parse_listing_page(self, response):
        dl_line = response.css('script').re_first(
            r'dataLayer = \[{"page":{"type":"standard"}}.*?\].+')
        if dl_line:
            matched_str = re.findall(r'\[.*\]', dl_line)[0]
            if matched_str:
                payload = json.loads(matched_str)
                if payload:
                    property_detail = payload[2].get('property')
                    listing_id = property_detail.get('id')
                    listing_package_type = property_detail.get(
                        'listing_package_type')
                    ask_price = property_detail.get('price')
                    listing_status = property_detail.get('status')
                    yield {
                        'listing_id': listing_id,
                        'listing_package_type': listing_package_type,
                        'ask_price': ask_price,
                        'listing_status': listing_status,
                        'data_type': 'listing'
                    }
