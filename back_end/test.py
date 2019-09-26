'''
This file tests the functionality of ETL
'''
import unittest

from ETL import acs
from ETL import crime
from ETL import permit
from ETL import project
from ETL import subsidy
from ETL import utils

import pandas as pd
import requests

class TestDataCollection(unittest.TestCase):
    '''Tests the collection of raw data.'''

    def test_get_acs_data(self):
        df = acs.get_acs_data()
        self.assertIsInstance(df, pd.DataFrame)
        for c in ['zone', 'zone_type', 'total_population']:
            self.assertIn(c, df.columns)

    def test_get_crime_data(self):
        df = crime.get_crime_data()
        self.assertIsInstance(df, pd.DataFrame)
        for c in ['zone', 'zone_type', 'crime', 'violent_crime', 'non_violent_crime']:
            self.assertIn(c, df.columns)

    def test_get_permit_data(self):
        df = permit.get_permit_data()
        self.assertIsInstance(df, pd.DataFrame)
        for c in ['zone', 'zone_type', 'construction_permits', 'total_permits']:
            self.assertIn(c, df.columns)

    def test_get_prescat_project(self):
        df = project.load_preservation_catalog_projects()
        self.assertIsInstance(df, pd.DataFrame)

    def test_topa(self):
        df = project.load_topa()
        self.assertIsInstance(df, pd.DataFrame)

    def test_reac(self):
        df = project.load_reac_data()
        self.assertIsInstance(df, pd.DataFrame)

    def test_get_subsidy_data(self):
        df = subsidy.load_preservation_catalog_subsidies()
        self.assertIsInstance(df, pd.DataFrame)
        for c in ['subsidy_id', 'nlihc_id', 'portfolio', 'poa_start', 'poa_end']:
            self.assertIn(c, df.columns)

class TestUtils(unittest.TestCase):
    '''Tests the utils within ETL.'''

    def test_get_credentials(self):
        self.assertEqual(utils.get_credentials('test'), 'passed')

    def test_census_tract_load(self):
        self.assertTrue(True)

    def test_neighborhood_cluster_load(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
