import unittest
import python.housinginsights.ingestion.functions as helper_funs


class FunctionsTestCase(unittest.TestCase):
    def test_identify_valid_unique_address(self):
        # Cases for complete address delimiters #
        # case 1: ';' delimiter separated addresses
        address_str = '1110 Aspen Street NW; 6650 Georgia Avenue NW; 6656 Georgia Avenue NW; others'
        expected_result = ['1110 Aspen Street NW', '6650 Georgia Avenue NW',
                           '6656 Georgia Avenue NW', 'others']
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed ';' delimiter case: {}".format(address))

        # case 2: 'and' delimiter separated address
        address_str = '1110 Aspen Street NW and 6650 Georgia Avenue NW'
        expected_result = ['1110 Aspen Street NW', '6650 Georgia Avenue NW']
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed 'and' delimiter case")

        # Cases for address number ranges #
        # case 3: '&' delimiter separated address
        address_str = '1521 & 1523 16th Street NW'
        expected_result = ['1521 16th Street NW', '1523 16th Street NW']
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed '&' delimiter case")

        """Seperating into multiple cases for now but it seems is best to assume +2 when given address number ranges. Examples for real data seems to confirm this.
        """
        # case 4a: '-' odd delimiter address number ranges
        address_str = '1309-1313 E Street SE'
        expected_result = ['1309 E Street SE', '1311 E Street SE',
                           '1313 E Street SE']
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed odd '-' delimiter case")

        # case 4b: '-' even delimiter address number ranges
        address_str = '4000-4008 8th Street NE'
        expected_result = ['4000 8th Street NE', '4002 8th Street NE',
                           '4004 8th Street NE', '4006 8th Street NE',
                           '4008 8th Street NE']
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed even '-' delimiter case")

        # case 4c: '-' ambiguous delimiter address number ranges
        address_str = '4000-4005 8th Street NE'
        expected_result = ['4000 8th Street NE', '4002 8th Street NE',
                           '4004 8th Street NE', '4001 8th Street NE',
                           '4003 8th Street NE', '4005 8th Street NE']
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed ambiguous '-' delimiter case")

        # Cases for composites #
        # case 5: '&' + 'and' delimiter separated addresses
        address_str = '1521 & 1523 16th Street NW and 1531 Church Street NW'
        expected_result = []
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed '&' + 'and' delimiter composite")

        # case 6: both addresses delimiter and address number ranges
        address_str = "1110 Aspen Street NW; 2301-2323 Good Hope Court SE; 6650 Georgia Avenue NW; 2420-2428 14th Street NE"
        expected_result = []
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed both number range and address delimiter cases")

        # case 7: composite of many delimiters
        address_str = '4232-4258 4th Street SE and 4281-4297 6th Street SE; 1521 & 1523 16th Street NW and 1531 Church Street NW'
        expected_result = []
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed composite of many delimiter cases")

        # clean up needed #
        # case 8: single address passed
        address_str = '1110 Aspen Street NW'
        result = helper_funs.identify_valid_unique_address(address_str)
        self.assertTrue(result, 'Failed - returned empty list')
        self.assertEqual(len(result), 1, 'Incorrect number of addresses')
        self.assertEqual(address_str, result.pop(),
                         'Failed single address validation')


if __name__ == '__main__':
    unittest.main()
