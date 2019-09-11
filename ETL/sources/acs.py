'''
    acs.py
    ------

    This file collects raw ACS data. It is used as the base file for
    make_zone_facts.py

'''
from temp_credentials import key
import requests
import pandas as pd

year = 2017 # Most recent year of 5 year estimates.
base = f'https://api.census.gov/data/{year}/acs/acs5'

fields = {
    'B01003_001E': 'total_population',
    'B02001_003E': 'black_population',
    'B17020_002E': 'population_in_poverty',
    'B23025_002E': 'labor_force_population',
    'B16008_019E': 'foreign_born_population',
    'B09002_015E': 'single_mom_households',
    'B19025_001E': 'aggregate_household_income',
    'B25057_001E': 'lower_rent_quartile_in_dollars',
    'B25058_001E': 'median_rent_quartile_in_dollars',
    'B25059_001E': 'upper_rent_quartile_in_dollars',
}

def get_acs_data():
    response = requests.get(base,
        params={
            'get': 'NAME,' + ','.join(fields.keys()),
            'for': 'tract:*',
            'in': 'state:11',
            'key': key,
        }
    )

    try:
        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])
        return df.rename(columns=fields)
    except:
        raise ValueError("Could not query data!")
