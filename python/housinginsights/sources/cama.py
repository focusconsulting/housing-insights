from pprint import pprint
import os
import sys
import requests
from collections import OrderedDict
import csv

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(PYTHON_PATH)

from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.mar import MarResult, FIELDS


class MarApiConn(BaseApiConn):
    """
    API Interface to the Master Address Record (MAR) database.
    Use public methods to retrieve data.
    """

    BASEURL = 'http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx'

    def __init__(self):
        super().__init__(MarApiConn.BASEURL)

    def get_data(self, square, lot, suffix):
        """
        Get information on a location based on a simple query string.
        :param square: SSL first part
        :type  location: String.
        :param lot: SSL second part
        :type  location: String.
        :param output_type: Output type specified by user.
        :type  output_type: String.
        :param output_file: Output file specified by user.
        :type  output_file: String
        :returns: Json output from the api.
        :rtype: String
        """
        params = {
            'f': 'json',
            'Square': square,
            'Lot': lot,
            'Suffix': suffix
        }

        result = self.get('/findAddFromSSL2', params=params)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))

        mar_data = result.json()
        if mar_data['returnDataset'] == {}:
            mar_returns = {'Warning': 'No MAR data availble - property under construction - see AYB year'}
        else:
            entry = mar_data['returnDataset']['Table1'][0]
            mar_returns = {'ANC': entry['ANC'],
                           'CENSUS_TRACT': entry['CENSUS_TRACT'],
                           'CLUSTER_': entry['CLUSTER_'],
                           'WARD': entry['WARD'],
                           'ZIPCODE': entry['ZIPCODE']
            }

        return mar_returns

class CamaApiConn(BaseApiConn):
    """
    API Interface to the Master Address Record (MAR) database.
    Use public methods to retrieve data.
    """

    BASEURL = 'https://opendata.arcgis.com/datasets'
    def __init__(self):
        super().__init__(CamaApiConn.BASEURL)

    def get_data(self):
        mar_api = MarApiConn()
        result = self.get(urlpath='/c5fb3fbe4c694a59a6eef7bf5f8bc49a_25.geojson', params=None)

        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))
        cama_data = result.json()

        dict_res = {}  # creates dict of residential data with SSL as primary key
        zone_types = ['ANC', 'CENSUS_TRACT', 'CLUSTER_', 'WARD', 'ZIPCODE']
        anc_count = []
        census_count = []
        cluster_count = []
        ward_count = []
        zipcode_count = []

        """ [:100] for the first 100 cama_data points """
        for row in cama_data['features'][:100]:
            objectid = row['properties']['OBJECTID']
            square, lot = row['properties']['SSL'].split()
            suffix = ' '
            if len(square) > 4:
                square = square[:4]
                suffix = square[-1]

            mar_return = mar_api.get_data(square, lot, suffix)
            row['properties'].update(mar_return)
            dict_res[row['properties']['OBJECTID']] = row['properties']


            ''' Count the units and bedrooms '''
            num_units = row['properties']['NUM_UNITS']
            if num_units == 0: num_units = 1
            bedrm = row['properties']['BEDRM']
            if bedrm == 0: bedrm = 1

            for zone in zone_types:
                if zone == 'ANC': zone_count = anc_count
                elif zone == 'CENSUS_TRACT': zone_count = census_count
                elif zone == 'CLUSTER_': zone_count = cluster_count
                elif zone == 'WARD': zone_count = ward_count
                elif zone == 'ZIPCODE': zone_count = zipcode_count

                if 'Warning' not in mar_return.keys():
                    flag = False
                    for dictionary in zone_count: #dictionary is {'zone_type': 'ANC', 'zone': 'ANC 8A', etc.}
                        if dictionary['zone'] == mar_return[zone]: #mar_return[ANC] is 'ANC 8A'
                            dictionary['housing_unit_count'] += num_units
                            dictionary['bedroom_unit_count'] += bedrm
                            flag = True
                            break
                    if not flag:
                        zone_count.append( OrderedDict([('zone_type', zone), ('zone', mar_return[zone]), ('housing_unit_count', num_units), ('bedroom_unit_count', bedrm)]) )

        return {'ANC': anc_count, 'CENSUS': census_count, 'CLUSTER': cluster_count, 'WARD': ward_count, 'ZIPCODE': zipcode_count}

    def get_csv(self):
        zone_data = self.get_data()
        toCSV = []

        for key, value in zone_data.items():
            # print("#"*100)
            # print("#"*100)
            # print("value: ", value)
            toCSV.extend(value)
            # print("#"*100)
            # print("#"*100)
            # print("toCSV: ", toCSV)

        keys = toCSV[0].keys()

        # print("#"*100)
        # print("#"*100)
        # print("keys: ", keys)

        with open('camaData.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(toCSV)


my_api = CamaApiConn()
csvfile = my_api.get_csv()
