'''
config.py
---------

This file configures application settings.
'''

class Config(object):
    """Configures the application."""

    SQLALCHEMY_DATABASE_URI = \
            'postgresql://codefordc:codefordc@postgres:5432/housinginsights_docker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
