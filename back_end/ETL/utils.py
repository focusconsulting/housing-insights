'''
utils.py
--------

This file has helper functions for loading and cleaning data.
'''
import re
import yaml
import datetime
import numpy as np
import pandas as pd
import geopandas as gp
import psycopg2
from shapely.geometry import Point
from psycopg2.extras import RealDictCursor

S3 = 'https://housing-insights.s3.amazonaws.com/'

def get_db_connection():
    return psycopg2.connect(
        database=get_credentials('database'),
        user=get_credentials('user'),
        password=get_credentials('password'),
        host=get_credentials('host'),
        port=get_credentials('port')
    )

def basic_query(query):
    '''Performs a basic query on the database, returns a list of tuples.'''
    with get_db_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            result = cur.fetchall()
    return result

def write_table(df, table_name, engine):
    '''
    Writes a dataframe to the specified table and database.

    Input: df - A DataFrame.
           table_name - The intended database table as a string.
           engine - The sqlalchemy engine of the database.
    Returns True or False (Success or Failure)
    '''
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        return True
    except:
        return False

def get_credentials(keys):
    '''
    Returns the credientials for the keys given.

    Input: keys a string of a single key, or a list of strings.
    Returns A string or list of strings of credentials.
    '''
    with open('./secrets.yml', 'r') as secrets:
        d = yaml.safe_load(secrets)
    if isinstance(keys, str):
        return d[keys]
    if not isinstance(keys, list):
        raise ValueError("Keys must be a string or list of strings.")
    return [d[key] for key in keys]

def filter_date(df, column):
    '''Returns observations within the past year.'''
    df[column] = pd.to_datetime(df[column].str.slice(0,10))
    return df[df[column] > year_ago()]

def fix_tract(tract_number):
    '''Makes a tract number a string of length six with leading zeroes.'''
    if not tract_number or np.isnan(tract_number):
        return '99999'
    tract_number = str(int(tract_number))
    return tract_number.zfill(6)

def just_digits(column):
    column = column.astype(str)
    return column.apply(lambda s: re.sub('[^0-9]', '', s).strip())

def get_years():
    '''Returns this year and last year as integers.'''
    this_year = datetime.datetime.now().year
    return this_year, this_year - 1

def year_ago():
    '''Returns the datetime for a year ago.'''
    return datetime.datetime.now() - datetime.timedelta(days=365)

def get_paths_for_data(data_category, years):
    '''
    Returns the data download paths for a data category for the given years.

    data_category: A string of the data_category (ex. crime).
    years: An iterable of years as integers.
    '''
    df = pd.read_excel(S3+'data_sources.xlsx')
    return (df[(df.data_category == data_category) &
               (df.year.isin(years))]["url"].to_list())

def make_df_geo_df(df, longitude_column, latitude_column):
    '''Makes a dataframe a geodataframe.'''
    return gp.GeoDataFrame(df,
        geometry=[Point(xy) for xy in zip(df[longitude_column], df[latitude_column])]
    )

def get_census_tract_for_data(df, longitude_column, latitude_column):
    '''Returns the data frame with a new column "tract".'''
    df = make_df_geo_df(df, longitude_column, latitude_column)

    # Grab census tract geometries from open data DC.
    census_tracts_dc = gp.read_file(
        'https://opendata.arcgis.com/datasets/6969dd63c5cb4d6aa32f15effb8311f3_8.geojson'
        )[['TRACT', 'geometry']]
    census_tracts_dc.columns = census_tracts_dc.columns.str.lower()

    # Align spatial projects and join where the projects' point
    # geometries are within the census tracts' polygon geometries.
    df.crs = census_tracts_dc.crs
    return gp.sjoin(df, census_tracts_dc, op='within', how='left')

def get_cluster_for_data(df, longitude_column, latitude_column):
    '''Returns the data frame with a new column "neighborhood_cluster".'''
    df = make_df_geo_df(df, longitude_column, latitude_column)

    # Grab census tract geometries from open data DC.
    cluster_file = gp.read_file(
        'https://opendata.arcgis.com/datasets/f6c703ebe2534fc3800609a07bad8f5b_17.geojson'
    )
    cluster_file = cluster_file[['NAME', 'NBH_NAMES', 'geometry']]
    cluster_file.columns = ['neighborhood_cluster', 'neighborhood_cluster_desc', 'geometry']

    # Align spatial projects and join where the projects' point
    # geometries are within the census tracts' polygon geometries.
    df.crs = cluster_file.crs
    return gp.sjoin(df, cluster_file, op='within', how='left')
