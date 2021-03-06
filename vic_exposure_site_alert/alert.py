import csv
from datetime import datetime
import json
import logging
import logging.handlers
import os
import pathlib
import re
import sys
import time

import requests
import schedule

from . import utils

TIER_RE = r'(Tier [0-9])'

def get_config(logger):
    """Open and validate configuration file."""
    project_dir = utils.get_project_dir()
    config_file = project_dir.joinpath('config.json')
    url_re = r'https\:\/\/api\.pushcut\.io\/.*\/notifications\/'
    try:
        with config_file.open(mode='r') as config_file_reader:
            config = json.load(config_file_reader)
            try:
                re.match(url_re, config['pushcut_url'])
                return config
            except:
                logger.exception('Invalid Pushcut URL')
    except:
        logger.exception('Unable to open config file')

def check_suburbs(logger, config, date_last_run_dt, data_json):
    """Check exposure site data for selected suburbs.
    
    The default suburb alert is set to 'Melbourne' if no suburbs are
    provided.
    """
    try:
        alert_suburbs = config['alert_suburbs']
    except:
        alert_suburbs = ['Melbourne']
    for site in data_json:
        pushcut_data = {}
        suburb_str = site['Suburb']
        added_dt = added_time(site)
        if (suburb_str.strip() in alert_suburbs and added_dt > date_last_run_dt):
            tier_match = re.match(TIER_RE, site['Advice_title'])
            pushcut_data['title'] = tier_match[0] + ' Covid-19 exposure in ' + suburb_str
            pushcut_text = site['Site_title'] + '\n' + site['Site_streetaddress'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
            pushcut_data['text'] = pushcut_text
            send_alert(logger, config, pushcut_data)

def check_pt(logger, config, date_last_run_dt, data_json):
    """Check exposure site data for selected public transport routes."""
    bus_re = r'Bus (?P<bus_route>[0-9]+)'
    train_re = r'Trains? - (?P<train_line>[a-zA-Z]+ Line)'
    tram_re = r'Tram\s(Route\s|number\s)?(?P<tram_route>[0-9]+)'
    for site in data_json:
        pushcut_data = {}
        if (site['Suburb'] == 'Public Transport'):
            tier_match = re.match(TIER_RE, site['Advice_title'])
            added_dt = added_time(site)
            bus_match = re.match(bus_re, site['Site_title'])
            train_match = re.match(train_re, site['Site_title'])
            tram_match = re.search(tram_re, site['Site_title'], flags=re.IGNORECASE)
            if (bus_match):
                bus_route = int(bus_match['bus_route'])
                if (bus_route in config['alert_buses'] and added_dt > date_last_run_dt):
                    pushcut_data['title'] = tier_match[0] + ' Covid-19 exposure on bus ' + str(bus_route)
                    pushcut_text = site['Site_title'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
                    pushcut_data['text'] = pushcut_text
                    send_alert(logger, config, pushcut_data)
            elif (train_match):
                train_line = train_match['train_line']
                if (train_line in config['alert_trains'] and added_dt > date_last_run_dt):
                    pushcut_data['title'] = tier_match[0] + ' Covid-19 exposure on train ' + train_line
                    pushcut_text = site['Site_title'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
                    pushcut_data['text'] = pushcut_text
                    send_alert(logger, config, pushcut_data)
            elif (tram_match and 'alert_trams' in config):
                tram_route = int(tram_match['tram_route'])
                if (tram_route in config['alert_trams'] and added_dt > date_last_run_dt):
                    pushcut_data['title'] = tier_match[0] + ' Covid-19 exposure on tram ' + str(tram_route)
                    pushcut_text = site['Site_title'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
                    pushcut_data['text'] = pushcut_text
                    send_alert(logger, config, pushcut_data)

def added_time(site):
    """Return the date/time a site was added as a datetime object.
    
    Some of the entries don't include the time it was added to the table,
    only the date.
    """
    if (site['Added_time'] != ''):
        added_str = site['Added_date_dtm'] + 'T' + site['Added_time']
    else:
        added_str = site['Added_date_dtm'] + 'T00:00:00'
    added_dt = datetime.fromisoformat(added_str)
    return added_dt

def send_alert(logger, config, pushcut_data):
    """Send an alert to Pushcut."""
    if ('pushcut_devices' in config):
        pushcut_data['devices'] = config['pushcut_devices']
        for device_str in config['pushcut_devices']:
            device_msg = 'Sending to device ' + device_str
            logger.debug(device_msg)
    pushcut_req = requests.post(config['pushcut_url'], json=pushcut_data)
    if (pushcut_req.ok):
        log_msg = 'Alert sent: ' + pushcut_data['title']
        logger.debug(log_msg)
    else:
        logger.error(pushcut_req.status_code)

def check_data(logger):
    """Check exposure site data."""
    project_dir = utils.get_project_dir()
    data_dir = project_dir.joinpath('data')
    if not data_dir.is_dir():
        utils.make_dir('data')
    data_csv_file = data_dir.joinpath('exposure-sites-data.csv')
    data_json_file = data_dir.joinpath('exposure-sites-data.json')
    date_last_run_file = data_dir.joinpath('date_last_run.json')

    # Check configuration.
    config = get_config(logger)

    # When did we last check the data?
    try:
        with date_last_run_file.open(mode='r') as date_last_run_reader:
            date_last_run = json.load(date_last_run_reader)
            date_last_run_str = date_last_run['date_last_run']
            if date_last_run_str != '':
                log_msg = 'Date last run: ' + date_last_run_str
                logger.debug(log_msg)
                date_last_run_dt = datetime.fromisoformat(date_last_run_str)
            else:
                date_last_run_dt = datetime.today().replace(hour=0, minute=0, second=0)
    except:
        logger.exception(sys.exc_info()[0])
        date_last_run_dt = datetime.today().replace(hour=0, minute=0, second=0)

    # Fetch data from Victorian Government Google Drive.
    logger.debug('Fetching data')
    data_url = 'https://drive.google.com/uc?export=download&id=1hULHQeuuMQwndvKy1_ScqObgX0NRUv1A'
    data_req = requests.get(data_url, stream=True)
    if (data_req.ok):
        data_json = []
        data_str = data_req.content.decode()
        with data_csv_file.open(mode='w',newline='\r') as csv_file_writer:
            print(data_str, file=csv_file_writer)
        with data_csv_file.open(mode='r',newline='\r') as csv_file_reader:
            csv_reader = csv.DictReader(csv_file_reader)
            for row in csv_reader:
                data_json.append(row)
        with data_json_file.open(mode='w') as json_file_writer:
            json.dump(data_json, json_file_writer)

        # Check suburbs.
        logger.debug('Checking suburbs')
        check_suburbs(logger, config, date_last_run_dt, data_json)

        # Check public transport.
        if ('alert_buses' in config or 'alert_trains' in config or 'alert_trams' in config):
            logger.debug('Checking public transport')
            check_pt(logger, config, date_last_run_dt, data_json)

        # Update last run date.
        date_now_dt = datetime.now()
        date_now_str = {"date_last_run": date_now_dt.isoformat()}
        with date_last_run_file.open(mode='w') as date_last_run_writer:
            json.dump(date_now_str, date_last_run_writer)
        logger.debug('All done')
    else:
        logger.error(data_req.status_code)

def main(freq=0, end=''):
    """Check exposure site data.
    
    If ``freq`` is 0 or missing, run once.
    Otherwise, run every ``freq`` minutes until ``end``.
    """
    logger = utils.start_log('alert', 28)
    if freq==0:
        check_data(logger)
        logging.shutdown()
    else:
        def do_check_data():
            check_data(logger)
        utils.start_log('schedule', 7)
        try:
            schedule.every(freq).minutes.until(end).do(do_check_data)
            while schedule.next_run():
                schedule.run_pending()
                time.sleep(10)
            logging.shutdown()
        except:
            logger.exception(sys.exc_info()[0])
        finally:
            logging.shutdown()

if __name__ == "__main__":
    main()
