"""
Base Api Connection classes.
"""

from urllib.parse import urljoin
from datetime import datetime
from uuid import uuid4

from housinginsights.config.base import HousingInsightsConfig
from housinginsights.sources.models.pres_cat import PROJ_FIELDS, SUBSIDY_FIELDS
from housinginsights.tools import dbtools

import requests
import csv
import os
from housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="sources.log")


class BaseApiConn(object):
    """
    Base API Connection to inherit from. Proxy support built in.

    Every XXXApiConn class that inherits from this class should have a few key features:

    If the class downloads whole data files for ingestion into our database:
    - get_data() method should be a one-call method that downloads all the files that class
      is capable of downloading. It should have 0 mandatory arguments, and at a minimum
      the following optional arguments:
        - unique_data_ids
        - sample (Boolean). If possible, return just a few rows of data instead of the whole thing
        - output_type ('csv' or 'stdout'). 'csv' should write the file to disk, 'stdout' prints to console
    - __init__ should have _available_unique_data_ids, a list of ids that the class can output.



    """

    def __init__(self, baseurl=None, proxies=None, database_choice=None, debug=False):
        """
        :param baseurl: URL endpoint of the API.
        :type baseurl: String.

        :param proxies: Proxies to use for the connection (HTTP or socks5).
                        Example: {'http': 'socks5://user:pass@someip:port',
                                  'https': 'socks5://user:pass@someip:port'}
        :type  proxies: dict of String.

        :param database_choice: String containing the name of the database to connect
            when existing data needs to be used. String should match the one found in
            secrets.json. Optional - not used by BaseApiConn, but sometimes used by others.
        """
        self.session = requests.Session()
        self.baseurl = baseurl
        self.proxies = proxies
        self.debug = debug

        # A list of strings; this should be defined in the child class
        self._available_unique_data_ids = None

    @property
    def output_paths(self):
        if self._available_unique_data_ids is None:
            raise NotImplementedError(
                "You need to add self._available_unique_data_ids to your class before using it"
            )

        paths = {}
        for u in self._available_unique_data_ids:
            base = os.path.abspath(
                os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
            )
            api_location = "data/raw/_downloads"
            filename = u + ".csv"
            d = datetime.now().strftime("%Y%m%d")
            path = os.path.join(base, api_location, d, filename)
            paths[u] = path

            # So output methods don't need to deal with missing dirs
            self.create_directory_if_missing(path)
        return paths

    def get(self, urlpath, params=None, **kwargs):
        """
        Thin wrapper around requests.get() that adds in proxy value
        and relative url joining.

        :param urlpath: URL path to be joined to the baseurl.

                        Example: if baseurl is https://www.somesite.com/api,
                                 and urlpath is /v2, the end result
                                 is https://www.somesite.com/api/v2.

                        If baseurl == None, the urlpath is used directly.

        :type  urlpath: String.

        :param params: Dictionary of request parameters.
        :type  params: dict of String.
        """
        if self.baseurl != None:
            if self.baseurl[-1] == "/":
                self.baseurl = self.baseurl[:-1]
            if urlpath[0] != "/":
                urlpath = "/" + urlpath
            url = self.baseurl + urlpath
        else:
            url = urlpath

        logger.info("Requested URL %s with params %s", url, params)
        return self.session.get(url, params=params, proxies=self.proxies, **kwargs)

    def post(self, urlpath, data=None, **kwargs):
        """
        Thin wrapper around requests.post() that adds in proxy value
        and relative url joining.

        :param urlpath: URL path to be joined to the baseurl.
                        Example: if baseurl is https://www.somesite.com/api,
                                 and urlpath is /v2, the end result
                                 is https://www.somesite.com/api/v2.
        :type  urlpath: String.

        :param params: Dictionary of request parameters.
        :type  params: dict of String.
        """
        url = urljoin(self.baseurl, urlpath)
        return self.session.post(url, data=data, proxies=self.proxies, **kwargs)

    def create_directory_if_missing(self, filepath):
        """
        Ensure there is a directory for given filepath, if doesn't exists it creates ones.

        :param filepath: file path for where to write and save csv file
        :type filepath: string

        :return: None
        """
        directory = os.path.dirname(filepath)
        os.makedirs(directory, exist_ok=True)

    def result_to_csv(self, fields, results, filepath):
        """
        Write the data to a csv file.

        :param fields: column headers for the data set
        :type fields: list

        :param results: field values for each row
        :type results: list

        :param filepath: file path for where to write and save csv file
        :type filepath: string

        :return: None
        """
        self.create_directory_if_missing(filepath)
        with open(filepath, "w", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(fields)
            for result in results:
                writer.writerow(result)

    def directly_to_file(self, data, filepath):
        """
        Write the data to a file

        :param data: raw data to write to file
        :type data: string

        :param filepath: file path for where to write and save csv file
        :type filepath: string

        :return: None
        """
        self.create_directory_if_missing(filepath)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(data)


class BaseApiManager(object):

    classname = "base"

    def __init__(self, config_file):
        self.config = self.get_config(config_file)

    def get_config(self, config_file):
        config = HousingInsightsConfig(config_file)
        return config.get_section(self.__class__.classname)
