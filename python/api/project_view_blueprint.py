from flask import Blueprint
from flask import jsonify, request
import math
from flask_cors import cross_origin


def construct_project_view_blueprint(name, engine):

    blueprint = Blueprint(name, __name__, url_prefix='/api')

    @blueprint.route('/assets/<nlihc_id>', methods=['GET'])
    @cross_origin()
    def nearby_assets(nlihc_id):
        '''
        Returns nearby asssets
        '''
        conn = engine.connect()
        try:
            q = """
                SELECT dist_in_miles, type, asset_name, asset_lat, asset_lon
                FROM asset_dist
                WHERE nlihc_id = '{}'
                """.format(nlihc_id)
            assets = conn.execute(q).fetchall()
            results = {}
            for asset in assets:
                category_name = asset[1]
                asset_name = asset[2]
                asset_latitude = asset[3]
                asset_longitude = asset[4]
                asset_dist = asset[0]
                asset_processed = {
                    'asset_name': asset_name,
                    'longitude': asset_longitude,
                    'latitude': asset_latitude,
                    'distance_in_miles': asset_dist
                }
                if category_name in results:
                    results[category_name].append(asset_processed)
                else:
                    results[category_name] = []
                    results[category_name].append(asset_processed)
        except Exception as e:
            conn.close()
            print("failed to fetch assets", e)
        finally:
            conn.close()
        return jsonify({'objects': results})
        


    @blueprint.route('/wmata/<nlihc_id>',  methods=['GET'])
    @cross_origin()
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

            #Parse the : separated objects
            routes = ':'.join(routes)
            routes = routes.split(':')
            unique = list(set(routes))
            return unique


    @blueprint.route('/building_permits/<dist>', methods=['GET'])
    @cross_origin()
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
            ,zip
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
            'objects': good_results
            , 'tot_permits':tot_permits
            , 'distance': dist
        }

        output_json = jsonify(output)

        conn.close()
        return output_json



    @blueprint.route('/projects/<dist>', methods=['GET'])
    @cross_origin()
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
        unit_counts = filter(None, unit_counts) #can't sum None
        unit_counts = [int(u) for u in unit_counts] #temporarily needed b/c accidentally stored as text
        tot_units = sum(unit_counts)
        tot_buildings = len(good_results)

        output = {
            'objects': good_results,
            'tot_units': tot_units,
            'tot_buildings': tot_buildings,
            'distance': dist
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
        original_coords = (lat1, lon1, lat2, lon2) # for debugging
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

    @blueprint.route('/project/<nlihc_id>/subsidies/', methods=['GET'])
    @cross_origin()
    def project_subsidies(nlihc_id):
        q = """
            SELECT * FROM subsidy
            WHERE nlihc_id = '{}'
            """.format(nlihc_id)

        conn = engine.connect()
        proxy = conn.execute(q)
        results = [dict(x) for x in proxy.fetchall()]
        conn.close()
        output = {'objects': results}
        return jsonify(output)

    return blueprint
