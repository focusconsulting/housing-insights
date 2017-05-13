"""
Module provides the api connection class for DCHousing data in opendata.dc.gov
web site.
"""

from pprint import pprint


from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.DCHousing import FIELDS,\
    DCHousingResult


class DCHousingApiConn(BaseApiConn):
    """
    API Interface to the Affordable Housing data set on opendata.dc.gov.

    Inherits from BaseApiConn class.
    """

    BASEURL = 'http://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/' \
              'Property_and_Land_WebMercator/MapServer/62'
    # default query to get all data as json output
    QUERY = '/query?where=1%3D1&outFields=*&outSR=4326&f=json'

    def __init__(self):
        super().__init__(DCHousingApiConn.BASEURL)

    def get_json(self, output_type=None, output_file=None):
        """
        Returns JSON object of the entire data set.

        :param output_type: Output type specified by user.
        :type  output_type: String.

        :param output_file: Output file specified by user.
        :type  output_file: String

        :returns: Json output from the api.
        :rtype: String
        """
        result = self.get(DCHousingApiConn.QUERY)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))

        if output_type == 'stdout':
            pprint(result.json())
        elif output_type == 'csv':
            data = result.json()['features']
            results = [DCHousingResult(address['attributes']) for address in
                       data]
            self.result_to_csv(FIELDS, results, output_file)

        return result.json()