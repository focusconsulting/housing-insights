"""
Meta.py is an object representation of the meta.json file used to document
all metadata fields for our raw data mapping them to their respective fields
used in the the database.
"""
# built-in imports
import os
import sys
import json

# app imports
from python.housinginsights.tools.base_colleague import Colleague
from python.housinginsights.tools.logger import HILogger
from python.housinginsights.ingestion import Cleaners

# relative package import for when running as a script
PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir, os.pardir))
# sys.path.append(PYTHON_PATH)
SCRIPTS_PATH = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))

logger = HILogger(name=__file__, logfile="ingestion.log")


class Meta(Colleague):

    def __init__(self, meta_path=None):
        super().__init__()
        if meta_path is None:
            self._meta_path = os.path.abspath(os.path.join(SCRIPTS_PATH,
                                                           'meta.json'))
        else:
            self._meta_path = meta_path

        self._meta = self._validate_and_load_into_memory()

    def _validate_and_load_into_memory(self):
        """
        Helper function validates the format of the JSON data in meta.json and
        returns the validated JSON data of meta.json file
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
        with open(self._meta_path) as fh:
            meta = json.load(fh)

        # validate that meta.json meets the expected data format
        json_is_valid = True
        try:
            for table in meta:
                for field in meta[table]['fields']:
                    for key in field:
                        if key not in (
                        'display_name', 'display_text', 'source_name',
                        'sql_name', 'type', 'required_in_source', '_comment'):
                            json_is_valid = False
                            first_json_error = "Location: " \
                                               "table: {}, section: {}, " \
                                               "attribute: {}".format(table,
                                                                      field,
                                                                      key)
                            raise ValueError("Error found in JSON, "
                                             "check expected format. "
                                             "{}".format(first_json_error))
        except Exception:
            raise ValueError("Error found in JSON, check expected format.")

        logger.info(
            "{} imported. JSON format is valid: {}".format(self._meta_path,
                                                           json_is_valid))
        return meta

    def get_meta(self):
        return self._meta

    def get_cleaner_from_name(self, manifest_row, engine=None):
        """
        Returns the instance of the cleaner class matching the given cleaner class
        name.

        :param manifest_row: the given row in manifest.csv
        :param engine: the engine object used for interacting with db
        :return: a class object of the given cleaner class
        """

        # Import
        # module = import_module("module.submodule")
        table_name = manifest_row['destination_table']
        cleaner_class_name = self._meta[table_name]['cleaner']
        Class_ = getattr(Cleaners, cleaner_class_name)
        instance = Class_(self._meta, manifest_row, engine=engine)
        return instance

    def get_sql_fields_and_type_from_meta(self, table_name=None):
        """
        Get list of 'sql_name' and 'type' from fields for database updating

        :param table_name: the name of the table to be referenced in meta
        :return: a tuple - 'sql_name, sql_name_type'
        """

        if table_name is None:
            raise ValueError(
                'Invalid table_name: {} was passed'.format(table_name))

        meta_fields = self._meta[table_name]['fields']

        sql_fields = list()
        sql_field_types = list()

        for field in meta_fields:
            sql_fields.append(field['sql_name'])
            sql_field_types.append(field['type'])

        return sql_fields, sql_field_types

    def get_meta_only_fields(self, table_name, data_fields):
        """
        Returns fields that exist in meta.json but not CSV so we can add
        them to the row as it is cleaned and written to PSV file.

        :param table_name: the table name for the data being processed
        :param data_fields: the fields for the data being processed
        :return: additional fields as dict
        """
        meta_only_fields = {}
        for field in self._meta[table_name]['fields']:
            if field['source_name'] not in data_fields:
                # adds 'sql_name',None as key,value pairs in dict
                meta_only_fields[field['sql_name']] = None
        return meta_only_fields
