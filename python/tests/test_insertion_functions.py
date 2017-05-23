import unittest
import os
import sys
import pandas as pd
import numpy as np
from pprint import pprint

# setup some useful absolute paths

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))
HOUSING_INSIGHTS_ROOT_PATH = os.path.abspath(os.path.join(PYTHON_PATH,
                                                          os.pardir))
DATA_RAW_PATH = os.path.join(HOUSING_INSIGHTS_ROOT_PATH, 'data', 'raw')

# add to python system path
sys.path.append(PYTHON_PATH)

from python.housinginsights.ingestion import insertion_functions as ins_fun
from python.housinginsights.sources.models.project import ADDRESS_FIELDS


class InsertionFuncTests(unittest.TestCase):
    def setUp(self):
        self.raw_project_csv = os.path.join(DATA_RAW_PATH,
                                            'preservation_catalog',
                                            '20170315', 'Project.csv')
        self.pres_cat_path = os.path.join(DATA_RAW_PATH,
                                            'preservation_catalog',
                                            '20170315')
        self.raw_dchousing_csv = os.path.join(DATA_RAW_PATH, 'dc_housing',
                                              '20170509', 'DCHousing.csv')
        self.mar_address_fields = ['ADDRESS_ID', 'ADDRNUM', 'ANC',
                                   'CENSUS_TRACT', 'FULLADDRESS', 'LATITUDE',
                                   'LONGITUDE', 'MARID', 'SSL', 'WARD',
                                   'XCOORD', 'YCOORD', 'ZIPCODE']

    def test_project_csv_fix_empty_address_id(self):
        df = ins_fun.project_csv_fix_empty_address_id()
        self.assertEqual(df.ix[358, 'Proj_address_id'], 68416)
        self.assertEqual(df.ix[358, 'Nlihc_id'], 'NL001032')
        # df, results = ins_fun.project_csv_fix_empty_address_id()
        # # self.assertEqual(idx, 358)
        # self.assertEqual(len(results['Table1']), 5)
        #
        # expected = {
        #   "Table1": [
        #     {
        #       "ADDRESS_ID": 68416,
        #       "MARID": 68416,
        #       "STATUS": "ACTIVE",
        #       "FULLADDRESS": "1309 ALABAMA AVENUE SE",
        #       "ADDRNUM": 1309,
        #       "ADDRNUMSUFFIX": None,
        #       "STNAME": "ALABAMA",
        #       "STREET_TYPE": "AVENUE",
        #       "QUADRANT": "SE",
        #       "CITY": "WASHINGTON",
        #       "STATE": "DC",
        #       "XCOORD": 401042.46,
        #       "YCOORD": 130751.44,
        #       "SSL": "PAR 02290161",
        #       "ANC": "ANC 8E",
        #       "PSA": "Police Service Area 705",
        #       "WARD": "Ward 8",
        #       "NBHD_ACTION": " ",
        #       "CLUSTER_": "Cluster 38",
        #       "POLDIST": "Police District - Seventh District",
        #       "ROC": "Police Sector 7D2",
        #       "CENSUS_TRACT": "007304",
        #       "VOTE_PRCNCT": "Precinct 120",
        #       "SMD": "SMD 8E04",
        #       "ZIPCODE": 20032,
        #       "NATIONALGRID": "18S UJ 27473 01406",
        #       "ROADWAYSEGID": 36174,
        #       "FOCUS_IMPROVEMENT_AREA": "NA",
        #       "HAS_ALIAS": "N",
        #       "HAS_CONDO_UNIT": "N",
        #       "HAS_RES_UNIT": "Y",
        #       "HAS_SSL": "Y",
        #       "LATITUDE": 38.84456326,
        #       "LONGITUDE": -76.98799165,
        #       "STREETVIEWURL": "http://maps.google.com/maps?z=16&layer=c&cbll=38.84456326,-76.98799165&cbp=11,179.731940668932,,0,2.09",
        #       "RES_TYPE": "RESIDENTIAL",
        #       "WARD_2002": "Ward 8",
        #       "WARD_2012": "Ward 8",
        #       "ANC_2002": "ANC 8E",
        #       "ANC_2012": "ANC 8E",
        #       "SMD_2002": "SMD 8E02",
        #       "SMD_2012": "SMD 8E04",
        #       "DISTANCE": 0.0
        #     },
        #     {
        #       "ADDRESS_ID": 278343,
        #       "MARID": 278343,
        #       "STATUS": "ACTIVE",
        #       "FULLADDRESS": "3200 13TH STREET SE",
        #       "ADDRNUM": 3200,
        #       "ADDRNUMSUFFIX": None,
        #       "STNAME": "13TH",
        #       "STREET_TYPE": "STREET",
        #       "QUADRANT": "SE",
        #       "CITY": "WASHINGTON",
        #       "STATE": "DC",
        #       "XCOORD": 401018.46,
        #       "YCOORD": 130740.38,
        #       "SSL": "5914    0007",
        #       "ANC": "ANC 8E",
        #       "PSA": "Police Service Area 705",
        #       "WARD": "Ward 8",
        #       "NBHD_ACTION": " ",
        #       "CLUSTER_": "Cluster 38",
        #       "POLDIST": "Police District - Seventh District",
        #       "ROC": "Police Sector 7D2",
        #       "CENSUS_TRACT": "007304",
        #       "VOTE_PRCNCT": "Precinct 120",
        #       "SMD": "SMD 8E04",
        #       "ZIPCODE": 20032,
        #       "NATIONALGRID": "18S UJ 27449 01395",
        #       "ROADWAYSEGID": 36170,
        #       "FOCUS_IMPROVEMENT_AREA": "NA",
        #       "HAS_ALIAS": "N",
        #       "HAS_CONDO_UNIT": "N",
        #       "HAS_RES_UNIT": "Y",
        #       "HAS_SSL": "Y",
        #       "LATITUDE": 38.84446365,
        #       "LONGITUDE": -76.98826813,
        #       "STREETVIEWURL": "http://maps.google.com/maps?z=16&layer=c&cbll=38.84446365,-76.98826813&cbp=11,84.4654730833699,,0,2.09",
        #       "RES_TYPE": "RESIDENTIAL",
        #       "WARD_2002": "Ward 8",
        #       "WARD_2012": "Ward 8",
        #       "ANC_2002": "ANC 8E",
        #       "ANC_2012": "ANC 8E",
        #       "SMD_2002": "SMD 8E02",
        #       "SMD_2012": "SMD 8E04",
        #       "DISTANCE": 26.43
        #     },
        #     {
        #       "ADDRESS_ID": 294865,
        #       "MARID": 294865,
        #       "STATUS": "ACTIVE",
        #       "FULLADDRESS": None,
        #       "ADDRNUM": None,
        #       "ADDRNUMSUFFIX": None,
        #       "STNAME": "ALABAMA",
        #       "STREET_TYPE": "AVENUE",
        #       "QUADRANT": "SE",
        #       "CITY": "WASHINGTON",
        #       "STATE": "DC",
        #       "XCOORD": 401074.88,
        #       "YCOORD": 130760.76,
        #       "SSL": "PAR 02290103",
        #       "ANC": "ANC 8E",
        #       "PSA": "Police Service Area 705",
        #       "WARD": "Ward 8",
        #       "NBHD_ACTION": " ",
        #       "CLUSTER_": "Cluster 38",
        #       "POLDIST": "Police District - Seventh District",
        #       "ROC": "Police Sector 7D2",
        #       "CENSUS_TRACT": "007304",
        #       "VOTE_PRCNCT": "Precinct 120",
        #       "SMD": "SMD 8E04",
        #       "ZIPCODE": 20032,
        #       "NATIONALGRID": "18S UJ 27505 01414",
        #       "ROADWAYSEGID": 36174,
        #       "FOCUS_IMPROVEMENT_AREA": "NA",
        #       "HAS_ALIAS": "Y",
        #       "HAS_CONDO_UNIT": "N",
        #       "HAS_RES_UNIT": "N",
        #       "HAS_SSL": "Y",
        #       "LATITUDE": 38.84464718,
        #       "LONGITUDE": -76.98761818,
        #       "STREETVIEWURL": "http://maps.google.com/maps?z=16&layer=c&cbll=38.84464718,-76.98761818&cbp=11,158.542804214262,,0,2.09",
        #       "RES_TYPE": "NON RESIDENTIAL",
        #       "WARD_2002": "Ward 8",
        #       "WARD_2012": "Ward 8",
        #       "ANC_2002": "ANC 8E",
        #       "ANC_2012": "ANC 8E",
        #       "SMD_2002": "SMD 8E02",
        #       "SMD_2012": "SMD 8E04",
        #       "DISTANCE": 33.73
        #     },
        #     {
        #       "ADDRESS_ID": 38674,
        #       "MARID": 38674,
        #       "STATUS": "ACTIVE",
        #       "FULLADDRESS": "3210 13TH STREET SE",
        #       "ADDRNUM": 3210,
        #       "ADDRNUMSUFFIX": None,
        #       "STNAME": "13TH",
        #       "STREET_TYPE": "STREET",
        #       "QUADRANT": "SE",
        #       "CITY": "WASHINGTON",
        #       "STATE": "DC",
        #       "XCOORD": 401017.88,
        #       "YCOORD": 130712.80,
        #       "SSL": "5914    0006",
        #       "ANC": "ANC 8E",
        #       "PSA": "Police Service Area 705",
        #       "WARD": "Ward 8",
        #       "NBHD_ACTION": " ",
        #       "CLUSTER_": "Cluster 38",
        #       "POLDIST": "Police District - Seventh District",
        #       "ROC": "Police Sector 7D2",
        #       "CENSUS_TRACT": "007304",
        #       "VOTE_PRCNCT": "Precinct 120",
        #       "SMD": "SMD 8E04",
        #       "ZIPCODE": 20032,
        #       "NATIONALGRID": "18S UJ 27447 01367",
        #       "ROADWAYSEGID": 17705,
        #       "FOCUS_IMPROVEMENT_AREA": "NA",
        #       "HAS_ALIAS": "N",
        #       "HAS_CONDO_UNIT": "N",
        #       "HAS_RES_UNIT": "Y",
        #       "HAS_SSL": "Y",
        #       "LATITUDE": 38.84421520,
        #       "LONGITUDE": -76.98827485,
        #       "STREETVIEWURL": "http://maps.google.com/maps?z=16&layer=c&cbll=38.8442152,-76.98827485&cbp=11,99.6444549813545,,0,2.09",
        #       "RES_TYPE": "RESIDENTIAL",
        #       "WARD_2002": "Ward 8",
        #       "WARD_2012": "Ward 8",
        #       "ANC_2002": "ANC 8E",
        #       "ANC_2012": "ANC 8E",
        #       "SMD_2002": "SMD 8E02",
        #       "SMD_2012": "SMD 8E04",
        #       "DISTANCE": 45.80
        #     },
        #     {
        #       "ADDRESS_ID": 69751,
        #       "MARID": 69751,
        #       "STATUS": "ACTIVE",
        #       "FULLADDRESS": "1249 ALABAMA AVENUE SE",
        #       "ADDRNUM": 1249,
        #       "ADDRNUMSUFFIX": None,
        #       "STNAME": "ALABAMA",
        #       "STREET_TYPE": "AVENUE",
        #       "QUADRANT": "SE",
        #       "CITY": "WASHINGTON",
        #       "STATE": "DC",
        #       "XCOORD": 400980.32,
        #       "YCOORD": 130736.38,
        #       "SSL": "5946    0072",
        #       "ANC": "ANC 8E",
        #       "PSA": "Police Service Area 705",
        #       "WARD": "Ward 8",
        #       "NBHD_ACTION": " ",
        #       "CLUSTER_": "Cluster 39",
        #       "POLDIST": "Police District - Seventh District",
        #       "ROC": "Police Sector 7D2",
        #       "CENSUS_TRACT": "007304",
        #       "VOTE_PRCNCT": "Precinct 120",
        #       "SMD": "SMD 8E04",
        #       "ZIPCODE": 20032,
        #       "NATIONALGRID": "18S UJ 27410 01392",
        #       "ROADWAYSEGID": 12415,
        #       "FOCUS_IMPROVEMENT_AREA": "NA",
        #       "HAS_ALIAS": "N",
        #       "HAS_CONDO_UNIT": "N",
        #       "HAS_RES_UNIT": "N",
        #       "HAS_SSL": "Y",
        #       "LATITUDE": 38.84442766,
        #       "LONGITUDE": -76.98870748,
        #       "STREETVIEWURL": "http://maps.google.com/maps?z=16&layer=c&cbll=38.84442766,-76.98870748&cbp=11,263.46262791632,,0,2.09",
        #       "RES_TYPE": "RESIDENTIAL",
        #       "WARD_2002": "Ward 8",
        #       "WARD_2012": "Ward 8",
        #       "ANC_2002": "ANC 8E",
        #       "ANC_2012": "ANC 8E",
        #       "SMD_2002": "SMD 8E05",
        #       "SMD_2012": "SMD 8E04",
        #       "DISTANCE": 63.94
        #     }
        #   ]
        #     }
        #
        # for idx in range(5):
        #     table = results['Table1']
        #     expected_table = expected['Table1']
        #     for key in table[idx].keys():
        #         self.assertEqual(table[idx][key], expected_table[idx][key])

    def test_create_mar_csv(self):
        proj_df = ins_fun.project_csv_fix_empty_address_id()
        mar_df = ins_fun.create_mar_csv(proj_df)

        # check to make sure there are no null values
        for field in self.mar_address_fields:
            self.assertFalse(mar_df[field].isnull().any())

        # use nlihc_id = NL000338 and aid = 904238 as first benchmark
        # inconsistent data between mar and proj for this row
        nlihc_id, proj_aid = 'NL000338', 904238

        # nlihc_id is in both tables
        proj_subset = proj_df[proj_df.Nlihc_id == nlihc_id]
        mar_subset = mar_df[mar_df.Nlihc_id == nlihc_id]
        self.assertTrue((proj_subset.Nlihc_id == 'NL000338').all())
        self.assertTrue((mar_subset.Nlihc_id == proj_subset.Nlihc_id).all())

        # aid 904238 in proj but not in mar - has different aid
        self.assertTrue((proj_subset.Proj_address_id == 904238).all())
        self.assertFalse((mar_subset.ADDRESS_ID ==
                          proj_subset.Proj_address_id).all())

        # use aid = 238401 for consistency validation
        nlihc_id, proj_aid = 'NL000001', 238401
        proj_subset = proj_df[proj_df.Nlihc_id == nlihc_id]
        mar_subset = mar_df[mar_df.Nlihc_id == nlihc_id]
        self.assertTrue((mar_subset.ADDRESS_ID ==
                          proj_subset.Proj_address_id).all())

    def test_add_dchousing_to_project_and_subsidy(self):
        # get csv file paths and open as data frame objects
        mar_csv = os.path.join(DATA_RAW_PATH, 'preservation_catalog',
                               '20170315',
                               'mar_project.csv')
        dchousing_csv = os.path.join(DATA_RAW_PATH, 'dc_housing', '20170509',
                                     'DCHousing.csv')
        dchousing_df = pd.read_csv(dchousing_csv)

        subsidy_df, proj_df = ins_fun.add_dchousing_to_project_and_subsidy()

        # expect to append all to subsidy but less to project table
        self.assertEqual(len(subsidy_df), len(dchousing_df))
        self.assertNotEqual(len(proj_df), len(dchousing_df))
        self.assertLess(len(proj_df), len(dchousing_df))

        # if above tests pass, let's write to raw folder
        result = ins_fun.save_to_csv(data_frame=subsidy_df,
                            save_to=self.pres_cat_path,
                            file_name='dchousing_append_subsidy.csv',
                            timestamp_folder=False)
        self.assertTrue(result)
        result = ins_fun.save_to_csv(data_frame=proj_df,
                                     save_to=self.pres_cat_path,
                                     file_name='dchousing_append_project.csv',
                                     timestamp_folder=False)
        self.assertTrue(result)

    def test_fill_empty_address_id(self):
        df = ins_fun.fill_empty_address_id(csv_file=self.raw_project_csv)
        self.assertEqual(df.ix[358, 'Proj_address_id'], 68416)
        self.assertEqual(df.ix[358, 'Nlihc_id'], 'NL001032')


if __name__ == '__main__':
    unittest.main()
