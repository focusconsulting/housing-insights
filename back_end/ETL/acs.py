'''
acs.py
------

This file collects raw ACS data. It is used as the base file for
make_zone_facts.py
'''
import requests
import pandas as pd
from . import utils

key = utils.get_credentials('census-api-key')

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

def get_tract_data():
    response = requests.get(base,
        params={
            'get': ','.join(fields.keys()),
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

def get_zone_data(tract_df, zone_type):
    '''
    Takes the tract data and aggregates it to another geography.

    zone_type is either 'ward' or 'neighborhood_cluster'
    '''
    weights = pd.read_csv(utils.S3+f'geographic_data/tract_{zone_type}_weights.csv')
    weights.tract = weights.tract.apply(utils.fix_tract)

    df = tract_df.merge(weights, left_on='tract', right_on='tract')
    df[zone_type] = utils.just_digits(df[zone_type])
    for col in fields.values():
        df[col] = df[col].astype(float) * df.weight

    return df.groupby(zone_type).sum().drop('weight', axis=1).apply(round)

def get_acs_data():
    '''Returns a dataset for tract, cluster, and ward.'''
    tract = get_tract_data()
    cluster = get_zone_data(tract, 'neighborhood_cluster')
    ward = get_zone_data(tract, 'ward')
    return tract, cluster, ward
