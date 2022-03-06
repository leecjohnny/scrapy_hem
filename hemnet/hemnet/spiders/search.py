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
                payload = json.loads(matched_str)[1].get('results')
                if payload:
                    results = payload.get('product_features')
                    for result in results:
                        listing_id = result.get('id')
                        upgrade_types = ['plus', 'premium']
                        for upgrades in upgrade_types:
                            upgrade_url = f'https://www.hemnet.se/betalning/{listing_id}/{upgrades}-uppgradering'
                            yield scrapy.Request(url=upgrade_url,
                                                 callback=self.parse_upgrade_pages)
                        listing_url = f'https://www.hemnet.se/bostad/{listing_id}'
                        yield scrapy.Request(url=listing_url,
                                             callback=self.parse_listing_page)
                    page_index = payload.get('page_index')
                    page_total = payload.get('page_total')
                    if page_index != page_total:
                        next_url = self.url_base + f'page={page_index + 1}'
                        yield response.follow(next_url, self.parse)

    def parse_upgrade_pages(self, response):
        for payload in response.css('div.js-checkout-klarna-react-root'):
            details = json.loads(payload.attrib['data-initial-data'])
            if details:
                listing = details.get('listing')
                listing_id = int(listing.get('id'))
                offer = details.get('availableOffers')[0]
                offer_name = offer.get('name')
                offer_price = offer.get('price')
                purchased_bool = int(details.get(
                    'ineligiblePurchase') is not None)
                yield {
                    'listing_id': listing_id,
                    'upgrade_product': offer_name,
                    'upgrade_price': offer_price,
                    'purchased_bool': purchased_bool,
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
                    property_detail = payload[1].get('property')
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
