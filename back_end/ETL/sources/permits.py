'''
permits.py
----------

This file collects raw building permit data, and summarizes the information
for each census tract. It is called by make_zone_facts.py

The resulting dataset from this file looks like:

 zone_type |   zone  | construction_permits | total_permits
 ----------|---------|----------------------|--------------
 tract     | 000100  |                 231  |          575
 tract     | 000201  |                   2  |            6
 tract     | 000202  |                 145  |          363
 tract     | 000300  |                 102  |          351
 tract     | 000400  |                  77  |          204
'''
from . import utils
from sqlalchemy import create_engine
import pandas as pd
# TODO: Have this grab the link from S3

URL = 'https://opendata.arcgis.com/datasets/52e671890cb445eba9023313b1a85804_8.csv'
def get_permit_data():
    df = pd.read_csv(URL)
    df.columns = df.columns.str.lower()
    df['construction_permits'] = df['permit_type_name'].apply(
            lambda x: 1 if x == 'CONSTRUCTION' else 0)
    df['total_permits'] = 1

    # Get census tract
    df = utils.get_census_tract_for_data(df, 'longitude', 'latitude')
    df = df[['tract', 'ward', 'neighborhoodcluster', 'construction_permits', 'total_permits']]

    df = df.rename(columns={'neighborhoodcluster': 'neighborhood_cluster'})
    df['neighborhood_cluster'] = utils.just_digits(df['neighborhood_cluster'])

    for geo in ['tract', 'neighborhood_cluster', 'ward']:
        temp = df.groupby(geo)[['construction_permits', 'total_permits']].sum()
        temp['zone_type'] = geo
        temp['zone'] = temp.index
        data.append(temp)
    return pd.concat(data).reset_index(drop=True)

def load_permit_data():
    '''Actually loads the data into the db.'''
    try:
        get_permit_data().to_sql(
            'new_permit',
            create_engine(utils.get_credentials('docker_database_connect_str')),
            if_exists='replace',
            index=False)
        return True
    except:
        return False
