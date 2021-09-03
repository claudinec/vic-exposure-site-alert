# Periodically fetch Victorian Covid-19 exposure site data and alert via Pushcut.

import csv
from datetime import datetime
import json
import logging
import logging.handlers
import os
import re
import requests

CONFIG_FILE = 'config.json'
LOG_FILE = 'logs/debug.log'
BUS_RE = r'Bus (?P<bus_route>[0-9]+)'
TIER_RE = r'(Tier [0-9])'
TRAIN_RE = r'Trains? - (?P<train_line>[a-zA-Z]+ Line)'
TRAM_RE = r'Tram (?:Route )?(?P<tram_route>[0-9]+)'
DATA_URL = 'https://drive.google.com/uc?export=download&id=1hULHQeuuMQwndvKy1_ScqObgX0NRUv1A'
DATA_CSV_FILE = 'data/exposure-sites-data.csv'
DATA_JSON_FILE = 'data/exposure-sites-data.json'
DATE_LAST_RUN_FILE = 'data/date_last_run.json'

# TODO mkdir data and logs if they don't exist

# Start logging.
def start_log():
    alert_logger = logging.getLogger('alert')
    alert_logger.setLevel(logging.DEBUG)
    alert_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    alert_fhandler = logging.handlers.TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount=28)
    alert_fhandler.setFormatter(alert_formatter)
    alert_logger.addHandler(alert_fhandler)
    return alert_logger

# Check configuration.
def get_config(logger):
    url_re = r'https\:\/\/api\.pushcut\.io\/.*\/notifications\/'
    with open(CONFIG_FILE, mode='r') as config_file_reader:
        config = json.load(config_file_reader)
        if (re.match(url_re, config['pushcut_url'])):
            return config
        else:
            logger.critical('Invalid Pushcut URL')

def check_suburbs(logger, config, date_last_run_dt, data_json):
    alert_suburbs = config['alert_suburbs']
    # Default suburb alert to Melbourne if no suburbs provided.
    if (alert_suburbs == []):
        alert_suburbs = ['Melbourne']
    for site in data_json:
        pushcut_data = {}
        suburb_str = site['Suburb']
        if (site['Added_time'] != ''):
            added_dt = added_time(site)
        if (suburb_str.strip() in alert_suburbs and added_dt > date_last_run_dt):
            tier_match = re.match(TIER_RE, site['Advice_title'])
            pushcut_data['title'] = tier_match[0] + ' Covid-19 exposure in ' + suburb_str
            pushcut_text = site['Site_title'] + '\n' + site['Site_streetaddress'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
            pushcut_data['text'] = pushcut_text
            send_alert(logger, config, pushcut_data)

def check_pt(logger, config, date_last_run_dt, data_json):
    # alert_trains = config['alert_trains']
    for site in data_json:
        pushcut_data = {}
        if (site['Suburb'] == 'Public Transport'):
            added_dt = added_time(site)
            bus_match = re.match(BUS_RE, site['Site_title'])
            tram_match = re.match(TRAM_RE, site['Site_title'])
            train_match = re.match(TRAIN_RE, site['Site_title'])
            if (bus_match):
                bus_route = int(bus_match['bus_route'])
                if (bus_route in config['alert_buses'] and added_dt > date_last_run_dt):
                    tier_match = re.match(TIER_RE, site['Advice_title'])
                    pushcut_data['title'] = tier_match[0] + 'Covid-19 exposure on bus ' + bus_route
                    pushcut_text = site['Site_title'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
                    pushcut_data['text'] = pushcut_text
                    send_alert(logger, config, pushcut_data)
            elif (train_match):
                train_route = int(train_match['train_line'])
                if (train_route in config['alert_trains'] and added_dt > date_last_run_dt):
                    tier_match = re.match(TIER_RE, site['Advice_title'])
                    pushcut_data['title'] = tier_match[0] + 'Covid-19 exposure on train ' + train_route
                    pushcut_text = site['Site_title'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
                    pushcut_data['text'] = pushcut_text
                    send_alert(logger, config, pushcut_data)
            elif (tram_match):
                tram_route = int(tram_match['tram_route'])
                if (tram_route in config['alert_trams'] and added_dt > date_last_run_dt):
                    tier_match = re.match(TIER_RE, site['Advice_title'])
                    pushcut_data['title'] = tier_match[0] + 'Covid-19 exposure on tram ' + tram_route
                    pushcut_text = site['Site_title'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
                    pushcut_data['text'] = pushcut_text
                    send_alert(logger, config, pushcut_data)

def added_time(site):
    # Some of the entries don't include the time it was added to the table, only the date.
    if (site['Added_time'] != ''):
        added_str = site['Added_date_dtm'] + 'T' + site['Added_time']
    else:
        added_str = site['Added_date_dtm'] + 'T00:00:00'
    added_dt = datetime.fromisoformat(added_str)
    return added_dt

def send_alert(logger, config, pushcut_data):
    if ('pushcut_devices' in config):
        pushcut_data['devices'] = config['pushcut_devices']
    pushcut_req = requests.post(config['pushcut_url'], json=pushcut_data)
    if (pushcut_req.ok):
        log_msg = 'Alert sent: ' + pushcut_data['title']
        logger.info(log_msg)
    else:
        logger.error(pushcut_req.status_code)

def check_data():
    # Start logging.
    logger = start_log()

    # Check configuration.
    config = get_config(logger)

    # When did we last check the data?
    with open(DATE_LAST_RUN_FILE, mode='r') as date_last_run_reader:
        date_last_run = json.load(date_last_run_reader)
        date_last_run_str = date_last_run['date_last_run']
        if (date_last_run_str != ''):
            log_msg = 'Date last run: ' + date_last_run_str
            logger.debug(log_msg)
            date_last_run_dt = datetime.fromisoformat(date_last_run_str)

    # Fetch data from Victorian Government Google Drive.
    logger.info('Fetching data')
    data_req = requests.get(DATA_URL, stream=True)
    if (data_req.ok):
        data_json = []
        data_str = data_req.content.decode()
        with open(DATA_CSV_FILE, mode='w',newline='\r') as csv_file_writer:
            print(data_str, file=csv_file_writer)
        with open(DATA_CSV_FILE, mode='r',newline='\r') as csv_file_reader:
            csv_reader = csv.DictReader(csv_file_reader)
            for row in csv_reader:
                data_json.append(row)
        with open(DATA_JSON_FILE, mode='w') as json_file_writer:
            json.dump(data_json, json_file_writer)

        # Check suburbs.
        logger.info('Checking suburbs')
        check_suburbs(logger, config, date_last_run_dt, data_json)
        # Check public transport.
        if (config['alert_trains'] != [] or config['alert_trams'] != []):
            logger.info('Checking public transport')
            check_pt(logger, config, date_last_run_dt, data_json)
        # Update last run date.
        date_now_dt = datetime.now()
        date_now_str = {"date_last_run": date_now_dt.isoformat()}
        with open(DATE_LAST_RUN_FILE, mode='w') as date_last_run_writer:
            json.dump(date_now_str, date_last_run_writer)
        logger.info('All done')
    else:
        logger.error(data_req.status_code)

check_data()

