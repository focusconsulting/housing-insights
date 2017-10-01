"""
Module reads and validates the data that will be used to update the database.
"""

from collections import Counter
from csv import DictReader
import csv
from os import path
import os

import sys, traceback

from http.client import HTTPConnection, HTTPSConnection, HTTPResponse, HTTPException, OK
from urllib.parse import urlparse
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError

import codecs

from datetime import datetime
import dateutil.parser as dateparser

from housinginsights.tools.base_colleague import Colleague
from housinginsights.tools.logger import HILogger
logger = HILogger(name=__file__, logfile="ingestion.log")


#DataReader edits (FYI for Walt):
# -Renamed DataReader to HIReader (housing insights reader); extended 2 versions of it (ManifestReader and DataReader)


# TODO: convert relative path to full path when passed as argument
class HIReader(Colleague):
    """
    Container object that reads in CSVs and provides them row-by-row through
    the __iter__ method. Each object is associated with one specific file
    through the file path. File can be local (path_type="file") or remote
    (path_type="s3").

    Note, local files are preferred when possible for faster processing time
    and lower bandwidth usage.
    """
    def __init__(self, path, path_type="file", encoding="latin-1", keys=None):
        super().__init__()
        self.path = path
        self._length = None
        self._keys = keys
        self.path_type = path_type
        self.encoding = encoding

    def __iter__(self):
        """Iterator wrapper for the class.

        It reads in the csv data into memory as dictionary object using the
        field names as keys.

        :return: a row from the data
        """
        self._length = 0
        self._counter = Counter()

        if self.path_type == "file":
            with open(self.path, 'r', newline='',
                      encoding=self.encoding) as data:
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

    def get_row_by_column_name(self, col_header_name, look_up_value):
        """
        Returns the row for a given value in a given column in the data file.

        :param col_header_name: a column header name in the data
        :type col_header_name: str

        :param look_up_value: the look up value to search for
        :type look_up_value: str
        :return: a dictionary representing the row that matches the search
        criteria
        """
        # make sure column name is valid
        if col_header_name not in self.keys:
            return None

        for row in self:
            if row[col_header_name] == look_up_value:
                return row
        return None


class DataReader(HIReader):
    """
    Reads a specific data file. This file must be associated with a specific
    manifest_row, which is the dictionary returned by the ManifestReader
    __iter__ method.

    If load_from = "local", the file is loaded from the local file system using
    the combo of 'local_folder' and 'filepath' from the manifest. When loading
    locally, if the file does not exist __init__ will try to automatically
    download the file from S3.

    If load_from = "s3" the file can be read directly from the web. This is
    available only for the future adaptation of this to be used on an EC2 or
    Lambda job; when running locally, it is recommended to use the "local"
    method and let the script download the file to disk automatically.

    Users can also run the aws cli sync command before using this tool to
    get the data.
    """

    def __init__(self, meta, manifest_row, load_from="local"):
        """
        Initialize the class with the specific json data to validate the data
        with, the related manifest row referencing the table and data file path,
        and the file system of choice to use for finding the data file.

        :param meta: the meta data as json data
        :type meta: json

        :param manifest_row: a row in the manifest
        :type manifest_row: dict

        :param load_from: file system where the data file resides
        :type load_from: str
        """
        self.meta = meta

        self.manifest_row = manifest_row
        self.destination_table = manifest_row['destination_table']

        # Use default encoding if none found
        if 'encoding' not in manifest_row:
            logger.warning("  Warning: encoding not found in manifest. " \
                            "Falling back to latin-1.")
        self.encoding = manifest_row.get('encoding', 'latin-1')

        self.load_from = load_from
        self.s3_path = os.path.join(manifest_row['s3_folder'],
                                    manifest_row['filepath'].strip("\/")
                                    ).replace("\\","/")
        self._error_reporting_overhead = {}
        # # Test connection to s3 URL
        # if self.manifest_row['include_flag'] == 'use':
        #     self._suppress_verbose_error_reporting()
        #     content_type_header = self._test_connection_to_URL(self.s3_path)
        #     self._restore_verbose_error_reporting()
        #     if content_type_header is not None:
        #         logger.info("  Content (MIME) type: {}".format(content_type_header))

        self._keys = None
        # Load data file from given file system - S3 or local
        if load_from == "s3":
            # Test connection to s3 URL
            if self.manifest_row['include_flag'] == 'use':
                #self._suppress_verbose_error_reporting()
                content_type_header = self._test_connection_to_URL(self.s3_path)
                #self._restore_verbose_error_reporting()
                if content_type_header is not None:
                    logger.info(
                        "  Content (MIME) type: {}".format(content_type_header))

            self.path = self.s3_path
            self.path_type = "url"
        else:
            self.path = os.path.normpath(
                            os.path.join(path.dirname(__file__),
                                         manifest_row['local_folder'],
                                         manifest_row['filepath']))
            self.path_type = "file"

            if self.manifest_row['include_flag'] == 'use':
                headers = self._download_data_file()

        self._keys = self._set_keys()

        self.not_found = [] #Used to log missing fields compared to meta data

        super().__init__(self.path, self.path_type, self.encoding, self._keys)

    def __iter__(self):
        """
        Iterator wrapper that only uses canonical header fieldname keys
        provided by _set_keys().
        (Note: These canonical keys differ from those yielded by DictReader's
               fieldnames property whenever the header row contains a BOM.)
        """
        self._length = 0
        self._counter = Counter()

        if self.path_type == "file":
            with open(self.path, 'r', newline='',
                      encoding=self.encoding) as data:
                # Always use canonical header fieldname keys:
                reader = DictReader(data, fieldnames=self._keys)
                header = next(reader)   # Omit header row from output
                for row in reader:
                    self._length += 1
                    yield row

        elif self.path_type == "url":
            with urlopen(self.path) as ftpstream:
                # Always use canonical header fieldname keys:
                reader = DictReader(codecs.iterdecode(ftpstream, self.encoding),
                                    self._keys)
                header = next(reader)   # Omit header row from output
                for row in reader:
                    self._length += 1
                    yield row

        else:
            raise ValueError("Need a path_type")

    @property
    def keys(self):
        return self._keys


    def _download_data_file(self):
        """
        Internal function that tries to load the data file from the local file
        system. If the file isn't found, it then downloads it.

        :return: data file headers
        """
        headers = None
        try:
            with open(self.path, 'r', newline='', encoding=self.encoding) as f:
                logger.info("  Defaulting to local data file: '{}'".format(self.path))
                myreader = csv.reader(f, delimiter=',')
                headers = next(myreader)
        except FileNotFoundError as e:
            self._validate_or_create_path()
            logger.info("  File not found. Attempting to download file to disk: " +
                         self.s3_path)
            try:
                urlretrieve(self.s3_path, self.path)
                file_size = 0
                if os.path.isfile(self.path):
                    file_size = int(os.stat(self.path).st_size)
                if file_size > 0:
                    logger.info("  Download complete.  " \
                                 "{} bytes downloaded.".format(file_size))
                else:
                    logger.warning("  Warning: Download cannot be verified; " \
                                    "check location: '{}'".format(self.path))
                    return
                with open(self.path, 'r', newline='', encoding=self.encoding) as f:
                    myreader = csv.reader(f,delimiter=',')
                    headers = next(myreader)
            except URLError as ue:
                logger.error("  Error: _download_data_file(): " \
                              "Error opening URL '{}' for download.".format(self.path))
                raise
            except OSError as oe:
                logger.error("  Error: _download_data_file(): " \
                              "Downloaded file '{}' cannot be opened " \
                              "for reading.".format(oe.filename))
                raise

        return headers

    def _validate_or_create_path(self):
        """
        Internal function that verifies whether a path exists on the
        local file system. If not, it recursively creates the path and all
        necessary folders.

        :return: None
        """
        root_path = os.path.abspath(os.path.dirname(self.path))
        if os.path.exists(root_path):
            return
        os.makedirs(root_path)
        return

    def _set_keys(self):
        """
        Internal function that returns the canonical header fieldname keys
        dictionary.  (Removes any byte order mark detected in the leading header
        fieldname key as read from the source file.)

        :return: header fieldname keys dictionary (with any BOM removed)
        """
        _keys = None
        if self.path_type == 'url':
            logger.info("  File will be read from remote location: '{}'".format(self.path))
            try:
                with urlopen(self.path) as ftpstream:
                    reader = DictReader(codecs.iterdecode(ftpstream, self.encoding))
                    _keys = reader.fieldnames
                    if self._contains_leading_bom(_keys[0], encoding=self.encoding):
                        logger.info("  Leading BOM (byte order mark) found in file '{}'; " \
                                     "updating header keys to omit BOM...".format(
                                        os.path.basename(self.path)))
                        _keys[0] = self._remove_leading_bom(_keys[0], self.encoding)
            except URLError as ue:
                logger.error("  Error: _set_keys(): Header fieldname keys cannot be set; " \
                              "error opening URL '{}' for reading.".format(self.path))
        else:
            try:
                with open(self.path, 'r', newline='', encoding=self.encoding) as data:
                    reader = DictReader(data)
                    _keys = reader.fieldnames
                    if self._contains_leading_bom(_keys[0], encoding=self.encoding):
                        logger.info("  Leading BOM (byte order mark) found in file '{}'; " \
                                     "updating header keys to omit BOM...".format(
                                        os.path.basename(self.path)))
                        _keys[0] = self._remove_leading_bom(_keys[0], encoding=self.encoding)
            except OSError as oe:
                logger.error("  Error: _set_keys(): Header fieldname keys cannot be set; " \
                              "file '{}' cannot be opened for reading.".format(oe.filename))
                logger.error("  Full system error message:\n\n  '{}'".format(oe.strerror))
            except ValueError as ve:
                logger.error("  Error: _set_keys(): Header fieldname keys cannot be set; " \
                              "encoding error encountered.")
        return _keys

    def should_file_be_loaded(self, sql_manifest_row):
        """
        Runs all the checks that the file is OK to use.

        :param sql_manifest_row: the given sql manifest row
        :return: True if passes validation; False otherwise.
        """

        if self._do_fields_match() and self._check_include_flag(sql_manifest_row):
            return True
        else:
            return False

    def _check_include_flag(self, sql_manifest_row):
        """
        Checks to make sure the include_flag matches requirements for loading the data

        Previously this compared the manifest_row to the sql_manifest_row; however,
        since the unique_data_id now stays constant across time this check is 
        not needed. 
        """

        if self.manifest_row['include_flag'] == 'use':
           return True

        else:
            logger.warning("Skipping data source. {} include_flag is {}".format(
                self.manifest_row['unique_data_id'],
                self.manifest_row['include_flag']))
            return False

    def _do_fields_match(self):
        """
        Returns True if the csv headers match the expected values.
        """

        # verify that table name is in meta.json
        try:
            field_list = self.meta[self.destination_table]['fields']
        except KeyError:
            logger.info('  table "{}" not found in meta data'.format(
                self.destination_table))
            return False

        self.not_found = []
        actual_exist = self._verify_actual_columns_exist_in_metadata(field_list)
        required_exist = self._verify_required_metadata_columns_exist_in_actual(
            field_list)

        # Success if both actual and required exist, else false.
        success = True if actual_exist and required_exist else False

        #Log our errors if any
        if not success:
            logger.warning("  do_fields_match: {}. '{}' had missing " \
                            "items:\n{}".format(success, self.destination_table,
                                                self.not_found))
        else:
            logger.info("  do_fields_match: {}. meta.json and csv field lists " \
                         "match completely for '{}'".format(
                            success, self.destination_table))

        return success

    def _verify_actual_columns_exist_in_metadata(self, field_list):
        """
        Returns True if all of the data columns are in meta.json.

        :param field_list: header columns to verify
        """

        success = True
        for data_file_field in self.keys:
            # does data headers match any of those in meta.json fields?
            if not any(field.get('source_name', None) == data_file_field
                       for field in field_list):
                self.not_found.append('"{}" in CSV not found in meta'.format(
                    data_file_field))
                success = False
        return success

    def _verify_required_metadata_columns_exist_in_actual(self, field_list):
        """
        Returns True if all the "required_in_source" fields in meta.json are
        also in the data file.

        :param field_list: header columns to verify
        """
        success = True
        for field in field_list:
            if (field['required_in_source']) and \
                    (field['source_name'] not in self.keys):
                self.not_found.append('  "{}" in meta.json not found in ' \
                                      'data'.format(field['source_name']))
                success = False
        return success

    def _test_connection_to_URL(self, url_str):
        """
        Internal function that tests the connection to a URL via a simple
        HTTP/1.1 HEAD request.  If a test connection cannot be established,
        raises an exception with a helpful diagnostic message (e.g. the
        HTTP Response status code & reason).

        :param url_str: full string for the URL to test a connection to
        :type url_str: str

        :return: the value of the HTTP Response 'Content-Type' header,
                 or None if no successful test connection was made
        """
        content_type_header = None
        try:
            url = urlparse(url_str)
            test_conn = None
            if url.scheme == 'https':
                test_conn = HTTPSConnection(url.netloc)
            elif url.scheme == 'http':
                test_conn = HTTPConnection(url.netloc)
            else:
                raise RuntimeError("  Error:  Cannot connect to URL '{}'\n" \
                                   "  Unsupported network protocol scheme " \
                                   "'{}' specified\n" \
                                   "  Supported schemes: http | https".format(
                                    url_str, url.scheme))
            test_conn.request('HEAD', url.path)
            response = test_conn.getresponse()
            content_type_header = response.getheader('Content-Type')
            if response.status != OK:    # i.e. "HTTP/1.1 200 OK"
                raise RuntimeError("  Error: Cannot connect to URL '{}'\n" \
                                   "  HTTP Response status code & reason: " \
                                   "{} {}".format(url_str, response.status,
                                                           response.reason))
        except ValueError as ve:    # Raised by urlparse(...)
            raise RuntimeError("  Error: Cannot connect to URL '{}'\n" \
                               "  URL string may be invalid.".format(url_str))
        except HTTPException as he: # Raised by HTTPSConnection(...)
                                    # or HTTPConnection(...)
            raise RuntimeError("  Error: Cannot connect to URL '{}'\n" \
                               "  HTTPException: {}\n" \
                               "  url.scheme : '{}'\n" \
                               "  url.netloc : '{}'\n" \
                               "  url.path   : '{}'\n".format(
                                url_str, str(he),
                                url.scheme, url.netloc, url.path))
        except OSError as oe:   # Catches any low-level socket errors
                                # raised by test_conn.request(...)
                                # -> _socket (socketmodule.c)
            raise RuntimeError("  Error: Cannot connect to URL '{}'\n" \
                               "  Socket Error: {}: {}\n" \
                               "  url.scheme : '{}'\n" \
                               "  url.netloc : '{}'\n" \
                               "  url.path   : '{}'\n".format(
                                url_str, type(oe).__name__, str(oe),
                                url.scheme, url.netloc, url.path))
        finally:
            if isinstance(test_conn, HTTPConnection):
                test_conn.close()

        return content_type_header

    def _suppress_verbose_error_reporting(self):
        """
        Internal function that enables temporary suppression of verbose error
        reporting of full stack traces accompanying exceptions.
        Instead of printing to stderr, stack traces are logged to
        the default logging instance.

        Note: This is currently used to pass along brief diagnostic feedback
              for connection/socket-level exceptions raised by
              _test_connection_to_URL(...) while omitting stack traces in
              stderr output.
        """
        # Save default exception-handling behavior:
        self._error_reporting_overhead['sys.excepthook'] = sys.excepthook
        # Temporarily set exception handling to custom exception handler that
        # logs stack traces for debugging instead of printing them to stderr:
        sys.excepthook = self._discreet_exception_handler
        # Temporarily remove any StreamHandler instances for the default logger:
        self._error_reporting_overhead['stream_handlers'] = []
        stream_handlers = (h for h in logger.getLogger().handlers \
                             if isinstance(h, logger.StreamHandler))
        for h in stream_handlers:
            self._error_reporting_overhead['stream_handlers'].append(h)
            logger.getLogger().removeHandler(h)

    def _restore_verbose_error_reporting(self):
        """
        Internal function that enables restores default error reporting that
        both prints full stack traces accompanying exceptions to stderr and
        logs them to the default logging instance.

        Note: This is intended to be called after
              _suppress_verbose_error_reporting() to restore normal error
              handling behavior.
        """
        # Restore any StreamHandler instances for the default logger:
        if len(self._error_reporting_overhead['stream_handlers']) > 0:
            stream_handlers_indices = []
            for i, h in enumerate(self._error_reporting_overhead['stream_handlers']):
                logger.getLogger().addHandler(h)
                stream_handlers_indices.append(i)
            for j in stream_handlers_indices:
                self._error_reporting_overhead['stream_handlers'].pop(j)
        # Restore default exception-handling behavior to verbose
        # (will print any stack traces to stderr again)
        sys.excepthook = self._error_reporting_overhead['sys.excepthook']

    def _discreet_exception_handler(self, exception_class, exception, tb):
        """
        Internal function that acts as a temporary exception handler.
        Prints only the handled exception to stderr while logging any
        accompanying stack traces to the default log.
        """
        logger.error("{}: {}".format(exception_class.__name__, exception))
        logger.error("Traceback (most recent call last):")
        tb_entries = traceback.extract_tb(tb)
        for tb_entry in tb_entries:
            logger.error("  File \"{}\", line {}, in {}\n" \
                          "    {}".format(tb_entry[0], tb_entry[1], tb_entry[2],
                                          tb_entry[3]))
        print("{}: {}".format(exception_class.__name__, exception),
              file=sys.stderr)

    def _contains_leading_bom(self, str, encoding='utf-8'):
        """
        Returns True if input string starts with 0xEFBBBF byte order mark
        sequence and False otherwise, testing the string according to
        an optional encoding parameter (default is 'utf-8').

        :param str: the string to evaluate
        :type str: str

        :param encoding: str encoding: 'utf-8' (default) | 'latin-1'
        :type encoding: str

        :return: True if str starts with BOM sequence, False otherwise
        """
        if (encoding == 'utf-8'):
            bom_as_hex = "efbbbf"   # hex encoding of utf-8 BOM
            str_as_hex = "".join("{:02x}".format(c) for c in str.encode())
            if str_as_hex.startswith(bom_as_hex):
                return True
        elif (encoding == 'latin-1'):
            bom_in_latin_1 = "ï»¿"  # latin-1-encoded version of BOM
            if (str.startswith(bom_in_latin_1)):
                return True
        else:
            logger.error("Unrecognized encoding: '{}'".format(encoding))
        return False

    def _remove_leading_bom(self, str, encoding='utf-8'):
        """
        Accepts an input string and optional encoding and returns the string
        with any leading byte order mark stripped off.

        :param str: the string to strip the BOM from
        :type str: str

        :param encoding: str encoding: 'utf-8' (default) | 'latin-1'
        :type encoding: str

        :return: input string with any leading BOM sequence removed
        """
        str_new = str
        if (encoding == 'utf-8'):
            bom_as_hex = "efbbbf"   # hex encoding of utf-8 BOM
            str_as_hex = "".join("{:02x}".format(c) for c in str.encode())
            if str_as_hex.startswith(bom_as_hex):
                str_as_hex = "".join(str_as_hex.split(bom_as_hex,1)[1])
                str_new = "".join("{}".format(chr(int(str_as_hex[i:i+2],16))) \
                                              for i in range(0,len(str_as_hex),2))
        elif (encoding == 'latin-1'):
            bom_in_latin_1 = "ï»¿"  # latin-1-encoded version of BOM
            if (str.startswith(bom_in_latin_1)):
                str_new = "".join(str.split(bom_in_latin_1,1)[1])
        else:
            logger.error("Unrecognized encoding: '{}'".format(encoding))
        return str_new

