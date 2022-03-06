import json
import csv
import argparse


def read_items(filepath):
    with open(filepath) as f:
        return json.load(f)


def flatten_items(items):
    listings = list(filter(lambda l: l['data_type'] == 'listing', items))
    upgrade_prices = list(filter(
        lambda l: l['data_type'] == 'upgrade_price', items))
    for listing in listings:
        listing_id = listing.get('listing_id')
        prices = [
            d for d in upgrade_prices if d['listing_id'] == listing_id]
        if prices:
            listing['plus_price'] = prices[0].get('plus').get('price')
            listing['premium_price'] = prices[0].get('premium').get('price')
            listing['raketen_price'] = prices[0].get('raketen').get('price')
            listing['publication_date'] = prices[0].get('publication_date')
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
