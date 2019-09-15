'''
make_zone_facts.py
------------------

This file creates the zone_facts table in the database, which is sent to
the front-end via /api/zone_facts/. It depends on the census data, crime
data, building permit data, and the geograpic boundaries.

The output columns for this file are:

    - zone_type:                Tract, neighborhood, or ward.
    - zone:                     Tract, neighborhood, or ward number.
    - poverty_rate
    - fraction_black
    - income_per_capita
    - labor_participation
    - fraction_foreign
    - fraction_single_mothers
    - acs_median_rent
    - crime_rate
    - violent_crime_rate
    - non_violent_crime_rate
    - building_permits_rate
    - construction_permits_rate
'''

import pandas as pd
from sources import get_acs_data, get_crime_data, get_permit_data

scaled_columns = [
    ('poverty_rate', 'population_in_poverty'),
    ('fraction_black', 'black_population'),
    ('income_per_capita', 'aggregate_household_income'),
    ('labor_participation', 'labor_force_population'),
    ('fraction_foreign', 'foreign_born_population'),
    ('fraction_single_mothers', 'single_mom_households'),
    ('acs_median_rent', 'median_rent_quartile_in_dollars'),
    ('crime_rate', 'crime'),
    ('violent_crime_rate', 'violent_crime'),
    ('non_violent_crime_rate', 'non_violent_crime'),
]

def combine_at_level(acs, permit, crime, level='tract'):
    '''Combines ACS, permit, and crime data for a zone type.'''
    for df in acs, permit, crime:
        df.index = df.index.astype(str)
    df = acs.merge(permit, left_on=level, right_on=level)
    df = df.merge(crime, left_on=level, right_on=level)
    df['zone_type'] = level
    return df.reset_index().rename(columns={level: 'zone'})

def make_base_table():
    print("Grabbing ACS data")
    acs_tract, acs_cluster, acs_ward = get_acs_data()

    print("Grabbing permit data")
    permit_tract, permit_cluster, permit_ward = get_permit_data()

    print("Grabbing crime data")
    crime_tract, crime_cluster, crime_ward = get_crime_data()

    return pd.concat([
        combine_at_level(acs_tract, permit_tract, crime_tract, level='tract'),
        combine_at_level(acs_cluster, permit_cluster, crime_cluster, level='neighborhood_cluster'),
        combine_at_level(acs_ward, permit_ward, crime_ward, level='ward'),
    ], sort=True)

def make_rates(df):
    '''Scales variables by the population.'''
    for scaled, original in scaled_columns:
        print(original)
        df[scaled] = df[original].astype(float) / df['total_population'].astype(float)
    return df

# Need the number of residential units?
#df['building_permits_rate'] =
#df['construction_permits_rate'] =

if __name__ == '__main__':
    df = make_rates(make_base_table())
