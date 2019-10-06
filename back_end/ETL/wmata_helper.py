'''
wmata_helper.py
---------------

This file assists in formating the output for the wmata API route.

'''
from . import utils

def wmata_helper(results):
    '''
    Data: List of tuples - dist, nlihc_id, stop_id, type

    Returns: 5 dictionaries.
        - stops:
        - bus_routes:
        - rail_routes:
        - bus_routes_grouped:
        - rail_routes_grouped:
    '''
    stops = make_stops()
    bus_routes = make_bus_routes()
    rail_routes = make_rail_routes()
    bus_routes_grouped = make_bus_routes_grouped()
    rail_routes_grouped = make_rail_routes_grouped()

def make_stops(stops):
    '''
    Takes in a list of stops.

    Contains two dictionaries. Bus and Rail.

    For each stop:
        - dist_in_miles
        - routes (lines)
        - stop_id_or_station_code
        - type
    '''
    utils.basic_query('''
        SELECT stop_id_or_station_code, lines
        FROM new_wmata_info
        WHERE stop_id_or_station_code IN ({}); 
        '''.format(stops)
    return None 

def make_bus_routes():
    pass

def make_rail_routes():
    pass

def make_bus_routes_grouped():
    pass

def make_rail_routes_grouped():
    pass


    '''

    #transform the results.
    stops = {'bus':[],'rail':[]};
    rail_stops = []; bus_stops = [];
    bus_routes = {}; rail_routes = {};

    for x in results:
        #reformat the data into appropriate json
        dist = str(x[0])
        typ = x[3]
        stop_id = x[2]
        routes = unique_transit_routes([stop_id])

        stop_dict = dict({'dist_in_miles':dist,
                        'type':typ,
                        'stop_id_or_station_code':stop_id,
                        'routes':routes
                        })

        #Calculate summary statistics for ease of use
        if typ == 'bus':
            stops['bus'].append(stop_dict)
            bus_stops.append(stop_id)

            #Add all unique routes to a master list, with the shortest walking distance to that route
            for route in routes:
                if route not in bus_routes:
                    bus_routes[route] = {'route':route,'shortest_dist':10000}
                if float(dist) < float(bus_routes[route]['shortest_dist']):
                    bus_routes[route]['shortest_dist'] = dist

        if typ == 'rail':
            stops['rail'].append(stop_dict)
            rail_stops.append(stop_id)

            #Add all unique routes to a master list, with the shortest walking distance to that route
            #TODO refactor this into reusable function
            for route in routes:
                if route not in rail_routes:
                    rail_routes[route] = {'route':route,'shortest_dist':10000}
                if float(dist) < float(rail_routes[route]['shortest_dist']):
                    rail_routes[route]['shortest_dist'] = dist

    #TODO - might be easier to approach this by using separate variables and then repackaging into the desired output format at the end?
    #Rearrange the bus routes into a groups of shortest distance for easier display on front end
    bus_routes_grouped = []
    for key in bus_routes:
        dist = bus_routes[key]['shortest_dist']
        idx = idx_from_ld(bus_routes_grouped,'shortest_dist',dist)
        if idx == None:
            bus_routes_grouped.append({"shortest_dist":dist, "routes":[]})
            idx = idx_from_ld(bus_routes_grouped,'shortest_dist',dist)
        bus_routes_grouped[idx]['routes'].append(key)

    #Rearrange rail
    rail_routes_grouped = []
    for key in rail_routes:
        dist = rail_routes[key]['shortest_dist']
        idx = idx_from_ld(rail_routes_grouped,'shortest_dist',dist)
        if idx == None:
            rail_routes_grouped.append({"shortest_dist":dist, "routes":[]})
            idx = idx_from_ld(rail_routes_grouped,'shortest_dist',dist)
        rail_routes_grouped[idx]['routes'].append(key)

    #TODO would be good to sort rail_routes_grouped and bus_routes_grouped before delivery (currently sorting on the front end)

    conn.close()
    return jsonify({'stops':stops,
                    'bus_routes':bus_routes,
                    'rail_routes':rail_routes,
                    'bus_routes_grouped':bus_routes_grouped,
                    'rail_routes_grouped':rail_routes_grouped
                    })
                    '''
