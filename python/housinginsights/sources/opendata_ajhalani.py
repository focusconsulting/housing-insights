from housinginsights.sources.base import BaseApiConn


class OpendataApiConn(BaseApiConn):
    """
    API Interface to the open data api(opendata.dc.gov).
    Use public methods to retrieve data.
    """

    BASEURL = 'https://opendata.arcgis.com/datasets/'

    def __init__(self):
        super().__init__(OpendataApiConn.BASEURL)

    def get_data(self, csv_urlpath, output_type=None,
                      output_file=None):
        """
        Generic get data function for opendata
        :param csv_urlpath: csv url path 
        :type  location: String.

        :param output_type: Output type specified by user.
        :type  output_type: String.

        :param output_file: Output file specified by user.
        :type  output_file: String

        :returns: CSV output from the api.
        :rtype: String
        """
        result = self.get(csv_urlpath, params=None)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))
        content = result.text
        if output_type == 'stdout':
            print(content)
        elif output_type == 'csv':
            self.result_to_file(content, output_file)
        return content

    def get_crime(self, year, output_type=None,
                      output_file=None):
        """
        Get information on a location based on a simple query string.

        :param year: Year for which data crime data is requested.
        :type  location: String.

        :param output_type: Output type specified by user.
        :type  output_type: String.

        :param output_file: Output file specified by user.
        :type  output_file: String

        :returns: Json output from the api.
        :rtype: String
        """
        YEAR_TO_URLPATH={
            '2013' : '5fa2e43557f7484d89aac9e1e76158c9_10.csv',
            '2014' : '6eaf3e9713de44d3aa103622d51053b5_9.csv',
            '2015' : '35034fcb3b36499c84c94c069ab1a966_27.csv',
            '2016' : 'bda20763840448b58f8383bae800a843_26.csv',
            '2017' : '6af5cb8dc38e4bcbac8168b27ee104aa_8.csv'
        }
        if year not in YEAR_TO_URLPATH:
          raise Exception("Year {} data is not supported".format(year))
        return self.get_data(YEAR_TO_URLPATH[year], output_type, output_file)



