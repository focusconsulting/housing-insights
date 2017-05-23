"""
Insertions_functions.py contains methods necessary for inserting data from 
one file into another file.
"""

import os
import sys
from uuid import uuid4
import pandas as pd
from datetime import datetime
import numpy as np

# setup some useful absolute paths
PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir, os.pardir))
DATA_RAW_PATH = os.path.join(PYTHON_PATH, os.pardir, 'data', 'raw')

# add to python system path
sys.path.append(PYTHON_PATH)

from python.housinginsights.sources.mar import MarApiConn
from python.housinginsights.sources.models.mar import FIELDS as MAR_FIELDS
from python.housinginsights.sources.models.DCHousing import PROJECT_FIELDS_MAP,\
    SUBSIDY_FIELDS_MAP
from python.housinginsights.sources.models.pres_cat import PROJ_FIELDS, \
    SUBSIDY_FIELDS


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
    Given a pandas data frame object of project.csv, this function returns a 
    new data frame for each row in the project.csv and its respective mar data
    using either AID or latitude/longitude reverse lookup.
    
    :param project_df: project.csv as a pandas data frame object
    :return: a pandas data frame object of the mar lookup result of each 
    corresponding row in project.csv
    """

    # useful header information
    column_headers = ['Nlihc_id'] + MAR_FIELDS
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

    # convert certain columns from float to int
    mar_df.ADDRESS_ID = mar_df.ADDRESS_ID.astype(np.int64)
    mar_df.ADDRNUM = mar_df.ADDRNUM.astype(np.int64)
    mar_df.MARID = mar_df.MARID.astype(np.int64)
    mar_df.ROADWAYSEGID = mar_df.ROADWAYSEGID.astype(np.int64)
    mar_df.ZIPCODE = mar_df.ZIPCODE.astype(np.int64)

    return mar_df


def save_to_csv(data_frame, save_to, file_name, timestamp_folder=True,
                timestamp_filename=False):
    """
    Saves a given pandas data frame object to csv file per parameters given.
    
    :param data_frame: the data to be saved
    :param save_to: the path where the data should be saved
    :param file_name: the file name the data should be saved as
    :param timestamp_folder: boolean flag to determine whether the file 
    should be saved under a time stamped folder
    :param timestamp_filename: boolean flag to determine whether the file 
    name should be appended with a time stamp.
    :return: Returns True if the expected file exists
    """
    path = os.path.abspath(save_to)
    time_stamp = datetime.today().strftime('%Y%m%d')

    if timestamp_folder:
        path = os.path.join(path, time_stamp)
        if not os.path.isdir(path):
            os.mkdir(path=path)

    if timestamp_filename:
        file_name += '-' + time_stamp

    path = os.path.join(path, file_name)

    data_frame.to_csv(path, columns=data_frame.columns, index=False)

    return os.path.isfile(path)


def fill_empty_address_id(csv_file, address_id='Proj_address_id',
                          latitude='Proj_lat', longitude='Proj_lon',
                          xcoord='Proj_x', ycoord='Proj_y',
                          address='Proj_addre'):
    """
    Identifies any rows in a given csv file with missing 
    address id and attempts to fix by using latitude/longitude, 
    proj_x/y, or proj_addre/city/st/zip.

    :return: a data frame object of updated data
    """
    df = pd.read_csv(csv_file)

    # get all indices with empty related address fields
    aid_empty_idx = df[df[address_id].isnull()].index
    lat_empty_idx = df[df[latitude].isnull()].index
    lon_empty_idx = df[df[longitude].isnull()].index
    x_empty_idx = df[df[xcoord].isnull()].index
    y_empty_idx = df[df[ycoord].isnull()].index
    address_empty_idx = df[df[address].isnull()].index

    mar_api = MarApiConn()

    # iterate through each row and use mar api to get address if possible
    for idx in aid_empty_idx:
        if idx not in lat_empty_idx and idx not in lon_empty_idx:
            result = mar_api.reverse_lat_lng_geocode(df.ix[idx, latitude],
                                                     df.ix[idx, longitude])
        elif idx not in x_empty_idx and idx not in y_empty_idx:
            result = mar_api.reverse_geocode(df.ix[idx, xcoord],
                                             df.ix[idx, ycoord])
        elif idx not in address_empty_idx:
            # check whether address is valid - it has street number
            try:
                first_address = df.ix[idx, address]
                str_num = first_address.split(' ')[0]
                int(str_num)
                result = mar_api.find_location(first_address)
            except ValueError:
                result = None

        if result is not None:
            df.ix[idx, address_id] = \
                result['Table1'][0]["ADDRESS_ID"]

    return df


def _get_data_for_temp_df(fields, fields_map, nlihc_id, dataframe, idx):
    data = {}
    for field in fields:
        value = fields_map[field]
        if value is None:
            if field == 'Nlihc_id':
                data[field] = [nlihc_id]
            else:
                data[field] = [None]
        else:
            data[field] = [dataframe.ix[idx, value]]
    return data


def add_dchousing_to_project_and_subsidy():
    """
    Returns a subsidy and project dataframe as tuple that represents the 
    appropriate locations from a given dchousing raw data csv files. As part 
    of the process, prior to creating the a dataframe object of the raw csv 
    file, it makes sure that each location as an address id that can be used 
    as lookup against the mar_project.csv file.
    """
    # get csv file paths and open as data frame objects
    mar_csv = os.path.join(DATA_RAW_PATH, 'preservation_catalog', '20170315',
                           'mar_project.csv')
    dchousing_csv = os.path.join(DATA_RAW_PATH, 'dc_housing', '20170509',
                                 'DCHousing.csv')
    mar_df = pd.read_csv(mar_csv)

    # get clean dchousing dataframe object
    dchousing_df = fill_empty_address_id(csv_file=dchousing_csv,
                                         address_id='ADDRESS_ID',
                                         latitude='LATITUDE',
                                         longitude='LONGITUDE',
                                         xcoord='XCOORD', ycoord='YCOORD',
                                         address='FULLADDRESS')

    # convert certain columns from float to int
    mar_df.ADDRESS_ID = mar_df.ADDRESS_ID.astype(np.int64)
    dchousing_df.ADDRESS_ID = dchousing_df.ADDRESS_ID.astype(np.int64)

    # create data frame objects for dchousing project and subsidy data
    proj_dc_df = pd.DataFrame(columns=PROJ_FIELDS)
    subsidy_dc_df = pd.DataFrame(columns=SUBSIDY_FIELDS)

    # iterate through each row of dchousing data and add only unique project
    # locations but add all to subsidy
    dchousing_idx = dchousing_df.index

    for idx in dchousing_idx:
        # get nlihc_id for row else use uuid to for nlihc_id
        aid = dchousing_df.ix[idx, 'ADDRESS_ID']
        nlihc_id = mar_df[mar_df.ADDRESS_ID == aid].Nlihc_id.values

        if nlihc_id:
            nlihc_id = nlihc_id[0]
        else:
            nlihc_id = str(uuid4())

            # add to proj dataframe
            data = _get_data_for_temp_df(fields=PROJ_FIELDS,
                                         fields_map=PROJECT_FIELDS_MAP,
                                         nlihc_id=nlihc_id,
                                         dataframe=dchousing_df, idx=idx)
            temp = pd.DataFrame(data=data, columns=PROJ_FIELDS)
            proj_dc_df = proj_dc_df.append(other=temp, ignore_index=True)

        # add to subsidy dataframe
        data = _get_data_for_temp_df(fields=SUBSIDY_FIELDS,
                                     fields_map=SUBSIDY_FIELDS_MAP,
                                     nlihc_id=nlihc_id,
                                     dataframe=dchousing_df, idx=idx)
        temp = pd.DataFrame(data=data, columns=SUBSIDY_FIELDS)
        subsidy_dc_df = subsidy_dc_df.append(other=temp, ignore_index=True)

    return subsidy_dc_df, proj_dc_df

