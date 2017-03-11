'''
After the print(" Ready to load") statement in the main() function of load_data.py, we want to send the data stored in the newly-created clean.csv file to the database. Then, we want to update/add the appropriate row of the Postgres 'manifest' table to reflect the status of that file in the database.

Things the object will need passed to it:
    'manifest_row',
    'meta' (memory version of meta.json)
    'csv_filename' (the path to the clean.csv file created by Cleaner)
    'overwrite' (a boolean indicating whether preexisting entries of the manifest_row['unique_data_id'] should be deleted if they exist)
'''

'''
We start with a manifest row dictionary. Each row represents a CSV. Multiple rows may correspond to one SQL table.

1. Taking a clean csv file path from the manifest dictionary - DataSql

2. Database connection is passed through load_data.py.

3. Check JSON meta file for how the fields should be updated in the database - insert & update vs. dropping and overwriting? - DataSql

4. Creating a SQL table if it doesn't exist - DataSql and ManifestSql

5. Write rows - DataSql (and ManifestSql?)

share db connection
share create table if doesn't exist

DATASQL
    need to know data load type
    going to do batch update

THINK ABOUT - Has table schema changed? Column names, number of columns, column data types

    if we have ten rows and five already exist, does database know how to update or is that on us?



are we overriding or appending?
    if overriding - prep and write
    if update - need to define unique key for each row in each table - maybe something for DataReader class? JSON file?



'''

import os
import pandas as pd
import sys
sys.path.append("../../")
from housinginsights.tools import dbtools
from sqlalchemy.orm import sessionmaker


class HISql(object):
    def __init__(self):
        pass

class DataSql(HISql):
    def __init__(self, meta, manifest_row, db_conn, filename=None):

        self.meta = meta
        self.manifest_row = manifest_row
        self.db_conn = db_conn

        #extract some values for convenience
        self.unique_data_id = self.manifest_row["unique_data_id"]
        self.tablename = self.manifest_row["destination_table"]
        self.fields = meta[self.tablename]['fields']

        #assign defaults
        self.filename = 'temp_{}.psv'.format(self.tablename) if filename == None else filename

        #convert fields dictionary to lists
        self.sql_fields = []
        for field in self.fields:
            self.sql_fields.append(field['sql_name'])

    def read_and_write_to_sql(self, engine=None, cursor=None):
        if engine != None:
            csv_df = pd.read_csv(self.filename, delimiter="|")
            csv_df['unique_data_id'] = self.unique_data_id
            csv_df.to_sql(self.tablename, engine, if_exists='append')
        if cursor != None:
            print("using cursor!")
            print(cursor)
            with open(self.filename, 'r') as f:
                cursor.copy_from(f, self.tablename, sep='|', null='Null', columns=None)

        else:
            engine = dbtools.get_database_engine("local_database")
            ses = sessionmaker(bind=engine)

            with open(self.filename, 'r') as f:
                fake_conn = engine.raw_connection()
                fake_cur = fake_conn.cursor()
                fake_cur.copy_from(f, self.tablename, sep='|', null='Null', columns=None)
                fake_conn.commit()

                print("tried to commit changes")


    def create_table(self):
        #TODO use a better way to not drop if no table
        self.db_conn.execute("DROP TABLE {}".format(self.tablename))

        field_commands = []
        for field in self.fields:
            field_commands.append(field['sql_name'] + " " + field['type'])
        field_command = ",".join(field_commands)
        create_command = "CREATE TABLE {}({});".format(self.tablename, field_command)
        self.db_conn.execute(create_command)

    # check to see if table exists in database - look up how to iterate through sqlalchemy database when connected - stackoverflow

    # if table doesn't exist, create the table:
    # open json file
    # for each field, create a column with the appropriate type, use the correct sql_name for the header - look up best way to do this.

    # read json and determine how to update database table if necessary. we need to look at specific example for this. way to update rows based on existing criteria?

    # if not done, batch update all rows using COPY FROM postgres command. As far as we know, COPY FROM appends new rows to the table. What's the best way to selectively insert and update? Dropping all old rows using unique key?



# class ManifestSql(HISql):
# 	def __init__(self, path):

# 	def get_row(self, unique_data_id):
