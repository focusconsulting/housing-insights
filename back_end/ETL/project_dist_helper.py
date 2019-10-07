'''
project_dist_helper.py
----------------------

This file collects projects within half a mile of a set of coordinates.

It is used by the projects route.

/projects/0.5?latitude=<>&longitude=<>
'''
from . import utils
import math
from math import radians, cos, sin, asin, sqrt

def nearby_projects(dist, latitude, longitude):

    latitude_tolerance, longitude_tolerance = bounding_box(dist, latitude, longitude)
    results = utils.basic_query(
    f'''
        SELECT *,
            (latitude - {latitude} ) AS lat_diff,
            (longitude - {longitude} ) AS lon_diff
        FROM new_project

        WHERE latitude < ({latitude} + {latitude_tolerance})::DECIMAL
        AND   latitude > ({latitude} - {latitude_tolerance})::DECIMAL
        AND   longitude < ({longitude} + {longitude_tolerance})::DECIMAL
        AND   longitude > ({longitude} - {longitude_tolerance})::DECIMAL;
    ''')
    
    good_results = list(filter(lambda r: haversine(latitude, longitude, 
        float(r['latitude']), float(r['longitude'])) <= dist, results))
    unit_counts = [r.get('proj_units_assist_max', 0) for r in good_results]

    return {
        'distance': dist,
        'objects': good_results,
        'tot_units': sum(map(unit_helper, good_results)),
        'tot_buildings': len(good_results),
    }

def unit_helper(row):
    '''Returns the number of units if it is a number, 0 if it is not.'''
    try:
        return int(row['proj_units_assist_max'])
    except:
        return 0

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = sin(d_lat/2)**2 + cos(lat1) * cos(lat2) * sin(d_lon/2)**2
    return (2 * asin(sqrt(a))) * 3956 # Radius of earth in miles

def bounding_box(dist, latitude, longitude):
    '''
    Legacy code, returns a lat and long tolerance.

    From: 
    https://gis.stackexchange.com/questions/142326/calculating-longitude-length-in-miles
    '''
    dlat_rad = 69 * dist / 3959 # Radius
    latitude_tolerance = dist / 69
    longitude_tolerance = dist / (cos(latitude) * 69.172)
    return (latitude_tolerance, longitude_tolerance)
