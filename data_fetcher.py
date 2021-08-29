# Fetch the data to be parsed by data_parser.

import csv
import json
import requests

data_csv_file = 'data/exposure-sites-data.csv'
data_json_file = 'data/exposure-sites-data.json'

r = requests.get('https://drive.google.com/uc?export=download&id=1hULHQeuuMQwndvKy1_ScqObgX0NRUv1A', stream=True)

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
