import json
import csv
import argparse


def read_items(filepath):
    with open(filepath) as f:
        return json.load(f)


def flatten_items(items):
    listings = list(filter(lambda l: l['data_type'] == 'listing', items))
    plus_prices = list(filter(
        lambda l: l['data_type'] == 'upgrade_price'
        and l['upgrade_product'] == 'Hemnet Plus', items))
    premium_prices = list(filter(
        lambda l: l['data_type'] == 'upgrade_price'
        and l['upgrade_product'] == 'Hemnet Premium', items))
    for listing in listings:
        listing_id = listing.get('listing_id')
        plus_dict = [
            d for d in plus_prices if d['listing_id'] == listing_id][0]
        premium_dict = [
            d for d in premium_prices if d['listing_id'] == listing_id][0]
        listing['plus_price'] = plus_dict.get('upgrade_price')
        listing['premium_price'] = premium_dict.get('upgrade_price')
    return listings


parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('output_file')
args = parser.parse_args()
items = read_items(args.input_file)
listings = flatten_items(items)
with open(args.output_file, 'w') as output:
    fields = list(listings[0].keys())
    dict_writer = csv.DictWriter(output, fields, delimiter='\t')
    dict_writer.writeheader()
    dict_writer.writerows(listings)
