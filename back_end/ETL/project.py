'''
    make_projects_table.py
    ----------------------

    This file creates the projects table in the database, which is sent to
    the front-end via /api/projects/. It depends on the following data sources:

        - Projects.csv, From the Preservation Catalog Folder in the s3
        - 'Affordable Housing Data': Updated regularly from open data DC
        - Master Adress Repository

    Projects that are not from the preservation catalog have an nlihc_id
    beginning with "AH" for affordable housing.
'''
from . import utils
import requests
import numpy as np
import pandas as pd
import geopandas as gp

preservation_catalog_columns = [
    "nlihc_id",
    "latitude",
    "longitude",
    "census_tract",
    "neighborhood_cluster",
    "ward",
    "neighborhood_cluster_desc",
    # Basic Project Information",
    "proj_name",
    "proj_addre",
    "proj_units_tot",
    "proj_address_id",
    "proj_units_assist_max",
    "proj_owner_type",
    "most_recent_reac_score_num",
    "most_recent_reac_score_date",
]

def load_preservation_catalog_projects():
    '''
    Loads the raw data from the preservation catalog.
    It is located in 'preservation_catalog' on the S3.
    '''
    df = pd.read_csv(utils.S3+'preservation_catalog/Project.csv')
    df.columns = df.columns.str.lower()
    df = utils.get_census_tract_for_data(df, 'proj_lon', 'proj_lat')
    df['neighborhood_cluster'] = utils.just_digits(df.cluster_tr2000)
    df['ward'] = utils.just_digits(df.ward2012)
    df = df.merge(load_reac_data())
    return df.rename(columns={"proj_lat": "latitude",
                              "proj_lon": "longitude",
                              "tract": "census_tract",
                              "date": "most_recent_reac_score_date",
                              "reac_score_num": "most_recent_reac_score_num",
                              "cluster_tr2000_name": "neighborhood_cluster_desc",
                              })[preservation_catalog_columns]

def load_affordable_housing_projects():
    '''Loads and transforms the "Affordabe Housing" raw data from opendata.dc'''
    columns = {
        'ADDRESS_ID': 'proj_address_id',
        'FULLADDRESS': 'proj_addre',
        'MAR_WARD': 'ward',
        'PROJECT_NAME': 'proj_name',
        'TOTAL_AFFORDABLE_UNITS': 'proj_units_tot',
        'LATITUDE': 'latitude',
        'LONGITUDE': 'longitude',
        'tract': 'census_tract',
    }
    url = utils.get_paths_for_data('affordable_housing', years=utils.get_years())[0]
    df = pd.read_csv(url)
    df['MAR_WARD'] = utils.just_digits(df['MAR_WARD'])
    df = utils.get_census_tract_for_data(df, 'LONGITUDE','LATITUDE')
    df = df.rename(columns=columns)[columns.values()]
    df = utils.get_cluster_for_data(df, 'longitude', 'latitude')
    df['nlihc_id'] = pd.Series(df.index).astype(str).apply(lambda s: 'AH' + s.zfill(6))
    return df[['nlihc_id', 'neighborhood_cluster']+ list(columns.values())]

def load_mar_projects():
    '''Loads and trasforms the "Address Points" raw data from opendata.dc'''
    url = utils.get_paths_for_data('mar', years=utils.get_years())[0]
    df = pd.read_csv(url)
    df = df[['ADDRESS_ID', 'ACTIVE_RES_UNIT_COUNT', 'SSL', 'CLUSTER_']]
    df.columns = ['proj_address_id', 'active_res_unit_count', 'ssl', 'neighborhood_cluster']
    return df

def load_tax():
    '''Adds the Project Taxable Value attribute to the data.'''
    # Tax Data. Seems to update every year. 
    r = requests.get(
        'https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Property_and_Land_WebMercator/MapServer/53/query?where=1%3D1&outFields=SSL,ASSESSMENT&returnGeometry=false&outSR=4326&f=json'
    )
    data = r.json()['features']
    return {r['attributes']['SSL']: r['attributes']['ASSESSMENT'] for r in data}

def load_topa():
    '''
    This function loads the raw TOPA data, grabs the most recent date for
    each address id, and counts the number of TOPA notices for each address id.

    It returns a dataframe where the obserations are an address id, the most
    recent topa notice as a data, and the number of topa notices.
    '''
    df = pd.read_csv(utils.S3+'topa/Rcasd_current.csv')
    df.columns = df.columns.str.lower()
    df['most_recent_topa_date'] = pd.to_datetime(df['notice_date'])
    return pd.concat([
            # The most recent topa data.
            (df.sort_values('most_recent_topa_date', ascending=False)
               .groupby('address_id').first()['most_recent_topa_date']),
            # Number of observations per address id.
            df.address_id.value_counts()
            ], axis=1).reset_index().rename(columns={
            # Fixing column names
            'address_id': 'topa_count', 'index': 'proj_address_id'})

def load_reac_data():
    '''Gets REAC information from the s3.'''
    df = pd.read_csv(utils.S3+'preservation_catalog/Reac_score.csv')
    df.columns = df.columns.str.lower()
    df['date'] = pd.to_datetime(df['reac_date'])
    df = df.sort_values('date', ascending=False).groupby('nlihc_id').first()
    return df[['date', 'reac_score_num']].reset_index()

def load_project_data(engine):
    '''With the addition of MAR - this takes a long time (a few minutes).'''
    df = pd.concat([load_preservation_catalog_projects(),
                    load_affordable_housing_projects()], sort=True)
    df = df.sort_values('nlihc_id').drop_duplicates('proj_address_id')
    df = df.merge(load_mar_projects(), on='proj_address_id', how='left')
    df['sum_appraised_value_current_total'] = df['ssl'].map(load_tax())


    # Fix neighborhood Cluster Info
    df['neighborhood_cluster_x'] = utils.just_digits(df.neighborhood_cluster_x)
    df['neighborhood_cluster_y'] = utils.just_digits(df.neighborhood_cluster_y)
    df['neighborhood_cluster'] = df.apply(lambda row: max(
        row.neighborhood_cluster_x, row.neighborhood_cluster_y), axis=1)
    df = df.drop(columns=['neighborhood_cluster_x', 'neighborhood_cluster_y'])
    df = df.merge(load_topa(), on='proj_address_id', how='left')
    return utils.write_table(df, 'new_project', engine)
