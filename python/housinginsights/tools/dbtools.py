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

def check_for_docker_database():
    # TODO this needs to be updated, was just a quick and dirty way to check if postgres is running locally in a docker container.
    running = False
    client = docker.from_env()
    containers = client.containers.list(filters={'status': 'running'})
    for container in containers:
        if 'postgres' in container.attrs['Args']:
            running = True
            break
    return running


def start_local_database_server():
    client = docker.from_env()
    client.containers.run('postgres:9.4.5', detach=True, ports={'5432/tcp': 5432})
    conn = get_database_connection('postgres_database')
    conn.execute("commit")
    conn.execute("create database housinginsights_local")
    conn.close()

