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
    # Connect to the database
    connection_string = get_connect_str(database_choice)
    engine = create_engine(connection_string)
    database_connection = engine.connect()
    return database_connection

def get_database_engine(database_choice):
    # Connect to the database
    connection_string = get_connect_str(database_choice)
    engine = create_engine(connection_string)
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
