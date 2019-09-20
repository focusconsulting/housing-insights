'''
subsidy.py
----------

This file collects and cleans the susidy data from the
preservation catalog.

The resulting dataset from this file looks like:

subsidy_id  nlihc_id   poa_start     poa_end         portfolio
--------------------------------------------------------------
         1  NL000001  2004-12-31  2034-12-31   DC Dept of H...
         2  NL000001  2004-11-01  2024-10-31   US Dept of H...
         3  NL000001  2004-10-01  2024-09-30   US Dept of H...
         4  NL000001  2005-03-01  2020-03-01                DC
         5  NL000001  2005-03-01  2045-03-01                DC
'''

from . import utils
import numpy as np
import pandas as pd

def load_subsidy():
    '''Brings in Preservation Catalog Subsidy Data.'''
    df = pd.read_csv(utils.S3+'preservation_catalog/Subsidy.csv')
    df.columns = df.columns.str.lower()
    df = df.replace('N', np.NaN)
    df['poa_start'] = pd.to_datetime(df['poa_start'])
    df['poa_end'] = pd.to_datetime(df['poa_end'])
    return df[['nlihc_id', 'subsidy_id', 'poa_start', 'poa_end', 'program', 'agency']]
