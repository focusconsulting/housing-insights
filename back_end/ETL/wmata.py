#import utils
from . import utils
import requests
import pandas as pd
import geopandas as gp
from operator import itemgetter

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

def get_rail_stations():
    data = requests.get('https://api.wmata.com/Rail.svc/json/jStations',
        params={'api_key': utils.get_credentials('wmata-api-key')})
    cols = ['Code', 'Name', 'Lat', 'Lon']
    g = itemgetter(*cols)
    return pd.DataFrame([g(d) for d in data.json()['Stations']], columns=cols)

def load_transit_data(engine):
    '''Loads the data to the DB. Returns a tuple of booleans.'''
    return (
        utils.write_table(get_bus_stops, 'bus_stops', engine),
        utils.write_table(get_rail_stations, 'rail_stations', engine)
    )
