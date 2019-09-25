'''
make_zone_facts.py
------------------

This file creates the zone_facts table in the database, which is sent to
the front-end via /api/zone_facts/. It depends on the census data, crime
data, building permit data, and the geograpic boundaries.


It's a gross SQL query, but faster than loading it all into pandas.

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

def make_zone_facts(db):
    '''
    This function automatically makes the zone facts table with the newest
    crime and permit data. It requires that the crime, permit, and acs tables
    aleady exist.

    Must be passed in a SQLAlchemy database object from the application.
    '''
    try:
        db.session.execute('''
        DROP TABLE IF EXISTS new_zone_facts;
        CREATE TABLE new_zone_facts AS
        SELECT

            acs.zone_type,
            acs.zone,
            CAST(acs.population_in_poverty AS FLOAT)           / CAST(acs.total_population AS FLOAT) AS poverty_rate,
            CAST(acs.black_population AS FLOAT)                / CAST(acs.total_population AS FLOAT) AS fraction_black,
            CAST(acs.aggregate_household_income AS FLOAT)      / CAST(acs.total_population AS FLOAT) AS income_per_capita,
            CAST(acs.labor_force_population AS FLOAT)          / CAST(acs.total_population AS FLOAT) AS labor_participation,
            CAST(acs.foreign_born_population AS FLOAT)         / CAST(acs.total_population AS FLOAT) AS fraction_foreign,
            CAST(acs.single_mom_households AS FLOAT)           / CAST(acs.total_population AS FLOAT) AS fraction_single_mothers,
            CAST(acs.median_rent_quartile_in_dollars AS FLOAT) / CAST(acs.total_population AS FLOAT) AS acs_median_rent,

            CAST(new_crime.crime AS FLOAT)                     / CAST(acs.total_population AS FLOAT) AS crime_rate,
            CAST(new_crime.violent_crime AS FLOAT)             / CAST(acs.total_population AS FLOAT) AS violent_crime_rate,
            CAST(new_crime.non_violent_crime AS FLOAT)         / CAST(acs.total_population AS FLOAT) AS non_violent_crime_rate,

            new_permit.total_permits,
            new_permit.construction_permits

        FROM acs
   LEFT JOIN new_crime
          ON acs.zone = new_crime.zone AND acs.zone_type = new_crime.zone_type
   LEFT JOIN new_permit
          ON acs.zone = new_permit.zone AND acs.zone_type = new_permit.zone_type;
      COMMIT;
        ''')
        return True
    except:
        return False

