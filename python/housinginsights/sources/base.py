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
import logging

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

        logging.debug("Url requested: {}".format(url))
        logging.debug("params: {}".format(params))
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

            # NOTE - only needed if using data downloaded from api call
            # instead of batch csv download
            # clean opendata 'GIS_DTTM' formatting - convert milliseconds
            # if value == 'GIS_LAST_MOD_DTTM':
            #     milli_sec = int(line[value])
            #     data[field] = \
            #         datetime.fromtimestamp(milli_sec / 1000.0).strftime(
            #             '%m/%d/%Y')
        return data

    def _get_nlihc_id_from_db(self, db_conn, mar_id):
        """
        Returns a tuple nlihc_id, in_proj_table_flag pair for a given address
        id by performing a lookup on the project table in the database using
        the mar_id column.

        If there doesn't map to an existing building in the table,
        a randomly generated uuid is returned as nlihc_id.
        """
        result = None
        if mar_id != None:
            query = "select nlihc_id from project where mar_id = " \
                    "'{}';".format(mar_id)
            query_result = db_conn.execute(query)
            result = [dict(x) for x in query_result.fetchall()]

        if result:
            return result[0]['nlihc_id'], True
        else:
            return str(uuid4()), False

    def _check_mar_for_address(self,addr, conn):
        '''
        Looks for a matching address in the MAR
        Currently just uses a 
        '''

        #Used to perform common string replacements in addresses. 
        #The key is original, value is what we want it to become
        #values match format typically found in the mar table
        #Allows first-pass matching of address strings to the MAR
            # (failed matches are then bumped up to more robust methods)
        self.address_string_mapping = {
            "Northeast":"NE",
            "Northwest":"NW",
            "Southeast":"SE",
            "Southwest":"SW",
            "St ":"Street ",
            "St. ":"Street ",
            "Pl ":"Place ",
            "Pl. ":"Place ",
            "Ave ":"Avenue ",
            "Ave. ":"Avenue "
        }

        # Format addr by matching the conventions of the MAR
        for key, value in self.address_string_mapping.items():
            addr = addr.replace(key,value)

        query = """
                select mar_id from mar
                where full_address ='{}'
                """.format(addr.upper()) #MAR uses upper case in the full_address field
                
        query_result = conn.execute(query)

        result = [dict(x) for x in query_result.fetchall()]

        if result:
            return result[0]['mar_id']

        #If no match found:
        return None

    def create_project_subsidy_csv(self, uid, project_fields_map,
                                   subsidy_fields_map, database_choice=None):
        """
        Writes 'new_proj_data_file' and 'new_subsidy_data_file' raw files
        from the source csv file. It then deletes the source file so it
        doesn't get added to manifest and loaded into the database.
        """
        if database_choice is None:
            database_choice = 'docker_database'
        engine = dbtools.get_database_engine(database_choice)
        db_conn = engine.connect()

        # create file path objects
        source_csv = self.output_paths[uid]
        folder = os.path.dirname(source_csv)
        new_proj_data_file = os.path.join(folder, "{}_project.csv".format(uid))
        new_subsidy_data_file = os.path.join(folder, "{}_subsidy.csv".format(uid))

        # create dchousing_project/subsidy files from source
        with open(source_csv, encoding='utf-8') as f, \
                open(new_proj_data_file, mode='w', encoding='utf-8') as proj, \
                open(new_subsidy_data_file, mode='w', encoding='utf-8') as subsidy:

            source_csv_reader = csv.DictReader(f)
            proj_writer = csv.DictWriter(proj, fieldnames=PROJ_FIELDS)
            proj_writer.writeheader()
            subsidy_writer = csv.DictWriter(subsidy, fieldnames=SUBSIDY_FIELDS)
            subsidy_writer.writeheader()

            # If the project doesn't exists in the database, we want to add a
            # new record to the project table.
            #
            # All projects need a new record added to the subsidy table. If that
            # project already exists in the database, link it to the project
            # using the nlihc_id; if not, link it to the record that was added
            # to the proj_writer output file."
            for source_row in source_csv_reader:

                #First, perform data-source appropriate transformations to the data
                if uid == 'dhcd_dfd_properties':
                    addr = source_row['address__street_1']
                    
                    #The DHCD data often has multiple addresses separated by semicolon
                    #  for now, let's search only for the first one
                    try:
                        first_semi = addr.index(';')
                        addr = addr[0:first_semi]
                    except ValueError:
                        addr = addr

                    #Assign these updated values to the dictionary
                    source_row['address_single'] = addr
                    source_row['mar_id'] = self._check_mar_for_address(addr=addr, conn=db_conn)
                    

                #Try to find the project in the database
                col_options = {'dchousing':'ADDRESS_ID','dhcd_dfd_properties':"mar_id"}
                addr_col = col_options[uid]

                nlihc_id, in_proj_table = self._get_nlihc_id_from_db(
                            db_conn=db_conn, 
                            mar_id=source_row[addr_col])
                
                #for debugging
                if uid == 'dhcd_dfd_properties':
                    print(source_row['mar_id'],source_row['address_single'],'\t',in_proj_table,nlihc_id)
                

                if not in_proj_table:
                    data = self._map_data_for_row(nlihc_id=nlihc_id,
                                                  fields=PROJ_FIELDS,
                                                  fields_map=project_fields_map,
                                                  line=source_row)
                    proj_writer.writerow(data)

                # add all to subsidy table
                data = self._map_data_for_row(nlihc_id=nlihc_id,
                                              fields=SUBSIDY_FIELDS,
                                              fields_map=subsidy_fields_map,
                                              line=source_row)
                subsidy_writer.writerow(data)


class BaseApiManager(object):

    classname = "base"

    def __init__(self, config_file):
        self.config = self.get_config(config_file)

    def get_config(self, config_file):
        config = HousingInsightsConfig(config_file)
        return config.get_section(self.__class__.classname)
