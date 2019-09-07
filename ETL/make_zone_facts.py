'''
    make_zone_facts.py
    ------------------

    This file creates the zone_facts table in the database, which is sent to
    the front-end via /api/zone_facts/. It depends on the census data, crime
    data, and the geograpic boundaries. The output columns for this file are:

        - zone:                     Tract, neighborhood, or ward number.
        - zone_type:                Tract, neighborhood, or ward.
        - poverty_rate
        - fraction_black
        - income_per_capita
        - labor_participation
        - fraction_foreign
        - fraction_single_mothers
        - acs_lower_rent_quartile
        - acs_median_rent
        - acs_upper_rent_quartile
        - crime_count
        - violent_crime_count
        - non_violent_crime_count
        - crime_rate
        - violent_crime_rate
        - non_violent_crime_rate
        - residential_units
        - building_permits
        - building_permits_rate
        - construction_permits
        - construction_permits_rate
        - id
'''

import pandas as pd

# Load Census Data
