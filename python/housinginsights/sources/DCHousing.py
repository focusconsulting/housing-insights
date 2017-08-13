"""
Module provides the api connection class for DCHousing data in opendata.dc.gov
web site.
"""

from pprint import pprint
import logging

from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.DCHousing import FIELDS,\
    DCHousingResult
from housinginsights.sources.models.DCHousing import PROJECT_FIELDS_MAP,\
    SUBSIDY_FIELDS_MAP


class DCHousingApiConn(ProjectBaseApiConn):
    """
    API Interface to the Affordable Housing data set on opendata.dc.gov.

    Inherits from BaseApiConn class.
    """

    # constants for downloading data via api query
    API_BASEURL = 'http://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/' \
              'Property_and_Land_WebMercator/MapServer/62'
    # default query to get all data as json output
    API_QUERY = '/query?where=1%3D1&outFields=*&outSR=4326&f=json'

    # constants for batch download as csv
    BASEURL = 'https://opendata.arcgis.com/datasets/'
    DATA_URL = '34ae3d3c9752434a8c03aca5deb550eb_62.csv'

    def __init__(self):
        super().__init__(DCHousingApiConn.BASEURL)

        self._available_unique_data_ids = ['dchousing']

    def get_data(self, unique_data_ids=None, sample=False, output_type='csv',
                 **kwargs):
        """
        """
        if unique_data_ids is None:
            unique_data_ids = self._available_unique_data_ids

        db = kwargs.get('db', None)

        for u in unique_data_ids:
            if u not in self._available_unique_data_ids:
                #TODO this will always be raised when passing a list to get_multiple_api_sources method for those not in this class. 
                logging.info("  The unique_data_id '{}' is not supported by the DCHousingApiConn".format(u))

            else:
                result = self.get(DCHousingApiConn.DATA_URL)
                if result.status_code != 200:
                    err = "An error occurred during request: status {0}"
                    raise Exception(err.format(result.status_code))

                content = result.text

                if output_type == 'stdout':
                    print(content)
                elif output_type == 'csv':
                    self.directly_to_file(data=content,
                                          filepath=self.output_paths[u])
                    self.create_project_subsidy_csv(
                        self._available_unique_data_ids[0], PROJECT_FIELDS_MAP,
                        SUBSIDY_FIELDS_MAP, db)


if __name__ == '__main__':
    
    apiConn = DCHousingApiConn()
    apiConn.create_project_subsidy_csv()