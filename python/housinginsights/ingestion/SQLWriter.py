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
import logging
import os
import sys
sys.path.append("../../")
from housinginsights.tools import dbtools
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
from psycopg2 import DataError
import copy
import datetime

class TableWritingError(Exception):
    pass

class HISql(object):
    def __init__(self, meta, manifest_row, engine, filename=None):

        self.meta = meta
        self.manifest_row = manifest_row
        self.engine = engine

        #extract some values for convenience
        self.unique_data_id = self.manifest_row["unique_data_id"]
        self.tablename = self.manifest_row["destination_table"]
        self.metafields = meta[self.tablename]['fields']

        #assign defaults
        self.filename = 'temp_{}.psv'.format(manifest_row['unique_data_id']) if filename == None else filename

        #convert fields dictionary to lists
        self.sql_fields = []
        self.sql_field_types = []
        for field in self.metafields:
            self.sql_fields.append(field['sql_name'])
            self.sql_field_types.append(field['type'])
        self.sql_fields.append('unique_data_id')
        self.sql_field_types.append('text')


    def write_file_to_sql(self):
        #TODO let this use existing session/connection/engine instead?
        #engine = dbtools.get_database_engine("local_database")
        
        conn = self.engine.connect()
        trans = conn.begin()
        try:
            print("  opening {}".format(self.filename))
            with open(self.filename, 'r') as f:
                #copy_from is only available on the psycopg2 object, we need to dig in to get it
                dbapi_conn = conn.connection
                dbapi_cur = dbapi_conn.cursor()

                dbapi_cur.copy_from(f, self.tablename, sep='|', null='Null', columns=None)
                
                self.update_manifest_row(conn=conn, status="loaded")

                #used for debugging, keep commented in real usage
                #raise ProgrammingError(statement="test", params="test", orig="test")
                
                dbapi_conn.commit()
            trans.commit()
            logging.info("  data file loaded into database")
        
        #TODO need to find out what types of expected errors might actually occur here  
        #For now, assume that SQLAlchemy will raise a programmingerror
        except (ProgrammingError, DataError) as e:
            trans.rollback()
            
            logging.warning("  FAIL: something went wrong loading {}".format(self.unique_data_id))
            logging.warning("  exception: {}".format(e))
            raise TableWritingError

        conn.close()

    def update_manifest_row(self, conn, status="unknown"):
        '''
        Adds self.manifest_row associated with this table to the SQL manifest
        conn = the connection to use (won't be closed so calling function can rollback)
        status = the value to put in the "status" field
        '''
        #Add the status
        manifest_row = copy.copy(self.manifest_row)
        manifest_row['status'] = status
        manifest_row['load_date'] = datetime.datetime.now().isoformat()

        #Remove the row if it exists
        #TODO make sure data is synced or appended properly
        sql_manifest_row = self.get_sql_manifest_row(db_conn=conn,close_conn=False)
        if sql_manifest_row != None:
            logging.info("  deleting existing manifest row for {}".format(self.unique_data_id))
            delete_command = "DELETE FROM manifest WHERE unique_data_id = '{}'".format(self.unique_data_id)
            conn.execute(delete_command)
        
        columns = []
        values = []
        for key in manifest_row:
            columns.append(key)
            values.append(manifest_row[key])

        columns_string = "(" + ",".join(columns) + ")"
        values_string = "('" + "','".join(values) + "')"
                
        insert_command = "INSERT INTO manifest {} VALUES {};".format(columns_string,values_string)
        #print(insert_command)
        conn.execute(insert_command)

    def create_table(self, table=None):
        '''
        Creates the table associated with this data file if it doesn't already exist
        table = string representing the tablename
        '''
        #TODO - a better long-term solution to this might be SQLAlchemy metadata: http://www.mapfish.org/doc/tutorials/sqlalchemy.html
        
        db_conn = self.engine.connect()
        table = self.tablename if table==None else table

        try:
            db_conn.execute("SELECT * FROM {}".format(table))
            logging.info("  Did not create table because it already exists")
        except ProgrammingError:
            field_statements = []
            for idx, field in enumerate(self.sql_fields):
                field_statements.append(field + " " + self.sql_field_types[idx])
            field_command = ",".join(field_statements)
            create_command = "CREATE TABLE {}({});".format(table, field_command)
            db_conn.execute(create_command)
            logging.info("  Table created: {}".format(table))

        db_conn.close()

    def drop_table(self, table=None):
        
        db_conn = self.engine.connect()
        table = self.tablename if table==None else table

        #TODO also need to delete manifest row(s)
        #TODO need to use a transaction to ensure both operations sync
        try:
            db_conn.execute("DROP TABLE {}".format(table))
        except ProgrammingError:
            logging.warning("  {} table can't be dropped because it doesn't exist".format(self.tablename))
        db_conn.close()

    def get_sql_manifest_row(self, db_conn=None, close_conn=True):
        sql_query = "SELECT * FROM manifest WHERE unique_data_id = '{}'".format(self.unique_data_id)

        if db_conn == None:
            db_conn = self.engine.connect()
        
        query_result = db_conn.execute(sql_query)

        # convert the sqlAlchemy ResultProxy object into a list of dictionaries
        results = [dict(row.items()) for row in query_result]
        if close_conn == True:
            db_conn.close()

        # We expect there to be exactly one row matching the query if the csv_row is already in the database
        if len(results) > 1:
            raise ValueError('Found multiple rows in database for data id {}'.format(self.unique_data_id))

        # Return just the dictionary of results, not the list of dictionaries
        if len(results) == 1:
            return results[0]

        if len(results) == 0:
            return None

