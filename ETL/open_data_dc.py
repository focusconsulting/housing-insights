'''
    open_data_dc.py
    ---------------

    This file creates the 'building_permits', 'crime', 'dc_tax', and 'mar'
    database tables. Documentation for each dataset can be found on opendata.dc.gov
    and the ETL README.

    To load the data, this file:

        1. Connects to the database.
        2. Drops and recreates the database table.
        3. Places relevant years of data to the database tables.

    As the actual source data is hosted on arcgis under patternless urls,
    this file will need to be updated each year with the convention set below.
    This will most likely change (some sort of ingestion file could be
    created).

    TODO: DCHousing dataset.
'''
import requests
import psycopg2
import pandas as pd

base = 'https://opendata.arcgis.com/datasets/'
mapping = {

    # Building Permit Data
    'building_permits': {
        2019: '52e671890cb445eba9023313b1a85804_8.csv',
        2018: '42cbd10c2d6848858374facb06135970_9.csv',
        2017: '81a359c031464c53af6230338dbc848e_37.csv',
        2016: '5d14ae7dcd1544878c54e61edda489c3_24.csv',
        # Add years here...
    },

    # Crime Data 
    'crime': {
        2019: 'f08294e5286141c293e9202fcd3e8b57_1.csv',
        2018: '38ba41dd74354563bce28a359b59324e_0.csv',
        2017: '6af5cb8dc38e4bcbac8168b27ee104aa_38.csv',
        2016: 'bda20763840448b58f8383bae800a843_26.csv',
        # Add years here...
    },

    # Tax Data. Seems to update every year. 
    'dc_tax': {
        2019: '496533836db640bcade61dd9078b0d63_53.csv',
    },

    # Master Address Repository: https://opendata.dc.gov/datasets/address-points
    'mar': {
        2019: 'aa514416aaf74fdc94748f1e56e7cc8a_0.csv'
    },

    # 'Affordable Housing Data': Seems to update regularly. 
    # https://opendata.dc.gov/datasets/34ae3d3c9752434a8c03aca5deb550eb_62
    'dc_housing': {
        2019: '34ae3d3c9752434a8c03aca5deb550eb_62.csv'
    },
}

def get_data_for_table(table_name):
    """Downloads an ArcGIS dataset for a single year.

    Input: table_name (string) - The table name of the data you want.
    """

    # Get connection | Update this to change with config
    connection = psycopg2.connect(
        dbname='housinginsights_docker',
        user='codefordc',
        password='codefordc',
        host='postgres'
    )
    cursor = connection.cursor()

    try:
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

        for year in [2019]: # mapping[table_name].keys()):
            print(table_name, year)
            # Should there be a column designating the year?
            df = pd.read_csv(base+mapping[table_name][year])
            print(df.head())
            print(df.info(memory_usage='deep'))
            #.to_sql(table_name, if_exists='append')
        #cursor.commit()

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    for table in mapping.keys():
        get_data_for_table(table)
