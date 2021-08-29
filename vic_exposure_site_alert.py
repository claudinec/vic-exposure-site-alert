# Periodically fetch Victorian Covid-19 exposure site data and alert via Pushcut.

import csv
import json
from datetime import datetime
import re
import requests

config_file = 'config.json'
tier_match = '(Tier\s[0-9])'
data_url = 'https://drive.google.com/uc?export=download&id=1hULHQeuuMQwndvKy1_ScqObgX0NRUv1A'
data_csv_file = 'data/exposure-sites-data.csv'
data_json_file = 'data/exposure-sites-data.json'
date_last_run_dt = datetime.now()
date_last_run_str = {"date_last_run": date_last_run_dt.isoformat()}
date_last_run_file = 'data/date_last_run.json'

# Get configuration.
with open(config_file, mode='r') as config_file_reader:
    config = json.load(config_file_reader)

# Fetch the data to be parsed by data_parser.
r = requests.get(data_url, stream=True)
if (r.ok):
    data_json = []
    data_str = r.content.decode()
    with open(data_csv_file, mode='w',newline='\r') as csv_file_writer:
        print(data_str, file=csv_file_writer)
    with open(data_csv_file, mode='r',newline='\r') as csv_file_reader:
        csv_reader = csv.DictReader(csv_file_reader)
        for row in csv_reader:
            data_json.append(row)
    with open(data_json_file, mode='w') as json_file_writer:
        json.dump(data_json, json_file_writer)
else:
    print(r.status_code)

# Parse exposure site data.
with open(data_json_file, mode='r') as data_file_reader:
    data_json = json.load(data_file_reader)
    for site in data_json:
        pushcut_data = {}
        suburb_str = site['Suburb']
        added_dt = datetime.fromisoformat(site['Added_date_dtm'])
        if (suburb_str in config['suburbs_list'] and added_dt > date_last_run_dt):
            tier_num = re.match(tier_match, site['Advice_title'])
            pushcut_data['title'] = tier_num[0] + ' Covid-19 exposure in ' + suburb_str
            pushcut_text = site['Site_title'] + '\n' + site['Site_streetaddress'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
            pushcut_data['text'] = pushcut_text
            if config['pushcut_devices']:
                pushcut_data['devices'] = config['pushcut_devices']
            r = requests.post(config['pushcut_url'], json=pushcut_data)

with open(date_last_run_file, mode='w') as date_last_run_writer:
    json.dump(date_last_run_str, date_last_run_writer)
