#!/bin/bash -e

SCRAPY_OUPUT="data/items_$(date -u +"%Y%m%d_%H_%MZ").json"
LOG_OUTPUT="logs/log_$(date -u +"%Y%m%d_%H_%MZ").txt"
FILE_OUTPUT="data/listings_$(date -u +"%Y%m%d_%H_%MZ").txt"

cd "$(dirname "$0")"
source run.config
scrapy crawl search -O $SCRAPY_OUPUT -L INFO --logfile $LOG_OUTPUT
python3 process_scrapped_items.py $SCRAPY_OUPUT $FILE_OUTPUT

curl -s --user $API_KEY \
    https://api.mailgun.net/v3/mg.johnnyclee.com/messages \
    -F from='Pi <pi@johnnyclee.com>' \
    -F to=$TO_EMAIL \
    -F subject="[Scrapy Status] Complete $(date)" \
    -F text="$(wc -l $FILE_OUTPUT)"