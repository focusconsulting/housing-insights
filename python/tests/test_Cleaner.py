import unittest
import os
from python.housinginsights.ingestion.Cleaners import ProjectCleaner, PYTHON_PATH
from python.housinginsights.ingestion.Manifest import Manifest
from python.housinginsights.ingestion.functions import load_meta_data


class CleanerTestCase(unittest.TestCase):
    def setUp(self):
        # use test data
        test_data_path = os.path.abspath(os.path.join(PYTHON_PATH, 'tests',
                                                      'test_data'))
        self.meta_path = os.path.abspath(os.path.join(test_data_path,
                                                      'meta_load_data.json'))
        self.manifest_path = os.path.abspath(
            os.path.join(test_data_path, 'manifest_load_data.csv'))
        self.database_choice = 'docker_database'
        self.manifest = Manifest(path=self.manifest_path)

    def test_add_geocode_from_mar(self):
        # get rows for test cases
        dchousing_manifest_row = self.manifest.get_manifest_row(
            unique_data_id='dchousing_project')
        building_permits_2017_manifest_row = self.manifest.get_manifest_row(
            unique_data_id='building_permits_2017')

        # mar_id test cases - except for ward other fields are typically Null
        mar_ids = [148655, 289735, 311058, 308201]
        fields = ['Ward2012', 'Cluster_tr2000', 'Cluster_tr2000_name',
                  'Proj_Zip', 'Anc2012', 'Geo2010',
                  'Status', 'Proj_addre', 'Proj_image_url',
                  'Proj_streetview_url', 'Psa2012', 'Proj_City', 'Proj_ST']
        rows = list()

        # populate fields for each case as 'Null'
        for ids in mar_ids:
            id_dict = dict()
            id_dict.setdefault('mar_id', ids)
            for field in fields:
                if field == 'Proj_streetview_url':
                    id_dict[field] = "dummy"
                else:
                    id_dict[field] = 'Null'
            rows.append(id_dict)

        # verify add_geocode_from_mar()
        cleaner = ProjectCleaner(load_meta_data(self.meta_path),
                                 dchousing_manifest_row)
        for row in rows:
            result = cleaner.add_geocode_from_mar(row)
            for field in fields:
                self.assertFalse(result[field] == 'Null', "no 'Nulls' left.")


if __name__ == '__main__':
    unittest.main()
