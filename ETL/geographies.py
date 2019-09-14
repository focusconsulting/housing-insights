'''
geographies.py
--------------

This file makes a lookup table for census tracts, wards, and neighborhood
clusters in DC. It utilizes the geojson API from Open Data DC.
'''
import geopandas as gp

TRACT = ('https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/'
         'Demographic_WebMercator/MapServer/8/query?where=1%3D1&outFields='
         'TRACT,Shape,GEOID,Shape_Length,Shape_Area&outSR=4326&f=json')

NEIGHBORHOOD = ('https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/'
                'Administrative_Other_Boundaries_WebMercator/MapServer/17/'
                'query?where=1%3D1&outFields=NAME,Shape,Shape_Length,'
                'Shape_Area&outSR=4326&f=json')

WARD = ('https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/'
        'Administrative_Other_Boundaries_WebMercator/MapServer/31/'
        'query?where=1%3D1&outFields=WARD,Shape,WARD_ID,Shape_Length,'
        'Shape_Area&outSR=4326&f=json')

def read(path):
    '''Reads in the shape and makes the columns lowercase.'''
    shp = gp.read_file(path)
    shp.columns = shp.columns.str.lower()
    return shp

tract = read(TRACT)
neighborhood = read(NEIGHBORHOOD)
ward = read(WARD)
