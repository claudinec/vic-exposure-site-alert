# Fetch the data to be parsed by data_parser.

import requests

data_csv = 'data/exposure-sites-data.csv'

r = requests.get('https://drive.google.com/uc?export=download&id=1hULHQeuuMQwndvKy1_ScqObgX0NRUv1A', stream=True)

if (r.ok):
    data_str = r.content.decode()

with open(data_csv, mode='w',newline='\r') as file_writer:
    print(data_str, file=file_writer)
