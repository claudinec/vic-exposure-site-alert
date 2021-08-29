# Parse exposure site data.

import json
import re
from datetime import datetime, timedelta
import requests

suburbs_json_file = 'config/suburbs.json'
pushcut_json_file = 'config/pushcut.json'
data_json_file = 'data/exposure-sites-data.json'
tier_match = '(Tier\s[0-9])'

last_run_dt = datetime.now()
last_run_str = {"last_run": last_run_dt.isoformat()}
last_run_file = 'data/last_run.json'

with open(suburbs_json_file, mode='r') as suburbs_file_reader:
    suburbs_list = json.load(suburbs_file_reader)

with open(pushcut_json_file, mode='r') as pushcut_file_reader:
    pushcut_config = json.load(pushcut_file_reader)
    pushcut_url = pushcut_config['pushcut_url']

with open(data_json_file, mode='r') as data_file_reader:
    data_json = json.load(data_file_reader)
    for site in data_json:
        pushcut_data = {}
        suburb_str = site['Suburb']
        added_dt = datetime.fromisoformat(site['Added_date_dtm'])
        if (suburb_str in suburbs_list and added_dt > last_run_dt):
            tier_num = re.match(tier_match, site['Advice_title'])
            pushcut_data['title'] = tier_num[0] + ' Covid-19 exposure in ' + suburb_str
            pushcut_text = site['Site_title'] + '\n' + site['Site_streetaddress'] + '\n' + site['Exposure_date'] + ' ' + site['Exposure_time']
            pushcut_data['text'] = pushcut_text
            r = requests.post(pushcut_url, json=pushcut_data)

with open(last_run_file, mode='w') as last_run_file_writer:
    json.dump(last_run_str, last_run_file_writer)
