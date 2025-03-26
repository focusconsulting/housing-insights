import unittest
import os
import sys

# setup some useful absolute paths

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# add to python system path
sys.path.append(PYTHON_PATH)

from python.housinginsights.sources.mar import MarApiConn


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.mar_api = MarApiConn()

    def test_mar_reverse_lat_lng_geocode(self):
        result = self.mar_api.reverse_lat_lng_geocode("38.84456326", "-76.98799165")
        # did we get five results as expected per api docs
        self.assertEqual(len(result["Table1"]), 5)
        # do some random sampling of data in the tables as final check
        self.assertEqual(result["Table1"][0]["FULLADDRESS"], "1309 ALABAMA AVENUE SE")
        self.assertEqual(
            result["Table1"][1]["POLDIST"], "Police District - Seventh District"
        )
        self.assertEqual(result["Table1"][2]["ADDRESS_ID"], 294865)
        self.assertEqual(result["Table1"][3]["XCOORD"], 401017.88)
        self.assertEqual(result["Table1"][4]["SSL"], "5946    0072")

    def test_find_location(self):
        result = self.mar_api.find_location("1210 lamont st")
        table = result["returnDataset"]["Table1"]

        # did we get only 1 result as expected per api docs
        self.assertEqual(len(table), 1)
        # do some random sampling of data in the tables as final check
        self.assertEqual(table[0]["FULLADDRESS"], "1210 LAMONT STREET NW")
        self.assertEqual(table[0]["POLDIST"], "Police District - Third District")
        self.assertEqual(table[0]["ADDRESS_ID"], 231167)
        self.assertEqual(table[0]["XCOORD"], 397484.58)
        self.assertEqual(table[0]["SSL"], "2844    0827")

        # check for non-DC address
        result = self.mar_api.find_location("8512 Wagon Wheel Rd")
        self.assertIsNone(result["returnCodes"])
        self.assertIsNone(result["returnDataset"])

    def test_mar_reverse_geocode(self):
        result = self.mar_api.reverse_geocode("401042.46", "130751.44")

        # did we get five results as expected per api docs
        self.assertEqual(len(result["Table1"]), 5)

        # do some random sampling of data in the tables as final check
        self.assertEqual(result["Table1"][0]["FULLADDRESS"], "1309 ALABAMA AVENUE SE")
        self.assertEqual(
            result["Table1"][1]["POLDIST"], "Police District - Seventh District"
        )
        self.assertEqual(result["Table1"][2]["ADDRESS_ID"], 294865)
        self.assertEqual(result["Table1"][3]["XCOORD"], 401017.88)
        self.assertEqual(result["Table1"][4]["SSL"], "5946    0072")

    def test__get_address_id(self):
        result = self.mar_api._get_address_id("915 E St NW")
        self.assertEqual(result, 239822)

    def test_get_condo_count(self):
        result = self.mar_api.get_condo_count("915 E St NW")
        self.assertEqual(result, 160)

    def test_reverse_address_id(self):
        result = self.mar_api.reverse_address_id(68416)
        loc_object = result["returnDataset"]["Table1"][0]

        # spot check returned data matches output from url end point
        self.assertEqual(loc_object["MARID"], 68416)
        self.assertEqual(loc_object["FULLADDRESS"], "1309 ALABAMA AVENUE SE")
        self.assertEqual(loc_object["XCOORD"], 401042.46)
        self.assertEqual(loc_object["YCOORD"], 130751.44)
        self.assertEqual(loc_object["LATITUDE"], 38.84456326)
        self.assertEqual(loc_object["LONGITUDE"], -76.98799165)
        self.assertEqual(loc_object["ConfidenceLevel"], 100.0)


if __name__ == "__main__":
    unittest.main()
