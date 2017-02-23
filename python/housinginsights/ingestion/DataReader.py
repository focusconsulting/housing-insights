from collections import Counter
from csv import DictReader
import csv
from os import path
import os

import logging
from urllib.request import urlretrieve

#DataReader edits (FYI for Walt):
# -Renamed DataReader to HIReader (housing insights reader); extended 2 versions of it (ManifestReader and DataReader)

#TODOs
#-convert relative path to full path when passed as argument

class HIReader(object):
    """
    Container object that will call read in csvs and marshal them to a Postgres Database.
    """
    def __init__(self, path):
        self.path = path
        self._length = None
        self._keys = None

    def __iter__(self):
        self._length = 0
        self._counter = Counter()
        with open(self.path, 'rU') as data:
            reader = DictReader(data)
            self._keys = reader.fieldnames
            for row in reader:
                self._length += 1
                yield row

    def __len__(self):
        if self._length is None:
            for row in self:
                # Read data for length and counter
                continue
        return self._length

    @property
    def items(self):
        return self.counter.keys()

    @property
    def keys(self):
        _it = iter(self)
        next(_it)
        return self._keys

    def reset(self):
        """
        In case it breaks in the middle of reading the file
        :return:
        """
        self._length = None


class ManifestReader(HIReader):
    '''
    Adds extra functions that make sure the manifest.csv works as expected
    '''

    _include_flags_positive = ['use']
    _include_flags_negative = ['pending', 'exclude', 'superseded']

    def __init__(self, path='manifest.csv'):
        super().__init__(path)
        self.unique_ids = {}            #from the unique_id column in the manifest

    #Completed, test created
    def has_unique_ids(self):
        '''
        Makes sure that every value in the manifest column 'unique_data_id' is in fact unique. 
        This makes sure that we can rely on this column to uniquely identify a source CSV file,
        and and can connect a record in the SQL manifest to the manifest.csv
        '''
        self.unique_ids = {}

        for row in self:
            if row['unique_data_id'] in self.unique_ids:
                return False
            else:
                #don't add flags that won't make it into the SQL database
                if row['include_flag'] in ManifestReader._include_flags_positive:
                    self.unique_ids[row['unique_data_id']] = 'found'
        return True



class DataReader(HIReader):
    def __init__(self, manifest_row):
        self.path = os.path.join(path.dirname(__file__), manifest_row['local_folder'], manifest_row['filepath'])

        self.manifest_row = manifest_row      #a dictionary from the manifest
        self.s3_path = manifest_row['s3_folder'] + manifest_row['filepath']
        self.destination_table = manifest_row['destination_table']

        #self.download_data_file()

        super().__init__(self.path)


    def download_data_file(self):
        '''
        Checks to see if the file already exists locally, if not downloads it
       '''
        try:
            with open(self.path) as f:
                myreader=csv.reader(f,delimiter=',')
                headers = next(myreader)
        except FileNotFoundError as e:
            logging.info("  file not found. attempting to download file to disk: " + s3_path)
            urlretrieve(s3_path,local_path)
            logging.info("  download complete.")
            with open(local_path) as f:
                myreader=csv.reader(f,delimiter=',')
                headers = next(myreader)
        return headers #not strictly necessary but useful for testing

    def should_file_be_loaded(self, sql_manifest_row):
        '''
        compares manifest from the csv to manifest in the database
        '''
        if self.manifest_row['include_flag'] == 'use':
            if sql_manifest_row == None:
                return True
            if sql_manifest_row['include_flag'] != 'loaded':
                return True
            if sql_manifest_row['include_flag'] == 'loaded':
                logging.info("{} is already in the database, skipping".format(self.manifest_row['unique_data_id'])) 
                return False
        else:
            logging.info("{} include_flag is {}, skipping".format(self.manifest_row['unique_data_id'], self.manifest_row['include_flag'])) 
            return False

    def do_fields_match(self, meta):
        '''
        meta = the full meta.json nested dictionary 
        Checks that the csv headers match the expected values
        '''

        try:
            field_list = meta[self.destination_table]['fields']
        except KeyError:
            logging.info('  table "{}" not found in meta data'.format(self.destination_table))
            return False

        included = {}

        #Initialize values - start out assuming all is OK until we identify problems. 
        return_value = True                     
        not_found = []

        #Check that all of the data columns are in the meta.json
        for field in self.keys:
            if not any(d.get('source_name', None) == field for d in field_list):
                not_found.append('"{}" in CSV not found in meta'.format(field))
                return_value = False

        #Check that all the meta.json columns are in the data
        for field in field_list:
            if field['source_name'] not in self.keys:
                not_found.append('  "{}" in meta.json not found in data'.format(field['source_name']))
                return_value = False
        
        #Log our errors if any
        if return_value == False:
            logging.warning("  do_fields_match: {}. '{}' had missing items:\n{}".format(return_value, self.destination_table, not_found))
        else:
            logging.info("  do_fields_match: {}. \n    meta.json and csv field lists match completely for '{}'".format(return_value, self.destination_table))
        
        return return_value

