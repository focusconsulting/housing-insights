'''
wmata_helper.py
---------------

This file assists in formating the output for the wmata API route.
'''
from . import utils

def wmata_helper(results):
    '''
    Returns 5 data structures needed for the wmata API route.
        - stops:
        - bus_routes:
        - rail_routes:
        - bus_routes_grouped:
        - rail_routes_grouped:
    '''
    stops = make_stops(results)
    bus_routes, bus_grouped = make_routes(stops['bus'])
    rail_routes, rail_grouped = make_routes(stops['rail'])
    return {'stops': stops,
            'bus_routes': bus_routes,
            'rail_routes': rail_routes,
            'bus_routes_grouped': bus_grouped,
            'rail_routes_grouped': rail_grouped}

def make_stops(results):
    '''
    Takes in a list of stops. Bus and Rail stops.
    For each stop:
        - dist_in_miles
        - routes (lines)
        - stop_id_or_station_code
        - type
    '''
    bus, rail = list(), list()
    for row in results:
        row['routes'] = row['lines'].split(', ')
        if row['type'] == 'bus':
            bus.append(row)
        else:
            rail.append(row)
    return {'bus': bus, 'rail': rail}

def make_routes(stops):
    '''Makes the routes and routes_grouped data structure for the API route.'''
    routes_out = dict() 
    grouped_out = list()
    for stop in stops:
        for route in stop['routes']:
            routes_out[route] = {'route': route,
                                 'shortest_dist': stop['dist_in_miles']}
        grouped_out.append({'routes': stop['routes'],
                            'shortest_dist': stop['dist_in_miles']})
    return routes_out, grouped_out
