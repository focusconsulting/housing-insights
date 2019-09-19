'''Makes the subsidy table.'''

import numpy as np
import pandas as pd
from sources import utils
from sqlalchemy import create_engine


def load_preservation_catalog_subsidies():
    '''
    Loads the raw data from the preservation catalog.
    It is located in 'preservation_catalog' on the S3.
    '''
    df = pd.read_csv(utils.S3+'preservation_catalog/Subsidy.csv')
    df.columns = df.columns.str.lower()

    df['poa_start'] = pd.to_datetime(df.poa_start.replace('N', np.NaN))
    df['poa_end'] = pd.to_datetime(df.poa_end.replace('N', np.NaN))

    return df[['subsidy_id', 'nlihc_id', 'portfolio', 'poa_start', 'poa_end']]

def make_subsidy_table():
    '''Adds subsidy table to database.'''
    df = load_preservation_catalog_subsidies()
    df.to_sql('new_subsidy',
        create_engine(utils.get_credentials('docker_database_connect_str')),
        if_exists='replace')

if __name__ == "__main__":
    make_subsidy_table()
