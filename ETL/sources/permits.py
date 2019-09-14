'''
permits.py
----------

This file collects raw building permit data, and summarizes the information
for each census tract. It is called by make_zone_facts.py

The resulting dataset from this file looks like:

    tract  | construction_permits | total_permits
    -------|----------------------|--------------
    000100 |                 231  |          575
    000201 |                   2  |            6
    000202 |                 145  |          363
    000300 |                 102  |          351
    000400 |                  77  |          204
'''
import utils
import pandas as pd

df = pd.read_csv('https://opendata.arcgis.com/datasets/52e671890cb445eba9023313b1a85804_8.csv')
df.columns = df.columns.str.lower()
df['construction_permits'] = df['permit_type_name'].apply(
        lambda x: 1 if x == 'CONSTRUCTION' else 0)
df['total_permits'] = 1

# Merge to tract
df = utils.get_census_tract_for_data(df, 'longitude', 'latitude')
df = df[['tract', 'construction_permits', 'total_permits']]
df = df.groupby('tract').sum()
