from collections import Counter
from csv import DictReader
import csv
from os import path
import os

import logging

from urllib.request import urlretrieve
from urllib.request import urlopen
import codecs

from datetime import datetime
import dateutil.parser as dateparser

#DataReader edits (FYI for Walt):
# -Renamed DataReader to HIReader (housing insights reader); extended 2 versions of it (ManifestReader and DataReader)

#TODOs
#-convert relative path to full path when passed as argument

class HIReader(object):
    """
    Container object that will reads in CSVs and provides them row-by-row through the __iter__ method. 
    Each object is associated with one specific file through the file path. 
    File can be local (path_type="file") or remote (path_type="s3"). Note, local files are preferred
    when possible for faster processing time and lower bandwidth usage. 
    """
    def __init__(self, path, path_type="file"):
        self.path = path
        self._length = None
        self._keys = None
        self.path_type = path_type

    def __iter__(self):
        self._length = 0
        self._counter = Counter()

        if self.path_type == "file":
            with open(self.path, 'r', newline='', encoding='latin-1') as data:
                reader = DictReader(data)
                self._keys = reader.fieldnames
                for row in reader:
                    self._length += 1
                    yield row

        elif self.path_type == "url":
            ftpstream = urlopen(self.path)
            reader = DictReader(codecs.iterdecode(ftpstream, 'latin1'))
            self._keys = reader.fieldnames
            for row in reader:
                self._length += 1
                yield row

        else:
            raise ValueError("Need a path_type")

    #TODO add __next__ method for more general purpose use
    #https://www.ibm.com/developerworks/library/l-pycon/

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
    Adds extra functions specific to manifest.csv. This is the class that
    should be used to read the manifest and return it row-by-row. 
    '''

    _include_flags_positive = ['use']
    _include_flags_negative = ['pending', 'exclude', 'superseded']

    def __init__(self, path='manifest.csv'):
        super().__init__(path)
        self.unique_ids = {}            #from the unique_id column in the manifest


    def __iter__(self):
        self._length = 0
        self._counter = Counter()
        with open(self.path, 'r', newline='') as data:
            reader = DictReader(data)
            self._keys = reader.fieldnames
            for row in reader:
                self._length += 1

                #parse the date into proper format for sql 
                try:
                    _date = dateparser.parse(row['data_date'],dayfirst=False, yearfirst=False)
                    row['data_date'] = datetime.strftime(_date, '%Y-%m-%d')
                except ValueError:
                    row['data_date'] = 'Null'
                
                #return the row
                yield row

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
    '''
    Reads a specific data file. This file must be associated with a specific manifest_row, 
    which is the dictionary returned by the ManifestReader __iter__ method. 

    If load_from = "local", the file is loaded from the local file system using 
    the combo of 'local_folder' and 'filepath' from the manifest. When loading locally, 
    if the file does not exist __init__ will try to automatically download the file from S3. 

    If load_from = "s3" the file can be read directly from the web. This is available only for
    the future adaptation of this to be used on an EC2 or Lambda job; when running locally, it
    is recommended to use the "local" method and let the script download the file to disk automatically. 
    Users can also run the aws cli sync command before using this tool to get the data. 
    '''
    def __init__(self, meta, manifest_row, load_from="local"):
        self.meta = meta

        self.manifest_row = manifest_row      #a dictionary from the manifest
        self.destination_table = manifest_row['destination_table']

        self.load_from=load_from
        self.s3_path = os.path.join(manifest_row['s3_folder'], manifest_row['filepath'].strip("\/")).replace("\\","/")
        if load_from=="s3":
            self.path = self.s3_path
            self.path_type = "url"
        else: #load from file
            self.path = os.path.join(path.dirname(__file__), manifest_row['local_folder'], manifest_row['filepath'].strip("\/"))
            self.path_type = "file"

            if self.manifest_row['include_flag'] == 'use':
                self.download_data_file()

        self.not_found = [] #Used to log missing fields compared to meta data

        super().__init__(self.path, self.path_type)

    def download_data_file(self):
        '''
        Checks to see if the file already exists locally, if not downloads it
       '''
        try:
            with open(self.path, 'r', newline='') as f:
                myreader=csv.reader(f,delimiter=',')
                headers = next(myreader)
        except FileNotFoundError as e:
            logging.info("  file not found. attempting to download file to disk: " + self.s3_path)
            urlretrieve(self.s3_path, self.path)
            logging.info("  download complete.")
            with open(self.path, 'r', newline='') as f:
                myreader=csv.reader(f,delimiter=',')
                headers = next(myreader)
        return headers #not strictly necessary but useful for testing

    def should_file_be_loaded(self, sql_manifest_row):
        '''
        Runs all the checks that the file is OK to use
        '''
        if self.do_fields_match() == False:
            return False
        if self.check_include_flag(sql_manifest_row) == False:
            return False
        return True


    def check_include_flag(self, sql_manifest_row):
        '''
        compares manifest from the csv to manifest in the database. 
        If the manifest says the file should be used ("use") AND the file is not
        already loaded into the database (as indicated by the matching sql_manifest_row), the file
        will be added. 

        The sql object in charge of getting the sql_manifest_row and writing
        new sql_manifest_row elements to the database is in charge of making sure
        that the sql_manifest_row['status'] field can be trusted as a true representation of 
        what is in the database currently. 
        '''
        if self.manifest_row['include_flag'] == 'use':
            if sql_manifest_row == None:
                return True
            if sql_manifest_row['status'] != 'loaded':
                return True
            if sql_manifest_row['status'] == 'loaded':
                logging.info("  {} is already in the database, skipping".format(self.manifest_row['unique_data_id']))
                return False
        else:
            logging.info("  {} include_flag is {}, skipping".format(self.manifest_row['unique_data_id'], self.manifest_row['include_flag']))
            return False

    def do_fields_match(self):
        '''
        Checks that the csv headers match the expected values
        '''

        try:
            field_list = self.meta[self.destination_table]['fields']
        except KeyError:
            logging.info('  table "{}" not found in meta data'.format(self.destination_table))
            return False

        included = {}

        #Initialize values - start out assuming all is OK until we identify problems.
        return_value = True
        self.not_found = []

        #Check that all of the data columns are in the meta.json
        for field in self.keys:
            if not any(d.get('source_name', None) == field for d in field_list):
                self.not_found.append('"{}" in CSV not found in meta'.format(field))
                return_value = False

        #Check that all the meta.json columns are in the data
        for field in field_list:
            if field['source_name'] not in self.keys:
                self.not_found.append('  "{}" in meta.json not found in data'.format(field['source_name']))
                return_value = False

        #Log our errors if any
        if return_value == False:
            logging.warning("  do_fields_match: {}. '{}' had missing items:\n{}".format(return_value, self.destination_table, self.not_found))
        else:
            logging.info("  do_fields_match: {}. meta.json and csv field lists match completely for '{}'".format(return_value, self.destination_table))

        return return_value
