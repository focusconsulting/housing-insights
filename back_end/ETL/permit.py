'''
permit.py
---------

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
import pandas as pd

def get_permit_for_year(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()
    df['construction_permits'] = df['permit_type_name'].apply(
            lambda x: 1 if x == 'CONSTRUCTION' else 0)
    df['total_permits'] = 1

    # filter out permits from more than a year ago.
    df = utils.filter_date(df, 'issue_date')

    # Get census tract
    df = utils.get_census_tract_for_data(df, 'longitude', 'latitude')
    df = df[['tract', 'ward', 'neighborhoodcluster', 'construction_permits', 'total_permits']]

    df = df.rename(columns={'neighborhoodcluster': 'neighborhood_cluster'})
    df['neighborhood_cluster'] = utils.just_digits(df['neighborhood_cluster'])
    return df


def get_permit_data():
    paths = utils.get_paths_for_data('permits', years=utils.get_years())
    df = pd.concat([get_permit_for_year(path) for path in paths])
    data = []
    for geo in ['tract', 'neighborhood_cluster', 'ward']:
        temp = df.groupby(geo)[['construction_permits', 'total_permits']].sum()
        temp['zone_type'] = geo
        temp['zone'] = temp.index
        data.append(temp)
    return pd.concat(data).reset_index(drop=True)

def load_permit_data(engine):
    '''Actually loads the data into the db.'''
    df = get_permit_data()
    return utils.write_table(df, 'new_permit', engine)
