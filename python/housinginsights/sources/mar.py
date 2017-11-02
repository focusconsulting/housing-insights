
from pprint import pprint
from time import sleep

from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.mar import MarResult, FIELDS
from housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="sources.log")


class MarApiConn(BaseApiConn):
    """
    API Interface to the Master Address Record (MAR) database.
    Use public methods to retrieve data.
    """

    BASEURL = 'http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx'

    def __init__(self, baseurl=None, proxies=None,
                 database_choice=None, debug=False):
        super().__init__(baseurl=MarApiConn.BASEURL)
        self.error_counter = 0
        self.SLEEP_BASE_INT = 0.05  # default value for sleep interval in secs
        self.MAX_RETRY = 3  # controls max number retries until exception thrown

    def _handle_status_code_error(self, status_code, retry_secs, lookup_method,
                                  *args):
        """
        Helper function for error code handling - currently only used for 503
        status error codes. Could be easily expanded for others if we run
        into more.

        If MAX_RETRY is exceeded, the error logged and an exception is thrown.

        :param status_code: passed status code that was flagged in response
        :param retry_secs: try to capture indicated recommended server wait
        time in seconds
        :param lookup_method: string representation of the method that was
        called that lead to the response error code thrown
        :param args: the necessary args needed to retry the method again
        """
        self.error_counter += 1
        err = "{0} :An error occurred during request: status {1} - " \
              "method called {2}"

        # if exceed MAX_RETRY or not 503 code - log error and throw exception
        if self.error_counter > self.MAX_RETRY or status_code != 503:
            self.error_counter = 0  # reset counter
            err.format('FAIL', status_code, lookup_method)
            logger.exception(err)
            raise Exception(err)
        else:
            err.format('TRYING AGAIN', status_code, lookup_method)
            logger.exception(err)

        # sleep for a moment
        if retry_secs is None:
            sleep(self.SLEEP_BASE_INT * self.error_counter)
        else:
            sleep(retry_secs)  # based on server provided period of time

        # retry previously called method again
        if lookup_method == 'find_location':
            location, output_type, output_file = args
            self.find_location(location, output_type, output_file)
        elif lookup_method == 'reverse_geocode':
            xcoord, ycoord, output_type, output_file = args
            self.reverse_geocode(xcoord, ycoord, output_type, output_file)
        elif lookup_method == 'find_addr_string':
            address, output_type, output_file = args
            self.find_addr_string(address, output_type, output_file)
        elif lookup_method == 'reverse_lat_lng_geocode':
            latitude, longitude, output_type, output_file = args
            self.reverse_lat_lng_geocode(latitude, longitude, output_type,
                                         output_file)
        elif lookup_method == 'reverse_address_id':
            aid, output_type, output_file = args
            self.reverse_address_id(aid, output_type, output_file)

    def find_addr_string(self, address, output_type=None, output_file=None):
        """
        Get information about an address by using a complete address string

        :param address: Full address in approx. form of 123 Main St NW
        :type  address: String.

        :param output_type: deprecated, always returns json
        :type  output_type: String.

        :param output_file: Output file specified by user.
        :type  output_file: String

        :returns: Json output from the api.
        :rtype: String
        """
        params = {
            'f': 'json',
            'address': address
        }

        result = self.get('/verifyDCAddressThrouString2', params=params)  
        if result.status_code != 200:
            self._handle_status_code_error(result.status_code,
                                           result.headers['retry-after'],
                                           'find_addr_string', address,
                                           output_type, output_file)

        # reset counter
        self.error_counter = 0
        return result.json()

    def find_location(self, location, output_type=None,
                      output_file=None):

        """
        Get information on a location based on a simple query string.
        Warning - can return unintuitive results due to overly loose
        string matching logic in the MAR server. 

        Recommend using find_addr_string instead

        :param location: Location query.
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
            'str': location
        }
        result = self.get('/findLocation2', params=params)
        if result.status_code != 200:
            self._handle_status_code_error(result.status_code,
                                           result.headers['retry-after'],
                                           'find_location', location,
                                           output_type, output_file)
        if output_type == 'stdout':
            pprint(result.json())
        elif output_type == 'csv':
            data = result.json()['returnDataset']['Table1']
            results = [MarResult(address).data for address in data]
            self.result_to_csv(FIELDS, results, output_file)

        # reset counter
        self.error_counter = 0
        return result.json()

    def reverse_geocode(self, xcoord, ycoord, output_type=None,
                        output_file=None):
        """
        Do a reverse geocode lookup for address/alias points within 200 meters
        from the given Maryland State Plane (NAD 83) coordinates and returns the nearest five.
        Returned distance is given in meters.

        :param xcoord: Xcoordinate
        :type xcoord: String

        :param ycoord: Ycoordinate
        :type  ycoord: String

        :param output_type: Output type specified by user.
        :type  output_type: String.

        :param output_file: Output file specified by user.
        :type  output_file: String

        :returns: Json output from the api.
        :rtype: String
        """
        params = {
            'f': 'json',
            'x': xcoord,
            'y': ycoord
        }
        result = self.get('/reverseGeocoding2', params=params)
        if result.status_code != 200:
            self._handle_status_code_error(result.status_code,
                                           result.headers['retry-after'],
                                           'reverse_geocode', xcoord, ycoord,
                                           output_type, output_file)
        if output_type == 'stdout':
            pprint(result.json())
        elif output_type == 'csv':
            data = result.json()['Table1']
            results = [MarResult(address) for address in data]
            self.result_to_csv(FIELDS, results, output_file)

        # reset counter
        self.error_counter = 0
        return result.json()

    def get_condo_count(self, location, output_type=None,
                        output_file=None):
        """
        Get a count of all the condos at a particular address.
        Use sparingly, because it needs to make 3 requests
        to get the information (this api tho...).

        Get information on a location based on a simple query string.

        :param location: Location query.
        :type  location: String.

        :param output_type: Output type specified by user.
        :type  output_type: String.

        :param output_file: Output file specified by user.
        :type  output_file: String

        :returns: Json output from the api.
        :rtype: String
        """
        aid = self._get_address_id(location)
        units = self._find_condo_unit(aid)
        result = len(units['returnDataset']['Table1'])
        if output_type == 'stdout':
            print("Number of condos is: {0}".format(result))
        return result

    def get_condo_info(self, location, output_type=None,
                       output_file=None):
        pass  # TODO

    def _find_condo_unit(self, address_id):
        """
        Find condo information from an address id.

        :param address_id: Address id of the residence.
        :type  address_id: String.
        """
        params = {
            'f': 'json',
            'AID': address_id
        }
        result = self.get('/FindCondoUnitFromAID2', params=params)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))
        return result.json()

    def _get_address_id(self, location):
        """
        Get the address id of a location.

        :param location: Location query string.
        :type  location: String.

        :returns: Address id
        :rtype: String
        """
        result = self.find_location(location)
        # Return the first result.
        address_id = result['returnDataset']['Table1'][0]['ADDRESS_ID']
        return address_id

    def reverse_lat_lng_geocode(self, latitude, longitude, output_type=None,
                                output_file=None):
        """
        Do a reverse geocode lookup for MAR address/alias points within 200 
        meters from the given Latitude and Longitude coordinates and returns 
        the nearest five. The returned distance unit is meter.
        
        :param latitude: Latitude
        :type latitude: str
        
        :param longitude: Longitude
        :type longitude: str
        
        :param output_type: Output type specified by user.
        :type  output_type: str
        
        :param output_file: Output file specified by user.
        :type  output_file: str

        :returns: Json output from the api.
        :rtype: json
        """
        params = {
            'f': 'json',
            'lat': latitude,
            'lng': longitude
        }
        result = self.get('/reverseLatLngGeocoding2', params=params)
        if result.status_code != 200:
            self._handle_status_code_error(result.status_code,
                                           result.headers['retry-after'],
                                           'reverse_lat_lng_geocode', latitude,
                                           longitude, output_type, output_file)
        if output_type == 'stdout':
            pprint(result.json())
        elif output_type == 'csv':
            data = result.json()['Table1']
            results = [MarResult(address) for address in data]
            self.result_to_csv(FIELDS, results, output_file)

        # reset counter
        self.error_counter = 0
        return result.json()

    def reverse_address_id(self, aid, output_type=None, output_file=None):
        """
        Returns mars location result when given a valid address id (aid).
        
        :param aid: address id to lookup
        :type aid: integer
        
        :param output_type: Output type specified by user.
        :type  output_type: str
        
        :param output_file: Output file specified by user.
        :type  output_file: str

        :returns: Json output from the api.
        :rtype: json 

        Example resulting API url: http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx/findAID2?f=json&aid=233807
        """
        params = {
            'f': 'json',
            'AID': aid,
        }
        result = self.get('/findAID2', params=params)
        if result.status_code != 200:
            self._handle_status_code_error(result.status_code,
                                           result.headers['retry-after'],
                                           'reverse_address_id', aid,
                                           output_type, output_file)
        if output_type == 'stdout':
            pprint(result.json())
        elif output_type == 'csv':
            data = result.json()['Table1']
            results = [MarResult(address) for address in data]
            self.result_to_csv(FIELDS, results, output_file)

        # reset counter
        self.error_counter = 0
        return result.json()
