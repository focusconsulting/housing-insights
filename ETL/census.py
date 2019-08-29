'''
    census.py
    ---------

    This file collects ACS data.

    TO-DO: Establish the outputs needed from this data, and clean some of the
    raw data in this file.
'''
from temp_credentials import key
import requests
import pandas as pd

year = 2017 # Most recent year of 5 year estimates.
base = f'https://api.census.gov/data/{year}/acs/acs5'

fields = {
    'B01003_001E': 'total_population',
}

response = requests.get(base,
        params={
            'get': 'NAME,' + ','.join(fields.keys()),
            'for': 'tract:*',
            'in': 'state:11',
            'key': key,
            }
)
print(response)
data = response.json()
df = pd.DataFrame(data[1:], columns=data[0])
df = df.rename(columns=fields)
print(df.head())
