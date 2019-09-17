import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir)))

import housinginsights.tools.misc as misc_tools


class ToolsMiscTestCase(unittest.TestCase):

    def test_get_unique_addresses_from_str(self):
        # Cases for multiple addresses delimiters #
        # case 1: ';' delimiter separated addresses
        address_str = '1110 Aspen Street NW; 6650 Georgia Avenue NW; ' \
                      '6656 Georgia Avenue NW; others'
        expected_result = ['1110 Aspen Street NW', '6650 Georgia Avenue NW',
                           '6656 Georgia Avenue NW', 'others']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed ";" - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed ";" - returned less/more unique '
                         'addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed ';' delimiter case: {}".format(address))

        # case 2: 'and' delimiter separated address
        address_str = '1110 Aspen Street NW and 6650 Georgia Avenue NW'
        expected_result = ['1110 Aspen Street NW', '6650 Georgia Avenue NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed " and " - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed " and " - returned less/more unique '
                         'addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed "and" delimiter case: {}'.format(address))

        # Cases for address number ranges #
        # case 3: '&' delimiter separated address
        address_str = '1521 & 1523 16th Street NW'
        expected_result = ['1521 16th Street NW', '1523 16th Street NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed "&" - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed "&" - returned less/more unique '
                         'addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed "&" delimiter case: {}'.format(address))

        """
        Separating into multiple cases for now but it seems best to assume 
        +2 when given address number ranges. Examples for real data seems to 
        confirm this.
        """
        # case 4a: '-' odd delimiter address number ranges
        address_str = '1309-1313 E Street SE'
        expected_result = ['1309 E Street SE', '1311 E Street SE',
                           '1313 E Street SE']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed odd "-" - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed odd "-" - returned less/more unique '
                         'addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed odd "-" delimiter case: {}'.format(address))

        # case 4b: '-' even delimiter address number ranges
        address_str = '4000-4008 8th Street NE'
        expected_result = ['4000 8th Street NE', '4002 8th Street NE',
                           '4004 8th Street NE', '4006 8th Street NE',
                           '4008 8th Street NE']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed even "-" - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed even "-" - returned less/more unique '
                         'addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed even "-" delimiter case: {}'.format(
                                address))

        # case 4c: '-' ambiguous delimiter address number ranges
        address_str = '4000-4005 8th Street NE'
        expected_result = ['4000 8th Street NE', '4002 8th Street NE',
                           '4004 8th Street NE', '4001 8th Street NE',
                           '4003 8th Street NE', '4005 8th Street NE']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed ambiguous "-" - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed ambiguous "-" - returned less/more unique '
                         'addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed ambiguous "-" delimiter case: {}'.format(
                                address))

        # Cases for composites #
        # case 5: '&' + 'and' delimiter separated addresses
        address_str = '1521 & 1523 16th Street NW and 1531 Church Street NW'
        expected_result = ['1521 16th Street NW', '1523 16th Street NW',
                           '1531 Church Street NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed "&" + " and " - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed "&" + " and " - returned less/more unique '
                         'addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed '&' + 'and' delimiter "
                            "composite: {}".format(address))

        # case 6: both addresses delimiter and address number ranges
        address_str = '1110 Aspen Street NW; 4000-4005 8th Street NE; ' \
                      '6650 Georgia Avenue NW; 2420-2428 14th Street NE'
        expected_result = ['1110 Aspen Street NW', '4000 8th Street NE',
                           '4002 8th Street NE', '4004 8th Street NE',
                           '4001 8th Street NE', '4003 8th Street NE',
                           '4005 8th Street NE', '6650 Georgia Avenue NW',
                           '2420 14th Street NE', '2422 14th Street NE',
                           '2424 14th Street NE', '2426 14th Street NE',
                           '2428 14th Street NE']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed both number range and multiple '
                                'addresses delimiter - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed both number range and multiple addresses '
                         'delimiter - returned less/more unique '
                         'addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed both number range and address delimiter"
                            " cases: {}".format(address))

        # case 7: composite of many delimiters
        address_str = '4232-4238 4th Street SE and 4281-4285 6th Street SE; ' \
                      '1521 & 1523 16th Street NW and 1531 Church Street NW'
        expected_result = ['4232 4th Street SE', '4234 4th Street SE',
                           '4236 4th Street SE', '4238 4th Street SE',
                           '4281 6th Street SE', '4283 6th Street SE',
                           '4285 6th Street SE', '1523 16th Street NW',
                           '1521 16th Street NW', '1531 Church Street NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed composite of many delimiter - returned '
                                'empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed composite of many delimiter - returned '
                         'less/more unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed composite of many delimiter "
                            "cases: {}".format(address))

        # case 8: single address passed
        address_str = '1110 Aspen Street NW'
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed single address - returned empty list')
        self.assertEqual(len(result), 1,
                         'Failed single address - returned less/more unique '
                         'addresses {}'.format(result))
        self.assertEqual(address_str, result[0],
                         'Failed single address validation: {}'.format(
                             result[0]))

        # Messy cases involving commas #
        # case 9a: simple comma delimited address numbers only
        address_str = '6616, 6626 GEORGIA AVE NW'
        expected_result = ['6616 GEORGIA AVE NW', '6626 GEORGIA AVE NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed single address number range comma '
                                'delimiter - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed single address number range comma delimiter - '
                         'returned less/more unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            "Failed single address number range comma "
                            "delimiter case: {}".format(address))

        # case 9b: comma delimited address numbers only
        address_str = '6606, 6606, 6616, 6626 GEORGIA AVE NW'
        expected_result = ['6606 GEORGIA AVE NW', '6606 GEORGIA AVE NW',
                           '6616 GEORGIA AVE NW', '6626 GEORGIA AVE NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed multiple address number range comma '
                                'delimiter - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed multiple address number range comma '
                         'delimiter - returned less/more unique '
                         'addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed multiple address number range comma '
                            'delimiter case: {}'.format(address))

        # case 9c: clean up unnecessary comma
        address_str = '1864 CENTRAL PLACE, NE'
        expected_result = ['1864 CENTRAL PLACE NE']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed remove extra comma - returned '
                                'empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed remove extra comma - returned less/more '
                         'unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed remove extra comma case: {}'.format(
                                address))

        # case 9d: comma delimited address numbers and street
        address_str = '1860,1862,1864 CENTRAL PLACE, NE'
        expected_result = ['1860 CENTRAL PLACE NE', '1862 CENTRAL PLACE NE',
                           '1864 CENTRAL PLACE NE']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed remove extra comma + multiple address'
                                ' number range comma delimiter - returned '
                                'empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed remove extra comma + multiple address number '
                         'range comma delimiter - returned less/more '
                         'unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed remove extra comma + multiple address '
                            'number range comma delimiter case: {}'.format(
                                address))

        # case 10a: remove extra comma and '-' number range composite case
        address_str = '1210-1214 SOUTHERN AVE, S.E.'
        expected_result = ['1210 SOUTHERN AVE S.E.',
                           '1212 SOUTHERN AVE S.E.',
                           '1214 SOUTHERN AVE S.E.']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed remove extra comma + "-" - returned '
                                'empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed remove extra comma + "-" - returned less/more '
                         'unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed remove extra comma + "-" case: {}'.format(
                                address))

        # case 10b: shorthand '-' delimiter and remove extra comma composite
        address_str = '1210-14 SOUTHERN AVE, S.E.'
        expected_result = ['1210 SOUTHERN AVE S.E.',
                           '1212 SOUTHERN AVE S.E.',
                           '1214 SOUTHERN AVE S.E.']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed shorthand "-" + remove extra comma '
                                'composite - returned empty list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed shorthand "-" + remove extra comma - returned '
                         'less/more unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed shorthand "-" + remove extra comma '
                            'composite: {}'.format(address))

        # case 11: '&' and comma delimiter composite
        address_str = '24, 52, & 230 BATES ST NW'
        expected_result = ['230 BATES ST NW', '24 BATES ST NW',
                           '52 BATES ST NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed "&" + comma composite - returned empty '
                                'list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed "&" and comma composite - returned less/more '
                         'unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed "&" and comma composite: {}'.format(
                                address))

        # case 12: funky '&' case clean up and remove extra comma - invalid
        # building address
        address_str = 'HAYES STREET &ANACOSTIA AVENUE, NORTH EAST'
        expected_result = ['HAYES STREET & ANACOSTIA AVENUE NORTH EAST']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed funky "&" clean up - returned empty '
                                'list')
        self.assertEqual(len(expected_result), len(result),
                         'Failed funky "&" clean up - returned less/more '
                         'unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed funky "&" clean up case: {}'.format(
                                address))

        # case 13: '-', '&', and comma address number range composite
        address_str = '1416-1420,1432,1436 & 1440 R ST NW'
        expected_result = ['1440 R ST NW', '1420 R ST NW',
                           '1432 R ST NW', '1436 R ST NW',
                           '1416 R ST NW', '1418 R ST NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed "-" + "&" + comma composite - returned '
                                'empty list')
        self.assertEqual(len(result), len(expected_result),
                         'Failed "-" + "&" + comma composite - returned '
                         'less/more unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed "-" + "&" + comma composite '
                            'case: {}'.format(address))

        # 'dirty' cases - return original string
        # case 14a: invalid '&' with address number
        address_str = '1416-1440 R & 14th ST NW'
        expected_result = ['1416-1440 R & 14th ST NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed handling invalid "&" - '
                                'returned empty list')
        self.assertEqual(len(result), len(expected_result),
                         'Failed handling invalid "&" - returned '
                         'less/more unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed handling invalid "&" case: {}'.format(
                                address))

        # case 14b: invalid '&' (intersections)
        address_str = 'HAYES STREET &ANACOSTIA AVENUE NORTH EAST'
        expected_result = ['HAYES STREET &ANACOSTIA AVENUE NORTH EAST']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed handling invalid "&" - '
                                'returned empty list')
        self.assertEqual(len(result), len(expected_result),
                         'Failed handling invalid "&" - returned '
                         'less/more unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed handling invalid "&" case: {}'.format(
                                address))

        # case 15a: incomplete dash address number range
        address_str = '1416- R ST NW'
        expected_result = ['1416- R ST NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed incomplete dash address number - '
                                'returned empty list')
        self.assertEqual(len(result), len(expected_result),
                         'Failed incomplete dash address number - returned '
                         'less/more unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed incomplete dash address number '
                            'case: {}'.format(address))

        # case 15b: incomplete comma address number range
        address_str = '1416, R ST NW'
        expected_result = ['1416, R ST NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed incomplete comma address number - '
                                'returned empty list')
        self.assertEqual(len(result), len(expected_result),
                         'Failed incomplete comma address number - returned '
                         'less/more unique addresses {}'.format(result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed incomplete comma address number '
                            'case: {}'.format(address))

        # case 15c: incomplete ampersand address number range
        address_str = '1416 & R ST NW'
        expected_result = ['1416 & R ST NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed incomplete ampersand address number - '
                                'returned empty list')
        self.assertEqual(len(result), len(expected_result),
                         'Failed incomplete ampersand address number - '
                         'returned less/more unique addresses {}'.format(
                             result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed incomplete ampersand address number '
                            'case: {}'.format(address))

        # case 16: multiple contiguous '-', '&', ',': assuming invalid address
        address_str = '1416 && 1418 R ST NW; 1416--1418 R ST NW; ' \
                      '1416,, 1418 R ST NW; 1416 &-, 1418 R ST NW'
        expected_result = ['1416 && 1418 R ST NW', '1416--1418 R ST NW',
                           '1416,, 1418 R ST NW', '1416 &-, 1418 R ST NW']
        result = misc_tools.get_unique_addresses_from_str(address_str)
        self.assertTrue(result, 'Failed multiple contiguous range delimiter - '
                                'returned empty list')
        self.assertEqual(len(result), len(expected_result),
                         'Failed multiple contiguous range delimiter - '
                         'returned less/more unique addresses {}'.format(
                             result))
        for address in result:
            self.assertTrue(address in expected_result,
                            'Failed multiple contiguous range delimiter '
                            'case: {}'.format(address))


if __name__ == '__main__':
    unittest.main()
