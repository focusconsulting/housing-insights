"""
Insertions_functions.py contains methods necessary for inserting data from 
one file into another file.
"""

import os
import sys
import pandas as pd
import numpy as np

# setup some useful absolute paths
PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir, os.pardir))
DATA_RAW_PATH = os.path.join(PYTHON_PATH, os.pardir, 'data', 'raw')

# add to python system path
sys.path.append(PYTHON_PATH)

from python.housinginsights.sources.mar import MarApiConn
from python.housinginsights.sources.models.mar import FIELDS


def append_raw_data(from_this, to_this, field_dict_map, unique_only=False):
    """
    Adds data from one raw csv file into another raw csv file by using a 
    given fields mapping based on two options.

    :param from_this: the file path of the data to be added from
    :type from_this: str
    :param to_this: the file path of the data to be added to
    :param field_dict_map: a dict mapping the fields int he to data with the 
    respective fields in the from data
    :param unique_only: bool flag for adding only unique rows
    :return: object representing the resulting appended data
    """
    result = False

    # throw errors if same files or if either is not a csv files
    if (not from_this.endswith('.csv')) or (not to_this.endswith('.csv')):
        raise RuntimeError('Not CSV file - check you file paths!')

    if os.path.samefile(from_this, to_this):
        raise RuntimeError('Same file - check your file paths!')

    return result


def project_csv_fix_empty_address_id():
    """
    Identifies any rows in the project.csv file with missing 
    'proj_address_id' and attempts to fix by using latitude/longitude, 
    proj_x/y, or proj_addre/city/st/zip.
    
    :return: 
    """
    proj_df = pd.read_csv(os.path.join(DATA_RAW_PATH, 'preservation_catalog',
                                '20170315', 'Project.csv'))

    # get all indices with empty related address fields
    aid_empty_idx = proj_df[proj_df.Proj_address_id.isnull()].index
    lat_empty_idx = proj_df[proj_df.Proj_lat.isnull()].index
    lon_empty_idx = proj_df[proj_df.Proj_lon.isnull()].index
    x_empty_idx = proj_df[proj_df.Proj_x.isnull()].index
    y_empty_idx = proj_df[proj_df.Proj_y.isnull()].index
    address_empty_idx = proj_df[proj_df.Proj_addre.isnull()].index

    mar_api = MarApiConn()

    # iterate through each row and use mar api to get address if possible
    for idx in aid_empty_idx:
        if idx not in lat_empty_idx and idx not in lon_empty_idx:
            result = mar_api.reverse_lat_lng_geocode(proj_df.ix[idx,
                                                                'Proj_lat'],
                                                     proj_df.ix[idx,
            'Proj_lon'])
        elif idx not in x_empty_idx and idx not in y_empty_idx:
            result = mar_api.reverse_geocode(proj_df.ix[idx, 'Proj_x'],
                                             proj_df.ix[idx, 'Proj_y'])
        elif idx not in address_empty_idx:
            # check whether address is valid - it has street number
            try:
                first_address = proj_df.ix[idx, 'Proj_addre']
                str_num = first_address.split(' ')[0]
                int(str_num)
                result = mar_api.find_location(first_address)
            except ValueError:
                result = None

        if result is not None:
            proj_df.ix[idx, 'Proj_address_id'] = \
                result['Table1'][0]["ADDRESS_ID"]

    return proj_df


def create_mar_csv(project_df):
    """
    Given a pandas dataframe object of project.csv, this function returns a 
    new dataframe for each row in the project.csv and its respective mar data
    using either AID or latitude/longitude reverse lookup.
    
    :param project_df: project.csv as a pandas dataframe object
    :return: a pandas dataframe object of the mar lookup result of each 
    corresponding row in project.csv
    """

    # useful header information
    column_headers = ['Nlihc_id'] + FIELDS
    # column_headers.remove('ADDRESS_ID')
    # print(column_headers, '\n')

    # create new df with only the 'Nlihc_id', 'Proj_address_id' headers
    df_subset = project_df.ix[:, ['Nlihc_id', 'Proj_address_id']]
    df_subset = df_subset.rename(columns={'Proj_address_id': 'ADDRESS_ID'})
    # print(df_subset.head())

    # concat additional headers into a single mar data frame
    mar_df = df_subset.reindex(columns=column_headers)
    # print(mar_df.head(10))
    # print(mar_df.columns)

    mar_api = MarApiConn()

    for idx in mar_df.index:
        aid = int(mar_df.ix[idx, 'ADDRESS_ID'])  # api requires int not float
        print('idx: {}, aid: {}'.format(idx, aid))
        result = mar_api.reverse_address_id(aid=aid)

        # handle invalid aid numbers by using lat/lon lookup instead
        if result['returnDataset']:
            result = result['returnDataset']['Table1'][0]
        else:
            lat = project_df.ix[idx, 'Proj_lat']
            lon = project_df.ix[idx, 'Proj_lon']
            result = mar_api.reverse_lat_lng_geocode(latitude=lat,
                                                     longitude=lon)
            result = result['Table1'][0]

        # populate each mar data column with api result
        result_keys = result.keys()
        for key in result_keys:
            mar_df.ix[idx, key] = result[key]

    return mar_df

