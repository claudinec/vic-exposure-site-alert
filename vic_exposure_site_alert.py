# Periodically fetch Victorian Covid-19 exposure site data and alert via Pushcut.

import csv
import json
from datetime import datetime
import logging
import re
import requests

config_file = 'config.json'
tier_match = '(Tier\s[0-9])'
data_url = 'https://drive.google.com/uc?export=download&id=1hULHQeuuMQwndvKy1_ScqObgX0NRUv1A'
data_csv_file = 'data/exposure-sites-data.csv'
data_json_file = 'data/exposure-sites-data.json'
date_last_run_file = 'data/date_last_run.json'

def check_config():
    with open(config_file, mode='r') as config_file_reader:
        config = json.load(config_file_reader)
        if (config['pushcut_url'] == ''):
            logging.critical('Pushcut URL not set')
        else:
            return config

def fetch_data(req):
    data_json = []
    data_str = req.content.decode()
    with open(data_csv_file, mode='w',newline='\r') as csv_file_writer:
        print(data_str, file=csv_file_writer)
    with open(data_csv_file, mode='r',newline='\r') as csv_file_reader:
        csv_reader = csv.DictReader(csv_file_reader)
        for row in csv_reader:
             data_json.append(row)
    with open(data_json_file, mode='w') as json_file_writer:
        json.dump(data_json, json_file_writer)
    return data_json

def parse_data(config, date_last_run_dt, data_json):
    suburbs_list = config['suburbs_list']
    for site in data_json:
        pushcut_data = {}
        suburb_str = site['Suburb']
        if (site['Added_time'] != ''):
            added_str = site['Added_date_dtm'] + 'T' + site['Added_time']
        else:
            added_str = site['Added_date_dtm'] + 'T00:00:00'
        added_dt = datetime.fromisoformat(added_str)
        if (suburb_str in suburbs_list and added_dt > date_last_run_dt):
            tier_num = re.match(tier_match, site['Advice_title'])
            pushcut_data['title'] = tier_num[0] + ' Covid-19 exposure in ' + suburb_str
            pushcut_text = site['Site_title'] + '\n' + site['Site_streetaddress'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
            pushcut_data['text'] = pushcut_text
            r = requests.post(config['pushcut_url'], json=pushcut_data)
            logging.info('Alert sent:')
            logging.info(suburb_str)

def check_data():
    # Start logging.
    logging.basicConfig(filename='logs/debug.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    # Get configuration.
    config = check_config()

    # When did we last check the data?
    with open(date_last_run_file, mode='r') as date_last_run_reader:
        date_last_run = json.load(date_last_run_reader)
        date_last_run_str = date_last_run['date_last_run']
        logging.debug('Date last run:')
        logging.debug(date_last_run_str)
        if (date_last_run_str != ''):
            date_last_run_dt = datetime.fromisoformat(date_last_run_str)

    # Fetch the data to be parsed.
    logging.info('Fetching data')
    req = requests.get(data_url, stream=True)
    if (req.ok):
        data_json = fetch_data(req)
        # Parse exposure site data.
        logging.info('Parsing data')
        parse_data(config, date_last_run_dt, data_json)
        # Update last run date.
        date_now_dt = datetime.now()
        date_now_str = {"date_last_run": date_now_dt.isoformat()}
        with open(date_last_run_file, mode='w') as date_last_run_writer:
            json.dump(date_now_str, date_last_run_writer)
        logging.info('All done')
    else:
        logging.error(r.status_code)

check_data()
