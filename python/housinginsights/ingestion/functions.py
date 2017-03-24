import logging
import json
from sqlalchemy.exc import ProgrammingError
import sys, os

from importlib import import_module
sys.path.append(os.path.abspath('../../'))

import housinginsights.ingestion.Cleaners as Cleaners

# Completed, tests not written.
def load_meta_data(filename='meta.json'):
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

    json_is_valid = True
    try:
        for table in meta:
            for field in meta[table]['fields']:
                for key in field:
                    if key not in ('display_name', 'display_text', 'source_name', 'sql_name', 'type'):
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
                ("data_date","date"),
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


def get_cleaner_from_name(meta, manifest_row, name = "GenericCleaner"):

    #Import
    #module = import_module("module.submodule")
    Class_ = getattr(Cleaners, name)
    instance = Class_(meta, manifest_row)
    return instance


def join_paths(pieces=[]):
    '''
    Joins arbitrary pieces of a url or path. 
    Alternative to os.path.join if the second argument might start with "/"
    '''
    return '/'.join(s.strip('/') for s in pieces)

#Used for testing purposes
if __name__ == '__main__':
    pass
    instance = get_cleaner_from_name("GenericCleaner")
    print(type(instance))