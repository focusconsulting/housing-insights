'''
    make_projects_table.py
    ----------------------

    This file creates the projects table in the database, which is sent to
    the front-end via /api/projects/. It depends on the following data sources:

        - Projects.csv, From the Preservation Catalog Folder in the s3
        - 'Affordable Housing Data': Updated regularly from open data DC (MAR)
        - DC Department of Housing and Community Development, using their API

    The data dictionary for this dataset is in {{ UPDATE ME }}.

    X = Longitude
    Y = Latitude
'''
import requests
import numpy as np
import pandas as pd
import geopandas as gp
from sources import utils
from xml.etree import ElementTree
from xmljson import parker as xml_to_json

preservation_catalog_columns = [
    "nlihc_id",
    "proj_address_id",
    "status", #active
    "cluster_tr2000",
    "ward2012",
    "proj_units_tot",
    "proj_lat",
    "proj_lon",
    "proj_name",
    "proj_addre",
    "proj_zip",
    "proj_units_assist_max", # Subsidized units (max)
    "proj_owner_type",

    # From subsidy file? 
    #"subsidy_start_first",
    #"subsidy_end_last",

    # Most Recent TOPA Data
    # Number of TOPA Notices
    # Most Recent REAC Score
    # Most Recent REAC Date
]


def load_preservation_catalog_projects():
    '''
    Loads the raw data from the preservation catalog.
    It is located in 'preservation_catalog' on the S3.
    '''
    df = pd.read_csv(utils.S3+'preservation_catalog/Project.csv')
    df.columns = df.columns.str.lower()
    df = utils.get_census_tract_for_data(df, 'proj_lon', 'proj_lat')
    return clean_prescat(df[preservation_catalog_columns+['tract']])

def clean_prescat(df):
    '''Cleans up the prescat df.'''
    #df['subsidy_start'] = pd.to_datetime(df.subsidy_start_first.replace('N', np.NaN))
    #df['subsidy_end'] = pd.to_datetime(df.subsidy_end_last.replace('N', np.NaN))

    df['neighborhood_cluster'] = utils.just_digits(df.cluster_tr2000)
    df['ward'] = utils.just_digits(df.ward2012)
    return df

def add_taxes():
    '''Adds the Project Taxable Value attribute to the data.'''
    # Tax Data. Seems to update every year. 
    return pd.read_csv('https://opendata.arcgis.com/datasets/496533836db640bcade61dd9078b0d63_53.csv')


def load_dchousing():
    '''Loads the raw data from the opendata.dc.gov
    Current columns:
        - 'ADDRESS_ID'
        - 'FULLADDRESS'
        - 'MAR_WARD'
        - 'PROJECT_NAME'
        - 'STATUS_PUBLIC'
        - 'TOTAL_AFFORDABLE_UNITS'
        - 'LATITUDE'
        - 'LONGITUDE'
    '''
    # TODO: Rename all of the columns to match prescat
    df = pd.read_csv('https://opendata.arcgis.com/datasets/34ae3d3c9752434a8c03aca5deb550eb_62.csv')
    df = df[['ADDRESS_ID',
         'FULLADDRESS',
         'MAR_WARD',
         'PROJECT_NAME',
         'STATUS_PUBLIC',
         'TOTAL_AFFORDABLE_UNITS',
         'LATITUDE',
         'LONGITUDE',]]
    return df

def load_dhcd():
    '''Loads the raw data from the DHCD

        - 'project__name'
        - 'project__project_type_scope'
        - 'project__loan_status'
        - 'property__related_property_record_id____address__street_1'
        - 'property__related_property_record_id____units__total_number_of_affordable_units_to_report'
        - 'closing__projected_or_actual_closing_date'
        - 'loans___total_loan_amount'
        - 'lihtc_allocations__total_allocation_amount'
        - 'construction_activity__status'
        - 'payments'
        - 'update_id'
    '''
    r = requests.get('https://octo.quickbase.com/db/bit4krbdh',
            params={'a': 'API_DoQuery', 'query': '{\'1\'.XEX.\'0\'}'})
    print('DHCD Response', r)
    return pd.DataFrame(xml_to_json.data(ElementTree.fromstring(r.text))['record'])
