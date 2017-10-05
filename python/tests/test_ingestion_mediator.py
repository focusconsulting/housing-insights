import unittest
import os
import sys

from python.housinginsights.tools.ingestion_mediator import IngestionMediator
from python.housinginsights.ingestion.LoadData import LoadData
from python.housinginsights.ingestion.Manifest import Manifest

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))
# sys.path.append(PYTHON_PATH)
SCRIPTS_PATH = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))


class MyTestCase(unittest.TestCase):
    def setUp(self):
        manifest_path = os.path.abspath(os.path.join(SCRIPTS_PATH,
                                                     'manifest.csv'))
        # initialize mediator and colleague instances
        self.load_data = LoadData(debug=True)
        self.mediator = IngestionMediator()
        self.manifest = Manifest(manifest_path)

        # build connection between mediator and its colleagues
        self.load_data.set_ingestion_mediator(self.mediator)
        self.mediator.set_load_data(self.load_data)
        self.mediator.set_manifest(self.manifest)

    def test_load_psv_to_database(self):
        result = self.mediator.load_psv_to_database('fake')
        self.assertFalse(result)

        result = self.mediator.load_psv_to_database('mar')
        self.assertTrue(result)

    def test_rebuild_database(self):
        result = self.mediator.rebuild_database(drop_all_tables=True)
        self.assertTrue(result)

    def test_create_clean_psv(self):
        pass


if __name__ == '__main__':
    unittest.main()
