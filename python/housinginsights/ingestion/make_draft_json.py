"""
Module creates draft JSON file(s) from given csv data sources that after user
review will be inserted into the meta.json

You can think of meta.json as the skeleton template for the data in tables
loaded into the database.
"""

import logging
import json
import sys
import os
from optparse import OptionParser

import pandas as pandas

python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir, os.pardir))
sys.path.append(python_filepath)


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
    cleaned up before inserted into meta.json

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


def checkTable(table_name, meta):
    """
    Check whether the new table is in meta.json file

    :param: table_name - the new data to be added
    :param type: string

    :param: meta - path to the meta.json file (currently called meta.json)
    :param type: string

    :return: boolean value
    : True - table_name found in meta.json
    : False - table_name NOT found
    """
    if not(os.path.isfile(meta)):
        raise ValueError("Unable to access JSON file")

    # read the data from current json file
    with open(meta, "r") as json_file:
        current_data = json_file.read()

    # decode the json file, result is a "dict", cast the result as a "set"
    current_tables = json.loads(current_data)

    return table_name in current_tables.keys()


def appendJSON(new_json, master_json):
    """
    Copy the file content of new_json and append to the file content in meta_json

    :param:  new_json - path to the new json file
    :param type: string

    :param:  master_json - path to the meta.json file
    :param type: string

    :return: void
    """
    #TODO: version control of meta.json, create backup making changes to master JSON
    if not(os.path.isfile(new_json) and os.path.isfile(master_json)):
        raise ValueError("Path to one of the JSON files is invalid")

    # Update the master JSON file
    with open(new_json, "r") as new_file:
        json_data = new_file.read()
    new_data = json.loads(json_data)

    # read the current master JSON table
    with open(master_json, "r") as json_file:
        master_data = json_file.read()
    masterJ_data = json.loads(master_data)

    # add the new table to the master JSON
    masterJ_data.update(new_data)
    # write the new JSON list to the master JSON file
    json.dump(masterJ_data, open(master_json, 'w'), indent=2)
    print("%s appended to meta.json file" % new_json)


def duplicateTable(new_table, new_json, master_json):
    """
    Ask the user for decision on table that is found in the meta.json file.
    The user can decide to either overwrite current master json or cancel copying.

    :param:  new_table - new table being added
    :param type: string

    :param:  new_json - path to the new json file
    :param type: string

    :param:  master_json - path to the meta.json file
    :param type: string

    :return: void
    """
    if not(os.path.isfile(new_json) and os.path.isfile(master_json)):
        raise ValueError("Path to one of the JSON files is invalid")

    time_out = 0

    while time_out < 10:
        usr_decide = input("\nPress: [O] to overwrite current value in meta.json; [C] to cancel: ")

        if ('O' in usr_decide or 'o' in usr_decide):
            # Overwrite current table in master json
            # remove the entry meta.json
            with open(master_json, "r") as json_file:
                master_data = json_file.read()
            masterJ_data = json.loads(master_data)

            masterJ_data.pop(new_table, 0)	# 0 as fail-safe parameter
            json.dump(masterJ_data, open(master_json, 'w'), indent=2)

            appendJSON(new_json, master_json)
            return

        elif ('C' in usr_decide or 'c' in usr_decide):
            # cancel copying
            print("Copying new JSON cancelled")
            return

        else:
            print("Option not recognised\n")

        time_out += 1

    # incorrect selection exceeds limit
    print("Copying JSON aborted")


if __name__ == '__main__':
    #
    # Edit these values before running!
    csv_filename = os.path.abspath("../../../data/raw/preservation_catalog/20170315/Parcel.csv")#"../../../data/sample
    # /project_sample.csv"
    table_name = "parcel"
    encoding = "latin1" #Try utf-8 or latin1. Put the successful value into
    # manifest.csv
    #print('main(): {}, {}, {}'.format())
    # import ipdb; ipdb.set_trace()
    #Make the table
    if 'create' in sys.argv:
        make_draft_json(csv_filename, table_name, encoding)

    if 'add' in sys.argv:
        new_json_path = os.path.join(logging_path, (table_name+".json"))
        json_filepath = python_filepath + "/scripts/meta.json"

        try:
            if checkTable(table_name, json_filepath):
                # the new table is already in table_info.json
                print("table already in master json")
                duplicateTable(table_name, new_json_path, json_filepath)

            else:
                # the new table will be appended
                print("adding new table")
                appendJSON(new_json_path, json_filepath)

        except ValueError:
            print("Path to meta.json is invalid")
