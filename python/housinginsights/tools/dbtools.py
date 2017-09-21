##########################################################################
# Summary
##########################################################################
'''
tools for connecting to the database, which can be used in all of the project folders
'''

##########################################################################
# Imports & Configuration
##########################################################################
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table
from sqlalchemy.orm import sessionmaker
from subprocess import check_output
import csv
import json
import os
import time
#import docker

secrets_filepath = os.path.join(os.path.dirname(__file__), '../secrets.json')


##########################################################################
# Functions
##########################################################################
def get_connect_str(database_choice):
    """
    Loads the secrets json file to retrieve the connection string
    """
    with open(secrets_filepath) as fh:
        secrets = json.load(fh)
    return secrets[database_choice]['connect_str']


def get_database_connection(database_choice):
    '''
    Deprecated - it is better to use get_database_engine 
    and then use engine.connect() within your code so that
    closing the connection is more safely handled. 
    '''

    # Connect to the database
    connection_string = get_connect_str(database_choice)
    engine = create_engine(connection_string)
    database_connection = engine.connect()
    return database_connection

def get_database_engine(database_choice):
    '''
    engines are the way to connect to the database. 

    To use, follow this pattern:

    engine = get_database_engine('docker_database')
    conn = engine.connect()
    conn.execute('SELECT * from manifest')
    conn.close()
    '''
    
    # Connect to the database
    connection_string = get_connect_str(database_choice)
    try:
        engine = create_engine(connection_string)

        #test out the engine to make sure it is valid
        conn = engine.connect()
        conn.close()

    except Exception as e:
        print(e)
        print("Error - are you trying to use the wrong Docker connect string?")
        time.sleep(5)
        raise e

    return engine
    
def get_database_session(database_choice):
    # Connect to the database
    connection_string = get_connect_str(database_choice)
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_psycopg2_cursor(database_choice):
    connection_string = get_connect_str(database_choice)
    engine = create_engine(connection_string)
    cursor = engine.raw_connection().cursor()
    return cursor
