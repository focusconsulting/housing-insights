'''
make_zone_facts.py
------------------

This file creates the zone_facts table in the database, which is sent to
the front-end via /api/zone_facts/. It depends on the census data, crime
data, and the geograpic boundaries. The output columns for this file are:

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
from sources import get_acs_data, get_crime_data

acs = get_acs_data()
crime = get_crime_data()

#permits = get_permit_data()


acs.merge(get_crime_for_year(crime_2019), left_on='tract', right_on='census_tract').head()


# TODO - Building Permit Data: Depends on MAR
#building_permits = pd.read_csv('https://opendata.arcgis.com/datasets/52e671890cb445eba9023313b1a85804_8.csv')
#building_permits.columns = building_permits.columns.str.lower()
#building_permits[['maraddressrepositoryid', 'permit_type_name']].head()
#building_permits['permit_type_name'].apply(lambda x: 1 if x == 'CONSTRUCTION' else 0).head()
