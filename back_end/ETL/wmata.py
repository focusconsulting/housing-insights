'''
wmata.py
--------

This file contains code to create the following tables:
    Table      | Columns
    -------------------------------------------------------------------
    wmata_dist | nlihc_id, dist_in_miles, type, stop_id_or_station_code
    wmata_info | stop_id_or_station_code, lines
    wmata_json | Copy of open data dc geojson as text.

They are used in the project view.
'''
import requests
import pandas as pd
import geopandas as gp

from . import utils
from operator import itemgetter
from math import radians, cos, sin, asin, sqrt

def make_wmata_tables(engine):
    df = pd.read_sql('SELECT nlihc_id, latitude, longitude FROM new_project;',
            engine)
    df = utils.make_df_geo_df(df, 'longitude', 'latitude')
    transit = get_transit_locations()
    print(transit.head())
    print(transit.columns)
    make_wmata_info(transit, engine)
    make_wmata_dist(df, transit, engine)

def make_wmata_dist(df, transit, engine):
    '''
    Makes the table wmata_dist. Each row is a project and station that are
    within half a mile of eachother.
    '''
    merged = gp.sjoin(df, transit, how='left', op='within')
    print(merged.head())
    merged = merged[
        ['nlihc_id', 'latitude', 'longitude', 'Name',
            'type', 'stop_id_or_station_code', 'Lines', 'Lat', 'Lon']]
    merged['dist_in_miles'] = merged.apply(haversine, axis=1)
    merged = merged[['nlihc_id', 'type', 'stop_id_or_station_code', 'dist_in_miles']]
    return utils.write_table(merged, 'new_wmata_dist', engine)

def make_wmata_info(df, engine):
    '''Loads the wmata_info table into the database.'''
    df.columns = df.columns.str.lower()
    df = df.rename(columns={
        'lat': 'latitude', 'lon': 'longitude'})
    df = df[['stop_id_or_station_code', 'lines', 'name', 'latitude', 'longitude']]
    return utils.write_table(df, 'new_wmata_info', engine)

def haversine(row):
    '''
    Calculate the great circle distance between two points
    on the Earth (specified in decimal degrees).

    Meant to be applied to a dataframe.
    '''
    # convert decimal degrees to radians
    project_lon, project_lat, station_lon, station_lat = \
        map(radians, [row.longitude, row.latitude, row.Lon, row.Lat])

    # Haversine formula
    d_lon = station_lon - project_lon
    d_lat = station_lat - project_lat
    a = sin(d_lat/2)**2 + cos(project_lat) * cos(station_lat) * sin(d_lon/2)**2
    return (2 * asin(sqrt(a))) * 3956 # Radius of earth in miles

def get_transit_locations():
    '''Grabs bus stops and rail stations.'''
    data = requests.get('https://api.wmata.com/Bus.svc/json/jStops',
        params={'api_key': utils.get_credentials('wmata-api-key')})
    bus = pd.DataFrame(data.json()['Stops'])
    bus['type'] = 'bus'
    bus['Lines'] = bus['Routes'].str.replace('[','')
    bus = bus.rename(columns={'StopID': 'stop_id_or_station_code'})

    rail = get_rail_stations()
    rail['type'] = 'rail'
    rail['Lines'] = rail['Code']
    rail = rail.rename(columns={'Code': 'stop_id_or_station_code'})
    df = pd.concat([
        bus[['stop_id_or_station_code', 'Name', 'type', 'Lines', 'Lat', 'Lon']],
        rail[['stop_id_or_station_code', 'Name', 'type', 'Lines', 'Lat', 'Lon']]
    ])
    df = utils.make_df_geo_df(df, 'Lon', 'Lat')
    df.geometry = df.buffer((1/(69*2)))
    return df

def get_rail_stations():
    data = requests.get('https://api.wmata.com/Rail.svc/json/jStations',
        params={'api_key': utils.get_credentials('wmata-api-key')})
    cols = ['Code', 'Name', 'Lat', 'Lon'] + [f'LineCode{n}' for n in range(1,5)]
    g = itemgetter(*cols)
    df = pd.DataFrame([g(d) for d in data.json()['Stations']], columns=cols)
    df['Lines'] = df.apply(make_lines, axis=1)
    return df[['Code', 'Name', 'Lat', 'Lon', 'Lines']]

def make_lines(row):
    '''Given a row of the rail station df - this function concats the lines.'''
    output = ''
    for n in range(1, 5):
        if row[f'LineCode{n}']:
            output = output + row[f'LineCode{n}'] + ', '
    return output[:-2]

### ADDS NUMBER OF BUS STOPS DIRECTLY TO THE PROJECT TABLE
def get_bus_stops():
    '''Downloads all bus stops and makes a buffer of half a mile.'''
    data = requests.get('https://api.wmata.com/Bus.svc/json/jStops',
        params={'api_key': utils.get_credentials('wmata-api-key')})
    df = pd.DataFrame(data.json()['Stops'])
    df = utils.make_df_geo_df(df, 'Lon', 'Lat')
    df.geometry = df.buffer((1/(69*2)))
    return df

def add_bus_stops(df, longitude_column, latitude_column):
    '''
    Takes in a dataframe and returns the nlihc_id and the number of
    bus stops within half a mile.
    '''
    df = utils.make_df_geo_df(df, longitude_column, latitude_column)
    bus = get_bus_stops()
    merged = gp.sjoin(df, bus, how='left', op='within')
    rv = merged['nlihc_id'].value_counts().reset_index()
    rv.columns = ['nlihc_id', 'bus_routes_nearby']
    return rv
