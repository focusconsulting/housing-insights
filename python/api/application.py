# -*- coding: utf-8 -*-

"""
flask api
~~~~~~~~~
This is a simple Flask applicationlication that creates SQL query endpoints.

"""

from flask import Flask, request, Response, abort, json

import psycopg2
from sqlalchemy import create_engine

import logging
from flask_cors import CORS, cross_origin

import math
import sys

#Different json output methods.
# Currently looks like best pick is jsonify, but with the simplejson package pip-installed so that
# jsonify will uitilize simplejson's decimal conversion ability.
import json
import simplejson
from flask import jsonify
from flask.json import JSONEncoder
import calendar
from datetime import datetime, date

#######################
# Setup
#######################
logging.basicConfig(level=logging.DEBUG)
application = Flask(__name__)


class CustomJSONEncoder(JSONEncoder):
# uses datetime override http://flask.pocoo.org/snippets/119/
    def default(self, obj):
        try:
            if isinstance(obj,date):
                return datetime.strftime(obj,'%Y-%m-%d')
            if isinstance(obj, datetime):
                return datetime.strftime(obj,'%Y-%m-%d')
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

#apply the custom encoder to the app. All jsonify calls will use this method
application.json_encoder = CustomJSONEncoder


#Allow cross-origin requests. TODO should eventually lock down the permissions on this a bit more strictly, though only allowing GET requests is a good start.
CORS(application, resources={r"/api/*": {"origins": "*"}}, methods=['GET'])

#Allow us to test locally if desired
if 'docker' in sys.argv:
    database_choice = 'docker_database'
else:
    database_choice = 'remote_database'

with open('secrets.json') as f:
    secrets = json.load(f)
    connect_str = secrets[database_choice]['connect_str']


#Should create a new connection each time a separate query is needed so that API can recover from bad queries
#Engine is used to create connections in the below methods
engine = create_engine(connect_str)

#Establish a list of tables so that we can validate queries before executing
conn = engine.connect()
q = "SELECT tablename FROM pg_catalog.pg_tables where schemaname = 'public'"
proxy = conn.execute(q)
results = proxy.fetchall()
tables = [x[0] for x in results]
application.logger.debug('Tables available: {}'.format(tables))
conn.close()
logging.info(tables)

##########################################
# API Endpoints
##########################################

@application.route('/')
def hello():
    return("The Housing Insights API Rules!")

@application.route('/api/filter/', methods=['GET'])
def filter_data():
    q = """
        select p.nlihc_id
          , p.proj_units_tot
          , p.proj_units_assist_max
          , cast(p.proj_units_assist_max / p.proj_units_tot as decimal(3,2)) as percent_affordable_housing
          , p.hud_own_type
          , p.ward
          , p.anc
          , p.census_tract
          , p.neighborhood_cluster
          , p.neighborhood_cluster_desc
          , p.zip
          , c.acs_median_rent
          , s.portfolio
          , s.agency
          , to_char(s.poa_start, 'YYYY-MM-DD') as poa_start
          , to_char(s.poa_end, 'YYYY-MM-DD') as poa_end
          , s.units_assist
          , s.subsidy_id
        from project as p
        left join census as c on c.census_tract = p.census_tract and c.unique_data_id = 'acs_rent_median_15_5YR'
        left join subsidy as s on s.nlihc_id = p.nlihc_id
        """

    conn = engine.connect()
    proxy = conn.execute(q)
    results = [dict(x) for x in proxy.fetchall()]
    conn.close()
    output = {'items':results}
    return jsonify(output)


@application.route('/api/raw/<table>', methods=['GET'])
@cross_origin()
def list_all(table):
    """ Generate endpoint to list all data in the tables. """

    application.logger.debug('Table selected: {}'.format(table))
    if table not in tables:
        application.logger.error('Error:  Table does not exist.')
        abort(404)

    #Query the database
    conn = engine.connect()
    q = 'SELECT row_to_json({}) from {} limit 1000;'.format(table, table)
    proxy = conn.execute(q)
    results = [x[0] for x in proxy.fetchmany(1000)] # Only fetching 1000 for now, need to implement scrolling
    #print(results)
    conn.close()

    return jsonify(items=results)

@application.route('/api/meta', methods=['GET'])
def get_meta():
    '''
    Outputs the meta.json to the front end
    '''

    conn = engine.connect()
    result = conn.execute("SELECT meta FROM meta")
    row = result.fetchone()
    return row[0]


@application.route('/api/<data_source>/all/<grouping>', methods=['GET'])
def count_all(data_source,grouping):
    """ Example endpoint of doing a COUNT on a specific zipcode. """


    #input validation so users only execute valid queries
    if grouping not in ['zipcode','ward','anc', 'neighborhood_cluster']:
        return jsonify({'items': None})
    if data_source not in ['building_permits', 'crime']:
        return jsonify({'items': None})


    application.logger.debug('Getting all {}'.format(grouping))

    #Determine some parameters based on user submissions
    #TODO this approach will get unwieldy soon - temporary quick approach
    #date field name varies by data_source
    date_fields = {'building_permits': 'issue_date', 'crime': 'report_date'}
    date_field = date_fields[data_source]
    fallback = "'Unknown'"

    try:
        #TODO verify if this is auto-closed if the transaction errors out. Or does it matter?
        conn = engine.connect()

        q = """
            SELECT COALESCE({},{}) --'Unknown'
            ,count(*) AS records
            FROM {}
            where {} between '2016-01-01' and '2016-12-31'
            --WHERE report_date BETWEEN (now()::TIMESTAMP - INTERVAL '1 year') AND now()::TIMESTAMP
            GROUP BY {}
            ORDER BY {}
            """.format(grouping,fallback,data_source,date_field,grouping,grouping)

        proxy = conn.execute(q)
        results = proxy.fetchall()

        #transform the results.
        #TODO should come up with a better generic way to do this using column
          #names for any arbitrary sql table results.
        formatted = []
        for x in results:
            dictionary = dict({'group':x[0], 'count':x[1]})
            formatted.append(dictionary)


        conn.close()
        return jsonify({'items': formatted, 'grouping':grouping, 'data_id':data_source})

    #TODO do better error handling - for interim development purposes only
    except Exception as e:
        #conn.close()
        return "Query failed: {}".format(e)

@application.route('/api/wmata/<nlihc_id>',  methods=['GET'])
def nearby_transit(nlihc_id):
    '''
    Returns the nearby bus and metro routes and stops.
    Currently this assumes that all entries in the wmata_dist
    table are those that have a walking distance of 0.5 miles
    or less. We may later want to implement functionality to
    filter this to those with less distance.
    '''

    conn = engine.connect()
    try:
        q = """
            SELECT dist_in_miles, type, stop_id_or_station_code
            FROM wmata_dist
            WHERE nlihc_id = '{}'
            """.format(nlihc_id)

        proxy = conn.execute(q)
        results = proxy.fetchall()

        #transform the results.
        stops = {'bus':[],'rail':[]};
        rail_stops = []; bus_stops = [];
        bus_routes = {}; rail_routes = {};

        for x in results:
            #reformat the data into appropriate json
            dist = str(x[0])
            typ = x[1]
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

    except Exception as e:
        raise e
        return "Query failed: {}".format(e)


def idx_from_ld(lst,key,value):
    '''
    Takes a list of dictionaries and returns the dictionary
    entry matching the key and value supplied
    Used for data forms like this: [{'foo':'bar'},{'foo':'asdf'}]
    '''
    for idx, dic in enumerate(lst):
        if dic[key] == value:
            return idx
    return None

def unique_transit_routes(stop_ids):
    if len(stop_ids) == 0:
        return []
    else:
        #Second query to get the unique transit lines
        q_list = str(stop_ids).replace('[','(').replace(']',')')
        q = """
            SELECT lines FROM wmata_info
            WHERE stop_id_or_station_code in {}
            """.format(q_list)
        conn = engine.connect()
        proxy = conn.execute(q)
        routes = [x[0] for x in proxy.fetchall()]
        conn.close()

        #Parse the : separated items
        routes = ':'.join(routes)
        routes = routes.split(':')
        unique = list(set(routes))
        return unique


@application.route('/api/building_permits/<dist>', methods=['GET'])
def nearby_building_permits(dist):

    conn = engine.connect()
    #Get our params
    dist = float(dist)
    latitude = request.args.get('latitude',None)
    longitude = request.args.get('longitude',None)
    if latitude == None or longitude==None:
        return "Please supply latitude and longitude"
    else:
        latitude=float(latitude)
        longitude=float(longitude)

    latitude_tolerance, longitude_tolerance = bounding_box(dist, latitude, longitude)

    #Return just a subset of columns to lighten the data load. TODO do we want user option for short/all?
    q = '''
        SELECT
        (latitude - {latitude} ) AS lat_diff
        ,(longitude - {longitude} ) AS lon_diff
        ,latitude
        ,longitude
        ,ward
        ,neighborhood_cluster
        ,anc
        --,census_tract --not yet available
        ,zipcode
        ,permit_type_name
        ,permit_subtype_name
        ,full_address
        ,objectid

        FROM building_permits

        WHERE latitude < ({latitude} + {latitude_tolerance})::DECIMAL
        AND   latitude > ({latitude} - {latitude_tolerance})::DECIMAL
        AND   longitude < ({longitude} + {longitude_tolerance})::DECIMAL
        AND   longitude > ({longitude} - {longitude_tolerance})::DECIMAL

        AND issue_date BETWEEN (now()::TIMESTAMP - INTERVAL '1 year') AND now()::TIMESTAMP

    '''.format(
        latitude=latitude,
        longitude=longitude,
        latitude_tolerance=latitude_tolerance,
        longitude_tolerance=longitude_tolerance
    )

    proxy = conn.execute(q)
    results = proxy.fetchall()

    good_results = [dict(r) for r in results if haversine(latitude, longitude, float(r.latitude), float(r.longitude)) <= dist]

    tot_permits = len(good_results)

    output = {
        'items': good_results
        , 'tot_permits':tot_permits
        , 'distance': dist
    }

    output_json = jsonify(output)

    conn.close()
    return output_json



@application.route('/api/projects/<dist>', methods=['GET'])
def nearby_projects(dist):

    conn = engine.connect()
    dist = float(dist)
    #Get our params
    latitude = request.args.get('latitude',None)
    longitude = request.args.get('longitude',None)
    if latitude == None or longitude==None:
        return "Please supply latitude and longitude"
    else:
        latitude=float(latitude)
        longitude=float(longitude)

    latitude_tolerance, longitude_tolerance = bounding_box(dist, latitude, longitude)

    q = '''
        SELECT
        (latitude - {latitude} ) AS lat_diff
        ,(longitude - {longitude} ) AS lon_diff
        ,*
        FROM project

        WHERE latitude < ({latitude} + {latitude_tolerance})::DECIMAL
        AND   latitude > ({latitude} - {latitude_tolerance})::DECIMAL
        AND   longitude < ({longitude} + {longitude_tolerance})::DECIMAL
        AND   longitude > ({longitude} - {longitude_tolerance})::DECIMAL

        AND status = 'Active'

    '''.format(
        latitude=latitude,
        longitude=longitude,
        latitude_tolerance=latitude_tolerance,
        longitude_tolerance=longitude_tolerance
    )

    proxy = conn.execute(q)
    results = proxy.fetchall()

    good_results = [dict(r) for r in results if haversine(latitude, longitude, float(r.latitude), float(r.longitude)) <= dist]

    unit_counts = [r['proj_units_assist_max'] for r in good_results]
    unit_counts = filter(None,unit_counts) #can't sum None
    unit_counts = [int(u) for u in unit_counts] #temporarily needed b/c accidentally stored as text
    tot_units = sum(unit_counts)
    tot_buildings = len(good_results)

    output = {
        'items': good_results
        ,'tot_units': tot_units
        , 'tot_buildings':tot_buildings
        , 'distance': dist
    }

    conn.close()
    output_json = jsonify(output)
    return output_json


#def haversine(lat1, long1, lat2, long2):
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2,lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    original_coords = (lat1,lon1,lat2,lon2) #for debugging
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956 # Radius of earth in miles
    d = c * r
    #print("Haversine for {} = {}".format(original_coords,d))
    return c * r


def bounding_box(dist, latitude, longitude):
    """ Cribbed from https://gis.stackexchange.com/questions/142326/calculating-longitude-length-in-miles """

    radius = 3959 # miles, from google

    dlat_rad = 69 * dist / radius  # google again

    latitude_tolerance = dist / 69
    longitude_tolerance = dist / (math.cos(latitude) * 69.172)

    return (latitude_tolerance, longitude_tolerance)


@application.route('/api/project/<nlihc_id>/subsidies/', methods=['GET'])
def project_subsidies(nlihc_id):
    q = """
        SELECT * FROM subsidy
        WHERE nlihc_id = '{}'
        """.format(nlihc_id)

    conn = engine.connect()
    proxy = conn.execute(q)
    results = [dict(x) for x in proxy.fetchall()]
    conn.close()
    output = {'items':results}
    return jsonify(output)

@application.route('/api/census/<data_id>/<grouping>', methods=['GET'])
def census_with_weighting(data_id,grouping):
    #TODO this does not yet return the proper grouping
    
    #TODO when we add more than one year of data we need to use a newly added 'year' column to distinguish the rows and update the sql query.
    q = "SELECT * FROM census"
    conn = engine.connect()
    proxy = conn.execute(q)
    census_results = [dict(x) for x in proxy.fetchall()]

    q = "SELECT * FROM census_tract_to_neighborhood_cluster"
    conn = engine.connect()
    proxy = conn.execute(q)
    nc_weighting = [dict(x) for x in proxy.fetchall()]

    q = "SELECT * FROM census_tract_to_ward"
    conn = engine.connect()
    proxy = conn.execute(q)
    ward_weighting = [dict(x) for x in proxy.fetchall()]

    conn.close()

    #perform the proper calculation
    items = []
    if data_id == 'poverty_rate':
        for r in census_results:
            pop = r['population']
            pop_poverty = r['population_poverty']
            rate = (pop_poverty / pop)*100
            output = dict({'group':r['census_tract'], 'count':rate})
            items.append(output)

    return jsonify({'items': items, 'grouping':grouping, 'data_id':data_id})



##########################################
# Start the app
##########################################

if __name__ == "__main__":
    try:
        application.run(host="0.0.0.0", debug=True)
    except:
        conn.close()
