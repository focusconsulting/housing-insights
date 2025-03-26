import unittest
import os
import sys
from pprint import pprint

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEST_DATA_PATH = os.path.abspath(
    os.path.join(PYTHON_PATH, "tests", "test_data", "project_missing_streetview.csv")
)

# add to python system path
sys.path.append(PYTHON_PATH)

from housinginsights.sources.google_maps import GoogleMapsApiConn


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.map_api = GoogleMapsApiConn()

    def test_check_street_view(self):
        # test cases:
        # '292768': 38.97658194, -77.02884996, 'No street view'
        result = self.map_api.check_street_view(38.97658194, -77.02884996)
        pprint(result)
        self.assertFalse(result)
        # '312330': 38.90580301, -77.02655240000001, 'Exact street view'
        result = self.map_api.check_street_view(38.90580301, -77.02655240000001)
        pprint(result)
        self.assertTrue(result)
        # '310103': 38.97523115, -77.01565599999998, 'Next closest'
        result = self.map_api.check_street_view(38.97523115, -77.01565599999998)
        pprint(result)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
