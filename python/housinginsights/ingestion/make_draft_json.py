"""
Module creates draft JSON file(s) from given csv data sources that after user
review will be inserted into the meta.json (soon to be called table_info.json)

You can think of meta.json as the skeleton template for the data in tables
loaded into the database.
"""

import logging
import json
import sys
import os

import pandas as pandas

python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir, os.pardir))
sys.path.append(python_filepath)

from housinginsights.ingestion.DataReader import ManifestReader


#configuration
#See /logs/example-logging.py for usage examples
logging_path = os.path.abspath(os.path.join(python_filepath, "logs"))
logging_filename = os.path.abspath(os.path.join(logging_path, "ingestion.log"))
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
#Pushes everything from the logger to the command line output as well
logging.getLogger().addHandler(logging.StreamHandler())


def _sql_name_clean(name):
    """
    Internal function to clean column names for the sql_name JSON field.

    :param name: column name for sql_nam JSON field
    :type name: str

    :return: cleaned up column name as lower case
    """
    # TODO: add code to make sure doesn't end or begin with underscore
    for item in ["-"," ","."]:
        if item in name:
            name = name.replace(item, "_")
    return name.lower()


def _pandas_to_sql_data_type(pandas_type_string):
    """
    An internal mapping function that returns the sql equivalent data type of a
    given pandas data type.

    :param pandas_type_string: pandas data type to look for
    :type pandas_type_string: str

    :return: sql equivalent data type
    """
    mapping = {
        'object': 'text',
        'int64': 'integer',
        'float64': 'decimal',
        'datetime64': 'timestamp'
    }
    # TODO: refactor to return key with default look up?
    try:
        sql_type = mapping[pandas_type_string]
    except KeyError:
        sql_type = 'text'
    return sql_type


def make_draft_json(filename, tablename, encoding):
    """
    Create a draft JSON file for the new table that will be reviewed and
    cleaned up before inserted into meta.json (soon to be called
    table_info.json).

    The draft output will be saved within '/housing-insights/python/logs'
    folder.

    :param filename: the filename of the csv data source
    :type filename: str

    :param tablename: the table name to be used in sql database
    :type tablename: str

    :param encoding: character encoding to pass to pandas - use 'latin1' or
    'utf-8' if that doesn't.
    :type encoding: str

    :return: None
    """

    # basic structure of the draft JSON output
    output = {
        tablename: {
            # TODO: change cleaner naming scheme to CamelCase
            "cleaner": tablename + "{}".format("_cleaner"),
            "replace_table": True,
            "fields": []
        }
    }

    # TODO: insert 'unique_data_id' field into draft JSON
    unique_data_id_field = {
        "display_name": "Unique data ID",
        "display_text": "Identifies which source file this record came from",
        "source_name": "unique_data_id",
        "sql_name": "unique_data_id",
        "type": "text",
        "required_in_source": False
    }
    output[tablename]["fields"].append(unique_data_id_field)

    # read csv file as pandas data frame and column headers
    dataframe_file = pandas.read_csv(filename, encoding=encoding)
    dataframe_iterator = dataframe_file.columns

    # Iterate through each field and populate draft JSON with attributes info.
    for field in dataframe_iterator:
        pandas_type = str(dataframe_file[field].dtypes)
        sql_type = _pandas_to_sql_data_type(pandas_type)

        field_attributes = {
                "type": sql_type, 
                "source_name": field, 
                "sql_name": _sql_name_clean(field),
                "display_name": _sql_name_clean(field),
                "display_text":"",
                "required_in_source": True
            }
        output[tablename]["fields"].append(field_attributes)

    # Write completed draft JSON as csv into the logging folder
    output_path = os.path.join(logging_path, (tablename+".json"))
    with open(output_path, "w") as results:
        json.dump(output, results, sort_keys=True, indent=2)

    # TODO: consider using logging.info to report success?
    print(tablename + " JSON table file created.")


def make_all_json(manifest_path):

    completed_tables = {}
    manifest = ManifestReader(path=manifest_path)
    if manifest.has_unique_ids():
        for manifest_row in manifest:
            tablename = manifest_row['destination_table']
            encoding = manifest_row.get('encoding')
            if tablename not in completed_tables:
                if manifest_row['include_flag'] == 'use':
                    filepath = os.path.abspath(
                            os.path.join(manifest_row['local_folder'],
                                        manifest_row['filepath']
                                        ))
                    make_draft_json(filepath, tablename, encoding)
                    completed_tables[tablename] = filepath
                    print("completed {}".format(tablename))
            else:
                print("skipping {}, already loaded".format(manifest_row['unique_data_id']))

    print("Finished! Used these files to generate json:")
    print(completed_tables)


def checkTable(table_name, table_info):
    """
    Check whether the new table is in table_info.json file

    :param: table_name - the new data to be added table_info.json
    :param type: string

    :param: table_info - path to the table_info.json file (currently called meta.json)
    :param type: string

    :return: boolean value
    : True - table_name found in table_info.json
    : False - table_name NOT found
    """
    if not(os.path.isfile(table_info)):
        raise ValueError("Path to table_info.json is invalid")

    # read the data from current json file
    with open(table_info, "r") as json_file:
        current_data = json_file.read()

    # decode the json file, result is a "dict", cast the result as a "set"
    current_tables = json.loads(current_data)
    table_set = set(current_tables.keys())

    return table_name in table_set


if __name__ == '__main__':
    # TODO: refactor to take in cmd line arguments for csv_filename, table_name,
    # TODO: and encoding

    if 'single' in sys.argv:
        # Edit these values before running!
        csv_filename = os.path.abspath("/Users/KweningJ/Documents/Computer "
                                       "Programming/housing-insights/data/raw/"
                                       "tax_assessment/opendata/20170505/"
                                       "DCHousing.csv")
        table_name = "dchousing"
        encoding = "latin1" #only used for opening w/ Pandas. Try utf-8 if latin1 doesn't work. Put the successful value into manifest.csv
        make_draft_json(csv_filename, table_name, encoding)
        
    if 'multi' in sys.argv:
        manifest_path = os.path.abspath(
            os.path.join(python_filepath, 'scripts', 'manifest.csv'))
        make_all_json(manifest_path)

    if 'single-add' in sys.argv:
        """
        An option to add a new data source to both create a table JSON file
        then check if the table has been already to the master JSON file, table_info.json

        It performs the same procedure as 'single', then performs the additional
        checks before appending the new table to table_info.json
        """
        # development case
        #json_filepath = python_filepath + "/scripts/meta.json"
        #print(os.path.isfile(json_filepath))

        #new_table = "building_permits"
        #print(checkTable(new_table, json_filepath))

        # Edit the follow parameters before running

        # Change csv_filename to the file path of the raw data file
        csv_filename = os.path.abspath("/Users/KweningJ/Documents/Computer "
                                       "Programming/housing-insights/data/raw/"
                                       "tax_assessment/opendata/20170505/"
                                       "DCHousing.csv")

        # Change table_name to the table being added
        table_name = "dchousing"
        #only used for opening w/ Pandas. Try utf-8 if latin1 doesn't work. Put the successful value into manifest.csv
        encoding = "latin1"

        make_draft_json(csv_filename, table_name, encoding)
