"""
Base Api Connection classes.
"""

from urllib.parse import urljoin
from datetime import datetime
from uuid import uuid4

from housinginsights.config.base import HousingInsightsConfig
from housinginsights.sources.models.pres_cat import PROJ_FIELDS, \
    SUBSIDY_FIELDS
from housinginsights.tools import dbtools

import requests
import csv
import os


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


        #A list of strings; this should be defined in the child class 
        self._available_unique_data_ids = None

    @property
    def output_paths(self):
        if self._available_unique_data_ids is None:
            raise NotImplementedError("You need to add self._available_unique_data_ids to your class before using it")

        paths = {}
        for u in self._available_unique_data_ids:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,os.pardir,os.pardir))
            api_location = 'data/raw/apis'
            filename = u + ".csv"
            d = datetime.now().strftime('%Y%m%d')
            path = os.path.join(base,api_location,d,filename)
            paths[u] = path

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
            if self.baseurl[-1] == '/':
                self.baseurl = self.baseurl[:-1]
            if urlpath[0] != '/':
                urlpath = '/' + urlpath
            url = self.baseurl + urlpath
        else:
            url = urlpath

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
        directory=os.path.dirname(filepath)
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
        with open(filepath, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(fields)
            for result in results:
                writer.writerow(result.data)

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
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)

    def _map_data_for_row(self, nlihc_id, fields, fields_map, line):
        """
        Returns a dictionary that represents the values in line mapped to
        those fields in the given fields map.
        :param nlihc_id: the nlihc_id for the current line in dchousing data
        :param fields: the column headers data we want returned
        :param fields_map: a dictionary mapping for the dchousing headers to
        the field headers that should be returned
        :param line: the current line in the dchousing data to be mapped
        """
        data = {}
        for field in fields:
            value = fields_map[field]
            if value is None:
                if field == 'Nlihc_id':
                    data[field] = nlihc_id
                else:
                    data[field] = None
            else:
                data[field] = line[value]
        return data

    def _get_nlihc_id_from_db(self, db_conn, address_id):
        """
        Returns a tuple nlihc_id, in_proj_table_flag pair for a given address
        id by performing a lookup on the project table in the database using
        the mar_id column.

        If the address id doesn't map to an existing building in the table,
        a randomly generated uuid is returned as nlihc_id.
        """
        query = "select nlihc_id from project where mar_id = " \
                "'{}';".format(address_id)
        query_result = db_conn.execute(query)
        result = [dict(x) for x in query_result.fetchall()]

        if result:
            return result[0]['nlihc_id'], True
        else:
            return str(uuid4()), False

    def create_project_subsidy_csv(self, uid, project_fields_map,
                                   subsidy_fields_map, database_choice=None):
        """
        Writes 'source_project' and 'source_subsidy' raw files from the
        source csv file. It then deletes the source file so it
        doesn't get added to manifest and loaded into the database.
        """
        if database_choice is None:
            database_choice = 'docker_database'
        engine = dbtools.get_database_engine(database_choice)
        db_conn = engine.connect()

        # create file path objects
        source_csv = self.output_paths[uid]
        folder = os.path.dirname(source_csv)
        source_proj = os.path.join(folder, "{}_project.csv".format(uid))
        source_subsidy = os.path.join(folder, "{}_subsidy.csv".format(uid))

        # create dchousing_project/subsidy files from source
        with open(source_csv, encoding='utf-8') as f, \
                open(source_proj, mode='w', encoding='utf-8') as proj, \
                open(source_subsidy, mode='w', encoding='utf-8') as subsidy:

            reader = csv.DictReader(f)
            proj_writer = csv.DictWriter(proj, fieldnames=PROJ_FIELDS)
            proj_writer.writeheader()
            subsidy_writer = csv.DictWriter(subsidy, fieldnames=SUBSIDY_FIELDS)
            subsidy_writer.writeheader()

            for line in reader:
                nlihc_id, in_proj_table = self._get_nlihc_id_from_db(
                    db_conn=db_conn, address_id=line['ADDRESS_ID'])

                if not in_proj_table:
                    data = self._map_data_for_row(nlihc_id=nlihc_id,
                                                  fields=PROJ_FIELDS,
                                                  fields_map=project_fields_map,
                                                  line=line)
                    proj_writer.writerow(data)

                data = self._map_data_for_row(nlihc_id=nlihc_id,
                                              fields=SUBSIDY_FIELDS,
                                              fields_map=subsidy_fields_map,
                                              line=line)
                subsidy_writer.writerow(data)

        # remove source file so it doesn't get added to manifest hence database
        os.remove(source_csv)

class BaseApiManager(object):

    classname = "base"

    def __init__(self, config_file):
        self.config = self.get_config(config_file)

    def get_config(self, config_file):
        config = HousingInsightsConfig(config_file)
        return config.get_section(self.__class__.classname)

