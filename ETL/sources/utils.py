'''
utils.py
--------

This file has helper functions for loading and cleaning data.
'''

import datetime
import numpy as np
import pandas as pd

S3 = 'https://housing-insights.s3.amazonaws.com/'

def fix_tract(tract_number):
    '''Makes a tract number a string of length six with leading zeroes.'''
    if not tract_number or np.isnan(tract_number):
        return '99999'
    tract_number = str(int(tract_number))
    while len(tract_number) < 6:
        tract_number = '0' + tract_number
    return tract_number

def get_years():
    '''Returns this year and last year as integers.'''
    this_year = datetime.datetime.now().year
    return this_year, this_year - 1

def year_ago():
    '''Returns the datetime for a year ago.'''
    return datetime.datetime.now() - datetime.timedelta(days=365)


def get_paths_for_data(data_category, years):
    '''
    Returns the data download paths for a data category for the given years.

    data_category: A string of the data_category (ex. crime).
    years: An iterable of years as integers.
    '''
    df = pd.read_excel(S3+'data_sources.xlsx')
    return (df[(df.data_category == data_category) &
               (df.year.isin(years))]["url"].to_list())
