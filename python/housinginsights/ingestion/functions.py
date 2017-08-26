"""
Module contains helper functions used in loading data into database
"""

import logging
import json
from sqlalchemy.exc import ProgrammingError
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir, os.pardir)))

import housinginsights.ingestion.Cleaners as Cleaners


# Completed, tests not written.
def load_meta_data(filename='meta.json'):
    """
    Helper function validates the format of the JSON data in meta.json.

    :param filename: meta.json filepath
    :return: the validated JSON data of meta.json file
    """
    """
    Expected meta data format:
        { tablename: {fields:[
            {   "display_name": "Preservation Catalog ID",
                "display_text": "description of what this field is",
                "source_name": "Nlihc_id",
                "sql_name": "nlihc_id",
                "type": "object"
            }
            ]}
        }
    """
    with open(filename) as fh:
        meta = json.load(fh)

    # validate that meta.json meets the expected data format
    json_is_valid = True
    try:
        for table in meta:
            for field in meta[table]['fields']:
                for key in field:
                    if key not in ('display_name', 'display_text', 'source_name', 'sql_name', 'type', 'required_in_source', '_comment'):
                        json_is_valid = False
                        first_json_error = "Location: table: {}, section: {}, attribute: {}".format(table, field, key)
                        raise ValueError("Error found in JSON, check expected format. {}".format(first_json_error))
    except:
        raise ValueError("Error found in JSON, check expected format.")

    logging.info("{} imported. JSON format is valid: {}".format(filename, json_is_valid))

    return meta


def check_or_create_sql_manifest(engine, rebuild=False):
    '''
    Makes sure we have a manifest table in the database. 
    If not, it creates it with appropriate fields. 

    This corresponds to the manifest.csv file, which contains a log
    of all the individual data files we have used as well as which
    table they each go into. 

    The csv version of the manifest includes all files we have ever
    used, including ones not in the database. 

    The SQL version of the manifest only tracks those that have been
    written to the database, and whether they are still there or 
    have been deleted.

    engine = the SQLalchemy engine to get to the database
    rebuild = Boolean as to whether to drop the table first. 
    '''
    try:
        db_conn = engine.connect()
        sql_query = "SELECT * FROM manifest"
        query_result = db_conn.execute(sql_query)
        results = [dict(row.items()) for row in query_result]
        db_conn.close()
        return True
    except ProgrammingError as e:
        try:
            #Create the query with appropriate fields and datatypes
            db_conn = engine.connect()
            fields = [
                ("status","text"),
                ("load_date", "timestamp"),
                ("include_flag","text"),
                ("destination_table","text"),
                ("unique_data_id","text"),
                ("update_method", "text"),
                ("data_date","date"),
                ("encoding", "text"),
                ("local_folder","text"),
                ("s3_folder","text"),
                ("filepath","text"),
                ("notes","text")
                ]
            field_statements = []
            for tup in fields:
                field_statements.append(tup[0] + " " + tup[1])
            field_command = ",".join(field_statements)
            create_command = "CREATE TABLE manifest({});".format(field_command)
            db_conn.execute(create_command)
            db_conn.close()
            logging.info("Manifest table created in the SQL database")
            return True

        except Exception as e:
            raise e


def get_cleaner_from_name(meta, manifest_row, name="GenericCleaner", engine=None):
    """
    Returns the instance of the cleaner class matching the given cleaner class
    name.

    :param meta: in memory JSON object representing meta.json
    :param manifest_row: the given row in manifest.csv
    :param name: the referenced cleaner class in meta.json for the table as str
    :return: a class object of the given cleaner class
    """

    #Import
    #module = import_module("module.submodule")
    Class_ = getattr(Cleaners, name)
    instance = Class_(meta, manifest_row, engine=engine)
    return instance


def join_paths(pieces=[]):
    '''
    Joins arbitrary pieces of a url or path. 
    Alternative to os.path.join if the second argument might start with "/"
    '''
    return '/'.join(s.strip('/') for s in pieces)


def get_unique_addresses_from_str(address_str=""):

    def _trim_str(add_str):
        """Helper function that does some simple string cleaning."""
        add_str = add_str.lstrip()
        add_str = add_str.rstrip()
        return add_str

    def _parse_semicolon_delimiter(address_list):
        """Helper function that handles parsing semicolon delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep=';')
            if len(temp_results) > 1:
                for address in temp_results:
                    output.append(_trim_str(address))
            else:
                output.append(add_str)
        return output

    def _parse_and_delimiter(address_list):
        """Helper function that handles parsing 'and' delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep='and')
            if len(temp_results) > 1:
                for address in temp_results:
                    output.append(_trim_str(address))
            else:
                output.append(add_str)
        return output

    def _parse_ampersand_delimiter(address_list):
        """Helper function that handles parsing '&' delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep='&')
            if len(temp_results) > 1:
                num_1 = _trim_str(temp_results[0])
                base = _trim_str(temp_results[1])
                num_2, base = base.split(' ', 1)
                num_2 = _trim_str(num_2)
                base = _trim_str(base)

                output.append('{} {}'.format(num_1, base))
                output.append('{} {}'.format(num_2, base))
            else:
                output.append(add_str)
        return output

    def _parse_dash_delimiter(address_list):
        """Helper function that handles parsing '-' delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep='-')
            if len(temp_results) > 1:
                num_1 = _trim_str(temp_results[0])
                base = _trim_str(temp_results[1])
                num_2, base = base.split(' ', 1)
                num_2 = _trim_str(num_2)
                base = _trim_str(base)

                # check whether odd, even, or ambiguous range
                even = True if int(num_1) % 2 == 0 else False

                if (int(num_2) % 2 == 0 and not even) or (
                            int(num_2) % 2 != 0 and even):
                    even = None

                # populate address number ranges
                step = 1 if even is None else 2
                for num in range(int(num_1), int(num_2) + 1, step):
                    output.append('{} {}'.format(num, base))
            else:
                output.append(add_str)
        return output

    result = [address_str]  # tracks unique addresses from address_str

    # 1: parse complete address delimiters - ';', 'and'
    result = _parse_semicolon_delimiter(result)
    result = _parse_and_delimiter(result)

    # 2: parse address number range delimiters  - '&', '-'
    result = _parse_ampersand_delimiter(result)
    result = _parse_dash_delimiter(result)

    return result

#Used for testing purposes
if __name__ == '__main__':

    from housinginsights.tools import dbtools
    meta_path = os.path.abspath('../../scripts/meta.json')


    meta = load_meta_data(meta_path)
    engine = dbtools.get_database_engine('docker_database')
    meta_json_to_database(engine=engine, meta=meta)