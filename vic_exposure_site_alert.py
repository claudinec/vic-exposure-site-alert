# Periodically fetch Victorian Covid-19 exposure site data and alert via Pushcut.

import csv
import json
from datetime import datetime
import logging
import logging.handlers
import re
import requests

CONFIG_FILE = 'config.json'
LOG_FILE = 'logs/debug.log'
TIER_MATCH = '(Tier\s[0-9])'
DATA_URL = 'https://drive.google.com/uc?export=download&id=1hULHQeuuMQwndvKy1_ScqObgX0NRUv1A'
DATA_CSV_FILE = 'data/exposure-sites-data.csv'
DATA_JSON_FILE = 'data/exposure-sites-data.json'
DATE_LAST_RUN_FILE = 'data/date_last_run.json'

# Start logging.
def start_log():
    alert_logger = logging.getLogger('alert')
    alert_logger.setLevel(logging.DEBUG)
    alert_fhandler = logging.handlers.TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount=28)
    alert_fhandler.setFormatter('%(asctime)s %(levelname)s %(message)s')
    return alert_logger

def check_config(logger):
    with open(CONFIG_FILE, mode='r') as config_file_reader:
        config = json.load(config_file_reader)
        if (config['pushcut_url'] == ''):
            logger.critical('Pushcut URL not set')
        else:
            return config

def fetch_data(req):
    data_json = []
    data_str = req.content.decode()
    with open(DATA_CSV_FILE, mode='w',newline='\r') as csv_file_writer:
        print(data_str, file=csv_file_writer)
    with open(DATA_CSV_FILE, mode='r',newline='\r') as csv_file_reader:
        csv_reader = csv.DictReader(csv_file_reader)
        for row in csv_reader:
             data_json.append(row)
    with open(DATA_JSON_FILE, mode='w') as json_file_writer:
        json.dump(data_json, json_file_writer)
    return data_json

def parse_data(logger, config, date_last_run_dt, data_json):
    suburbs_list = config['suburbs_list']
    for site in data_json:
        pushcut_data = {}
        suburb_str = site['Suburb']
        if (site['Added_time'] != ''):
            added_str = site['Added_date_dtm'] + 'T' + site['Added_time']
        else:
            added_str = site['Added_date_dtm'] + 'T00:00:00'
        added_dt = datetime.fromisoformat(added_str)
        if (suburb_str.strip() in suburbs_list and added_dt > date_last_run_dt):
            tier_num = re.match(TIER_MATCH, site['Advice_title'])
            pushcut_data['title'] = tier_num[0] + ' Covid-19 exposure in ' + suburb_str
            pushcut_text = site['Site_title'] + '\n' + site['Site_streetaddress'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
            pushcut_data['text'] = pushcut_text
            r = requests.post(config['pushcut_url'], json=pushcut_data)
            logger.info('Alert sent:')
            logger.info(suburb_str)

def check_data():
    # Start logging.
    logger = start_log()

    # Get configuration.
    config = check_config(logger)

    # When did we last check the data?
    with open(DATE_LAST_RUN_FILE, mode='r') as date_last_run_reader:
        date_last_run = json.load(date_last_run_reader)
        date_last_run_str = date_last_run['date_last_run']
        logger.debug('Date last run:')
        logger.debug(date_last_run_str)
        if (date_last_run_str != ''):
            date_last_run_dt = datetime.fromisoformat(date_last_run_str)

    # Fetch the data to be parsed.
    logger.info('Fetching data')
    req = requests.get(DATA_URL, stream=True)
    if (req.ok):
        data_json = fetch_data(req)
        # Parse exposure site data.
        logger.info('Parsing data')
        parse_data(logger, config, date_last_run_dt, data_json)
        # Update last run date.
        date_now_dt = datetime.now()
        date_now_str = {"date_last_run": date_now_dt.isoformat()}
        with open(DATE_LAST_RUN_FILE, mode='w') as date_last_run_writer:
            json.dump(date_now_str, date_last_run_writer)
        logger.info('All done')
    else:
        logger.error(r.status_code)

check_data()

