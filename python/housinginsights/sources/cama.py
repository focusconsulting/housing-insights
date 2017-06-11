from pprint import pprint
import os
import sys
import requests
from collections import OrderedDictq
import csv
import datetime

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(PYTHON_PATH)

from housinginsights.sources.base import BaseApiConn


class MarApiConn_2(BaseApiConn):
    """
    API Interface to the Master Address Record (MAR) database.
    Use public methods to retrieve data.
    """

    BASEURL = 'http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx'

    def __init__(self):
        super().__init__(MarApiConn_2.BASEURL)

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
            mar_returns = {'anc': entry['ANC'],
                           'census_tract': entry['CENSUS_TRACT'],
                           'neighborhood_cluster': entry['CLUSTER_'],
                           'ward': entry['WARD'],
                           'zip': entry['ZIPCODE']
            }

        return mar_returns

class CamaApiConn(BaseApiConn):
    """
    API Interface to the Computer Assisted Mass Appraisal - Residential (CAMA)
    API, to obtain SSL numbers to use as input for the  MarApiConn_2 and get
    the corresponding housing and bedroom units.
    """

    BASEURL = 'https://opendata.arcgis.com/datasets'
    def __init__(self):
        super().__init__(CamaApiConn.BASEURL)

    def get_data(self):
        """
        Grabs data from CAMA. Individual CAMA property retrieves zone_type data
        from MAR api. Count number of housing units and bedroom units per zone.
        Return the count data (in dictionary form) to be processed into csv
        by get_csv() method.
        """

        mar_api = MarApiConn_2()
        result = self.get(urlpath='/c5fb3fbe4c694a59a6eef7bf5f8bc49a_25.geojson', params=None)

        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))
        cama_data = result.json()

        """
        Example of: anc_count = [OrderedDict([('zone_type', 'anc'), ('zone', 'ANC 2B'), 
                                ('housing_unit_count', 10), ('bedroom_unit_count', 10)], etc)]
        """
        zone_types = ['anc', 'census_tract', 'neighborhood_cluster', 'ward', 'zip']
        anc_count = []
        census_count = []
        cluster_count = []
        ward_count = []
        zipcode_count = []


        """
        Take each CAMA property data and retrieve the MAR data.
        """
        """
        Certain square values have four digits + a letter. (ex. 8888E)
        Square would be the first four digits and suffix would be the letter.
        SSL sometimes comes as 8 digit string without spacing in the middle.
        """
        """
        CAMA data includes bldgs under construction. CAMA's data includes AYB of 2018
        as of June 2017. We eliminate all data points that are under construction and
        don't provide any housing units and bedrm at this time.
        """
        for row in cama_data['features']:
            try:
                current_year = int(datetime.date.today().strftime('%Y'))
                #Skipping none values for units under construction
                if row['properties']['AYB'] is not None and int(row['properties']['AYB']) > current_year:
                    continue

                objectid = row['properties']['OBJECTID']
                if len(row['properties']['SSL']) == 8:
                    square = row['properties']['SSL'][:4]
                    lot = row['properties']['SSL'][4:]
                else:
                    square, lot = row['properties']['SSL'].split()
                suffix = ' '
                if len(square) > 4:
                    square = square[:4]
                    suffix = square[-1]

                mar_return = mar_api.get_data(square, lot, suffix)

                ''' Count the housing units and bedrooms '''
                num_units = 0
                if row['properties']['NUM_UNITS']: num_units = row['properties']['NUM_UNITS']
                if num_units == 0:
                    num_units = 1

                bedrm = row['properties']['BEDRM']
                if bedrm == 0: bedrm = 1
                if bedrm == None: bedrm = 0

                for zone in zone_types:
                    if zone == 'anc': zone_count = anc_count
                    elif zone == 'census_tract': zone_count = census_count
                    elif zone == 'neighborhood_cluster': zone_count = cluster_count
                    elif zone == 'ward': zone_count = ward_count
                    elif zone == 'zip': zone_count = zipcode_count

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

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(exc_type, "line", exc_tb.tb_lineno)
                print("Error! SSL: ", row['properties']['SSL'], row['properties']['AYB'])
                continue

        return {'anc': anc_count, 'census_tract': census_count, 'neighborhood_cluster': cluster_count, 'ward': ward_count, 'zip': zipcode_count}


    def get_csv(self):
        """
        Takes the returned dictionary from get_data() and convert the information
        into csv file and then save the csv file in
        housing-insights/data/processed/zoneUnitCount
        as zoneUnitCount_2017-05-30.csv.
        """

        if not os.path.exists('../../../data/processed/zoneUnitCount'):
            os.makedirs('../../../data/processed/zoneUnitCount')


        data_processed_zoneUnitCount = os.path.join(PYTHON_PATH, os.pardir, 'data', 'processed', 'zoneUnitCount')

        zone_data = self.get_data()
        toCSV = []
        date = datetime.date.today().strftime('%Y-%m-%d')
        filename = os.path.join(data_processed_zoneUnitCount, 'zoneUnitCount_'+date+'.csv')

        for key, value in zone_data.items():
            toCSV.extend(value)

        keys = toCSV[0].keys()

        with open(filename, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(toCSV)


my_api = CamaApiConn()
csvfile = my_api.get_csv()
