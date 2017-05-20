"""
Base Api Connection classes.
"""

from urllib.parse import urljoin

from housinginsights.config.base import HousingInsightsConfig

import requests
import csv
import os


class BaseApiConn(object):
    """
    Base API Connection to inherit from. Proxy support is built in,
    because if you do enough scraping, I promise you you're gonna get
    your IP blocked at some point.
    """
    def __init__(self, baseurl, proxies=None):
        """
        :param baseurl: URL endpoint of the API.
        :type baseurl: String.

        :param proxies: Proxies to use for the connection (HTTP or socks5).
                        Example: {'http': 'socks5://user:pass@someip:port',
                                  'https': 'socks5://user:pass@someip:port'}
        :type  proxies: dict of String.
        """
        self.session = requests.Session()
        self.baseurl = baseurl
        self.proxies = proxies

    def get(self, urlpath, params=None, **kwargs):
        """
        Thin wrapper around requests.get() that adds in proxy value
        and relative url joining.

        :param urlpath: URL path to be joined to the baseurl.
                        Example: if baseurl is https://www.somesite.com/api,
                                 and urlpath is /v2, the end result
                                 is https://www.somesite.com/api/v2.
        :type  urlpath: String.

        :param params: Dictionary of request parameters.
        :type  params: dict of String.
        """
        if self.baseurl[-1] == '/':
            self.baseurl = self.baseurl[:-1]
        if urlpath[0] != '/':
            urlpath = '/' + urlpath
        url = self.baseurl + urlpath
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

    def result_to_csv(self, fields, results, csvfile):
        """
        Write the data to a csv file.

        :param fields: column headers for the data set
        :type fields: list

        :param results: field values for each row
        :type results: list

        :param csvfile: file path for where to write and save csv file
        :type csvfile: string

        :return: None
        """
        with open(csvfile, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(fields)
            for result in results:
                writer.writerow(result.data)

    def add_file(self, outdir, outfile):
        """
        Create an output directory if it doesn't already exist.

        :param outfile: file path for where to write and save csv file
        :type outfile: string

        :return: None
        """
        if not os.path.isdir(outdir):
            os.mkdir(outdir)

        if not os.path.exists(outdir+outfile):
            open(outdir+outfile, 'w').close()


class BaseApiManager(object):

    classname = "base"

    def __init__(self, config_file):
        self.config = self.get_config(config_file)

    def get_config(self, config_file):
        config = HousingInsightsConfig(config_file)
        return config.get_section(self.__class__.classname)

