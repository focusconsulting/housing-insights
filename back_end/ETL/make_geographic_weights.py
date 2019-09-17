'''
make_geographic_weights.py
--------------------------

This file only needs to be run if the geographies for DC have changed.

The output of this file can be found in the S3 under the geopgraphic_data
folder.

This file creates data that shows what percentage of census tracts are in
wards and neighborhood clusters in DC.

It utilizes the geojson API from Open Data DC. The output datasets are:

'tract_neighborhood_weights.csv':

    | tract | neighborhood_cluster | weight |
    | ----- | -------------------- | ------ |
    | 3400  | Cluster 3            | 95.891 |
    | 3400  | Cluster 21           |  2.486 |
    | 3400  | Cluster 2            |  1.623 |
    | 3500  | Cluster 3            | 28.895 |
    | 3500  | Cluster 2            | 71.105 |

'tract_ward_weights.csv':

    | tract | ward |  weight |
    | ----- | ---- | ------- |
    | 3400  |    6 |   0.000 |
    | 3400  |    1 |  97.529 |
    | 3400  |    5 |   2.471 |
    | 3500  |    1 | 100.000 |
'''
import pandas as pd
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

def get_areas(geom_1, geom_2):
    '''
    This function returns a dataframe where the first column
    is the base geometry, the second column is another geometry,
    and the last column is the percentage of the first geometry
    within the second geometry.

    The input requires two dictionaries, where the key is a label
    for the geometry (tract, for example) and the value is the
    geometry itself.

    This is slightly less efficient than a geopandas overlay, but
    a bit easier to understand and debug. Seeing as this forms the
    basis of the zone_facts table, it's ok that this is a bit brute
    force in order to be accurate.
    '''
    rv = []
    for key_1, g1 in geom_1.items():
        for key_2, g2 in geom_2.items():
            if g1.intersects(g2):
                rv.append((key_1, key_2, (g1.intersection(g2).area / g1.area) *100))
    return pd.DataFrame(rv)

if __name__ == "__main__":
    # Get raw data
    tract = read(TRACT)
    neighborhood = read(NEIGHBORHOOD)
    ward = read(WARD)

    # Make dictionaries for the get areas function
    tract_geo = dict(zip(tract.tract, tract.geometry))
    neighborhood_geo = dict(zip(neighborhood.name, neighborhood.geometry))
    ward_geo = dict(zip(ward.ward, ward.geometry))

    # Make lookup tables
    tract_nh = get_areas(tract_geo, neighborhood_geo)
    tract_nh.columns = ['tract', 'neighborhood_cluster', 'weight']
    tract_nh.to_csv('tract_neighborhood_cluster_weights.csv', index=False)

    tract_ward = get_areas(tract_geo, ward_geo)
    tract_ward.columns = ['tract', 'ward', 'weight']
    tract_ward.to_csv('tract_ward_weights.csv', index=False)
