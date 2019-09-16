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

S3 = 'https://housing-insights.s3.amazonaws.com/'

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

def fix_tract(tract_number):
    '''Makes a tract number a string of length six with leading zeroes.'''
    if not tract_number or np.isnan(tract_number):
        return '99999'
    tract_number = str(int(tract_number))
    while len(tract_number) < 6:
        tract_number = '0' + tract_number
    return tract_number

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

def get_census_tract_for_data(df, longitude_column, latitude_column):
    '''Returns the data frame with a new column "tract".'''
    df = gp.GeoDataFrame(df,
        geometry=gp.points_from_xy(df[longitude_column], df[latitude_column])
    )

    # Grab census tract geometries from open data DC.
    census_tracts_dc = gp.read_file(
        ('https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/'
         'Demographic_WebMercator/MapServer/8/query?where=1%3D1&outFields='
         'TRACT,Shape,GEOID,Shape_Length,Shape_Area&outSR=4326&f=json')
    )
    census_tracts_dc.columns = census_tracts_dc.columns.str.lower()

    # Align spatial projects and join where the projects' point
    # geometries are within the census tracts' polygon geometries.
    df.crs = census_tracts_dc.crs
    return gp.sjoin(df, census_tracts_dc, op='within', how='left')

def get_cluster_for_data(df, longitude_column, latitude_column):
    '''Returns the data frame with a new column "neighborhood_cluster".'''
    df = gp.GeoDataFrame(df,
        geometry=gp.points_from_xy(df[longitude_column], df[latitude_column])
    )

    # Grab census tract geometries from open data DC.
    cluster_file = gp.read_file(
        ('https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/'
         'Administrative_Other_Boundaries_WebMercator/MapServer/17/'
         'query?where=1%3D1&outFields=NAME,Shape,Shape_Length,'
         'Shape_Area&outSR=4326&f=json')
    )

    cluster_file.columns = cluster_file.columns.str.lower()
    cluster_file = cluster_file.rename({'name': 'neighborhood_cluster'})

    # Align spatial projects and join where the projects' point
    # geometries are within the census tracts' polygon geometries.
    df.crs = cluster_file.crs
    return gp.sjoin(df, cluster_file, op='within', how='left')

