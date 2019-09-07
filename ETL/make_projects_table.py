'''
    make_projects_table.py
    ----------------------

    This file creates the projects table in the database, which is sent to
    the front-end via /api/projects/. It depends on the following data sources:

        - Projects.csv, From the Preservation Catalog Folder in the s3
        - 'Affordable Housing Data': Updated regularly from open data DC
        - DC Department of Housing and Community Development, using their API

    The data dictionary for this dataset is in {{ UPDATE ME }}.
'''
import requests
import pandas as pd
from xml.etree import ElementTree
from xmljson import parker as xml_to_json

def load_prescat():
    '''
    Loads the raw data from the preservation catalog.
    It is located in 'preservation_catalog' on the S3.
    '''
    return pd.read_csv('https://housing-insights.s3.amazonaws.com/preservation_catalog/Project.csv')

def load_dchousing():
    '''Loads the raw data from the opendata.dc.gov
    Current columns:
        - 'X'
        - 'Y'
        - 'OBJECTID'
        - 'MAR_WARD'
        - 'ADDRESS'
        - 'PROJECT_NAME'
        - 'STATUS_PUBLIC'
        - 'AGENCY_CALCULATED'
        - 'TOTAL_AFFORDABLE_UNITS'
        - 'LATITUDE'
        - 'LONGITUDE'
        - 'AFFORDABLE_UNITS_AT_0_30_AMI'
        - 'AFFORDABLE_UNITS_AT_31_50_AMI'
        - 'AFFORDABLE_UNITS_AT_51_60_AMI'
        - 'AFFORDABLE_UNITS_AT_61_80_AMI'
        - 'AFFORDABLE_UNITS_AT_81_AMI'
        - 'CASE_ID'
        - 'ADDRESS_ID'
        - 'XCOORD'
        - 'YCOORD'
        - 'FULLADDRESS'
        - 'GIS_LAST_MOD_DTTM'
    '''
    return pd.read_csv('https://opendata.arcgis.com/datasets/34ae3d3c9752434a8c03aca5deb550eb_62.csv')

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

df = load_prescat()
