"""
Manifest module
"""
import os
from collections import Counter
from csv import DictWriter, DictReader
from sqlalchemy.exc import ProgrammingError

from housinginsights.ingestion.DataReader import HIReader
from housinginsights.tools.logger import HILogger
logger = HILogger(name=__file__, logfile="ingestion.log")

from datetime import datetime
import dateutil.parser as dateparser


class Manifest(HIReader):
    """
    Adds extra functions specific to manifest.csv. This is the class that
    should be used to read the manifest and return it row-by-row.
    """

    _include_flags_positive = ['use']
    _include_flags_negative = ['pending', 'exclude', 'superseded']

    def __init__(self, path='manifest.csv'):
        super().__init__(path)
        self.unique_ids = {}  # from the unique_id column in the manifest

        # validate the manifest
        if not self.has_unique_ids():
            raise ValueError('Manifest has duplicate unique_data_id!')

        # metadata fields for manifest.csv
        self._fields = [
                    ("status", "text"),
                    ("load_date", "timestamp"),
                    ("include_flag", "text"),
                    ("destination_table", "text"),
                    ("unique_data_id", "text"),
                    ("update_method", "text"),
                    ("data_date", "date"),
                    ("encoding", "text"),
                    ("local_folder", "text"),
                    ("s3_folder", "text"),
                    ("filepath", "text"),
                    ("dependency", "text"),
                    ("notes", "text")
                ]

    def __iter__(self):
        self._length = 0
        self._counter = Counter()
        with open(self.path, 'r', newline='') as data:
            reader = DictReader(data)
            self._keys = reader.fieldnames
            for row in reader:
                self._length += 1

                # parse the date into proper format for sql
                try:
                    _date = dateparser.parse(row['data_date'], dayfirst=False,
                                             yearfirst=False)
                    row['data_date'] = datetime.strftime(_date, '%Y-%m-%d')
                except ValueError:
                    row['data_date'] = 'Null'

                # return the row
                yield row

    def has_unique_ids(self):
        """
        Verifies that every value in the manifest column 'unique_data_id' is
        in fact unique. This makes sure that we can rely on this column to
        uniquely identify a source CSV file, and and can connect a record in
        the SQL manifest to the manifest.csv

        :return: true if passes validation; false otherwise
        """
        self.unique_ids = {}

        for row in self:
            if row['unique_data_id'] in self.unique_ids:
                return False
            else:
                #don't add flags that won't make it into the SQL database
                if row['include_flag'] in Manifest._include_flags_positive:
                    self.unique_ids[row['unique_data_id']] = 'found'
        return True

    def get_manifest_row(self, unique_data_id):
        """
        Returns the row for the given unique_data_id else 'None' if not in
        manifest.
        """
        for row in self:
            use = row['include_flag'] == 'use'
            if row['unique_data_id'] == unique_data_id and use:
                return row
        return None

    def create_list(self, folder_path):
        """
        Returns a list of potential unique_data_ids based on csv files in the
        given folder path. The assumption is that all raw data a saved as csv
        with filename that matches unique_data_id used in manifest.
        """
        unique_data_ids = list()
        files_in_folder = os.listdir(folder_path)
        for file in files_in_folder:
            file_path = os.path.join(folder_path, file)
            uid, file_ext = file.split(sep='.')
            if os.path.isfile(file_path) and file_ext == 'csv':
                unique_data_ids.append(uid)

        return unique_data_ids

    def update_manifest(self, date_stamped_folder):
        """
        Used for automatically swapping out old files for new ones in our manifest.csv
        whenever we gather new data. 

        Using the folder passed (e.g. /data/raw/apis), find the most recent subfolder
        (by sorting alphabetically). Make a list of .csv files in that folder
        and update the manifest.csv for every unique_data_id that corresponds
        to one of the .csv files. 
        """
        timestamp = os.path.basename(date_stamped_folder)
        data_date = datetime.strptime(timestamp, '%Y%m%d').strftime('%Y-%m-%d')
        file_path_base = date_stamped_folder[date_stamped_folder.find('raw'):]

        field_names = self.keys

        # get unique_data_ids for data files in recent subfolder
        uid_list = self.create_list(date_stamped_folder)
        data = list()

        # update the manifest.csv in place
        for row in self:
            row_uid = row['unique_data_id']
            if row_uid in uid_list:
                row['data_date'] = data_date
                filepath = os.path.join(file_path_base,
                                        "{}.csv".format(row_uid))
                row['filepath'] = filepath
            data.append(row)

        with open(self.path, mode='w', encoding='utf-8', newline='') as f:
            writer = DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(data)

        return self.path

    def check_or_create_sql_manifest(self):
        """
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
        """
        engine = self._ingestion_mediator.get_engine()

        if engine is None:
            print('Error - SQLalchemy engine is unassigned!!')
            raise ValueError

        try:
            with engine.connect() as db_conn:
                sql_query = "SELECT * FROM manifest"
                query_result = db_conn.execute(sql_query)
                _ = [dict(row.items()) for row in query_result]
            return True
        except ProgrammingError as _:
            try:
                # Create the query with appropriate fields and datatypes
                db_conn = engine.connect()
                field_statements = []
                for tup in self._fields:
                    field_statements.append(tup[0] + " " + tup[1])
                field_command = ",".join(field_statements)
                create_command = "CREATE TABLE manifest({});".format(
                    field_command)
                db_conn.execute(create_command)
                db_conn.close()
                logger.info("Manifest table created in the SQL database")
                return True

            except Exception as e:
                raise e
