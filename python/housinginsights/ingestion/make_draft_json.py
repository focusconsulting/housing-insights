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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir, os.pardir)))

from housinginsights.ingestion.DataReader import ManifestReader


#configuration
#See /logs/example-logging.py for usage examples
# TODO: replace hard code rel paths so this doesn't fail if called from outside
# TODO: the folder for this file
logging_filename = "../../logs/ingestion.log"
logging_path = os.path.abspath("../../logs")
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
        manifest_path = os.path.abspath('../../scripts/manifest.csv')
        make_all_json(manifest_path)
