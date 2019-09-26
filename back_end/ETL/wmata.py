import utils
import requests
import pandas as pd
from operator import itemgetter

def get_bus_stops():
    data = requests.get('https://api.wmata.com/Bus.svc/json/jStops',
        params={'api_key': utils.get_credentials('wmata-api-key')})
    return pd.DataFrame(data.json()['Stops'])

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
