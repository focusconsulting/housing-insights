'''
config.py
---------

This file configures application settings.
'''
from ETL.utils import get_credentials

class TestingConfig(object):
    """Configures the application."""
    SQLALCHEMY_DATABASE_URI = get_credentials('docker_database_connect_str')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
    DEBUG = True

class ProductionConfig(object):
    """Configures the application for productions."""
    SQLALCHEMY_DATABASE_URI = get_credentials('remote_database_connect_str')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
    DEBUG = False
