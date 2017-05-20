"""
CSVWriter.py contains the CSVWriter class that is used to create a clean.psv
file that can later be used to load to the database.
"""

from csv import DictWriter
import os
import copy

logging_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            os.pardir, os.pardir, "logs"))


class CSVWriter(object):
    """
    Takes a row of data, plus the meta data about it, and creates a clean.csv
    file locally that can be later be bulk-uploaded to the database.
    """

    def __init__(self, meta, manifest_row, filename=None):
        """""
        :param meta: the parsed json from the meta data containing the format
        expected of each SQL table.
        :param manifest_row: a dictionary from manifest.csv for the source file
        currently being acted on.
        :param filename: optional, filename of where to write the data.
        The default is current directory temp_{tablename}.csv
        """

        self.manifest_row = manifest_row
        self.tablename = manifest_row['destination_table']
        self.unique_data_id = manifest_row['unique_data_id']
        self.meta = meta
        self.fields = meta[self.tablename]['fields']

        # DictWriter needs a list of fields, in order, with the same key as
        # the row dict sql_fields could be used in the header row. Currently
        # not using because psycopg2 doesn't like it.
        self.csv_fields = []
        self.sql_fields = []
        for field in self.fields:
            self.csv_fields.append(field['source_name'])
            self.sql_fields.append(field['sql_name'])

        # We always want to append this to every table. write() should also
        # append this to provided data
        self.dictwriter_fields = copy.copy(self.csv_fields)

        # By default, creates a temp csv file wherever the calling module was
        #  located
        self.filename = 'temp_{}.psv'.format(self.unique_data_id) if filename == None else filename
        
        # remove any existing copy of the file so we are starting clean
        self.remove_file()

        #Using psycopg2 copy_from does not like having headers in the file. Commenting out
            #self.file = open(self.filename, 'w', newline='')
            #headerwriter = DictWriter(self.file, fieldnames = self.sql_fields, delimiter="|")
            #headerwriter.writeheader()
            #self.file.close()
            #print("header written")

        self.file = open(self.filename, 'a', newline='', encoding='utf-8')
        self.writer = DictWriter(self.file, fieldnames=self.dictwriter_fields, delimiter="|")

    def write(self, row):
        """
        Writes the given row into the clean pipe-delimited file that will be
        loaded into the database.

        :param row: the given data row
        :return: None
        """
        row['unique_data_id'] = self.manifest_row['unique_data_id']
        # Note to developers - if this row returns a key error due to an
        # optional column, it means you need to have your cleaner add a 'null'
        # value for that optional column.
        self.writer.writerow(row)

    def open(self):
        """
        Opens the file for writing. Normally called by init, but can be called
        again by the user if they want to re-open the file for writing
        """

    def close(self):
        """
        Since we can't use a with statement in the object, it's the caller's
        responsibility to manually close the file when they are done writing
        """
        self.file.close()

    # TODO should this be part of the __del__
    def remove_file(self):
        try:
            os.remove(self.filename)
        except OSError:
            pass
