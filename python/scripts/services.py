"""
services.py module is a scripting module used for user and server to
interface with ingestion_mediator and respective colleague modules used for
our ingestion workflow.
"""

import os
import sys
import argparse

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))
SCRIPTS_PATH = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))
sys.path.append(PYTHON_PATH)

from housinginsights.tools.logger import HILogger
from housinginsights.tools.mailer import HIMailer
# TODO: move logger configuration and management into IngestionMediator
loggers = [HILogger(name=__file__, logfile="services.log", level=10),
           HILogger(name=__file__, logfile="sources.log", level=10),
           HILogger(name=__file__, logfile="ingestion.log", level=10)
           ]
logger = loggers[0]


from housinginsights.tools.ingestion_mediator import IngestionMediator
from housinginsights.ingestion.LoadData import LoadData
from housinginsights.ingestion.Meta import Meta
from housinginsights.ingestion.Manifest import Manifest
from housinginsights.ingestion.SQLWriter import HISql
from housinginsights.ingestion.GetApiData import GetApiData

###############################
# Instantiate global colleague objects needed for ingestion scripting
###############################
_load_data = LoadData()
# currently safe to assume path for manifest will be unchanged
_manifest = Manifest(os.path.abspath(os.path.join(SCRIPTS_PATH,
                                                  'manifest.csv')))
_meta = Meta()
_hisql = HISql()
_get_api_api = GetApiData()
_mediator = None


def configure_ingestion_mediator(database_choice=None,
                                 debug=False):
    # initialize instance of ingestion mediator
    _mediator = IngestionMediator(database_choice=database_choice,
                                  debug=debug)

    # connect ingestion mediator instance to its colleague instances
    _mediator.set_load_data(_load_data)
    _mediator.set_manifest(_manifest)
    _mediator.set_meta(_meta)
    _mediator.set_hi_sql(_hisql)
    _mediator.set_get_api_data(_get_api_api)

    # connect colleague instances to this ingestion mediator instance
    _load_data.set_ingestion_mediator(_mediator)
    _manifest.set_ingestion_mediator(_mediator)
    _meta.set_ingestion_mediator(_mediator)
    _hisql.set_ingestion_mediator(_mediator)
    _get_api_api.set_ingestion_mediator(_mediator)


def weekly_update(database_choice=None, drop_tables_first=False):
    if _mediator is None:
        configure_ingestion_mediator(database_choice)

    return _load_data.reload_all_from_manifest(use_clean=False,
                                               drop_tables=drop_tables_first,
                                               load_dependents=True)


def load_db_with_raw_data(unique_data_id_list, download_api_data=False,
                          load_dependents=False, database_choice=None):
    if _mediator is None:
        configure_ingestion_mediator(database_choice)

    return _load_data.load_raw_data(unique_data_id_list=unique_data_id_list,
                                    download_api_data=download_api_data,
                                    load_dependents=load_dependents)


def load_db_with_cleaned_data(unique_data_id_list, use_raw_if_missing=True,
                              database_choice=None):
    if _mediator is None:
        configure_ingestion_mediator(database_choice)

    return _load_data.load_cleaned_data(unique_data_id_list=unique_data_id_list,
                                        use_raw_if_missing=use_raw_if_missing)


def load_db_from_manifest(use_clean=True, use_raw_if_missing=True,
                          drop_tables=False, download_api_data=False,
                          load_dependents=False, database_choice=None):
    if _mediator is None:
        configure_ingestion_mediator(database_choice)

    return _load_data.reload_all_from_manifest(
        use_clean=use_clean, use_raw_if_missing=use_raw_if_missing,
        drop_tables=drop_tables, download_api_data=download_api_data,
        load_dependents=load_dependents)


def recalculate(database_choice=None):
    if _mediator is None:
        configure_ingestion_mediator(database_choice)

    _load_data.recalculate_database()


def send_log_file_to_admin(debug=True):
    """
    At conclusion of process, send log file by email to admin and delete or
    archive from server.

    Currently very much a WIP demo, with some things partially implemented
    """


    #TODO!!! make this count all 3 files
    level_counts = _get_log_level_counts(loggers[2].logfile)

    error_count = level_counts.get('ERROR', 0)
    email = HIMailer(debug_mode=debug)
    # email.recipients.append('neal@nhumphrey.com')
    email.subject = "get_api_data logs, completed with {} errors".format(error_count)
    email.message = "See attached for the logs from the weekly_update(). Log counts by level are as follows: {}".format(level_counts)

    #add attachments - TODO not working!
    attachments = []
    for l in loggers:
        attachments.append(l.logfile)

    #TODO the HIMailer can properly attach one file but if attaching more than one they come through corrupted.
    email.attachments = [loggers[2].logfile]
    email.send_email()


    # This line is throwing a file busy error. TODO we should archive these log files instead of deleting.
    # os.unlink(logger.logfile)


def _get_log_level_counts(logfile):
    with open(logfile) as log:
        logdata = log.readlines()
        level_counts = {}
        for record in logdata:
            level = record.split(' ')[0]
            if level_counts.get(level):
                level_counts[level] += 1
            else:
                level_counts[level] = 1
    return level_counts


def main(args):
    """
    Passes command line arguments and options to respective service methods and
    initializes ingestion module class accordingly.
    """
    # for case of more than one database choice default to the option with
    # the lowest risk if database is updated
    if args.database == 'local':
        database_choice = 'local_database'

    elif args.database == 'docker_local':
        database_choice = 'docker_with_local_python'

    elif args.database == 'codefordc':
        database_choice = 'codefordc_remote_admin'

    # docker is default
    else:
        database_choice = 'docker_database'

    # initialize the ingestion mediator class accordingly
    configure_ingestion_mediator(database_choice=database_choice,
                                 debug=args.debug)

    # run requested method along with optional args
    if args.service == 'weekly_update':
        weekly_update(database_choice=database_choice,
                      drop_tables_first=args.drop_tables)

    if args.service == 'load_from_raw':
        load_db_with_raw_data(unique_data_id_list=args.uid,
                              download_api_data=args.get_api_data,
                              load_dependents=args.load_dependents,
                              database_choice=database_choice)

    if args.service == 'load_from_clean':
        load_db_with_cleaned_data(unique_data_id_list=args.uid,
                                  use_raw_if_missing=args.use_raw_if_missing,
                                  database_choice=database_choice)

    if args.service == 'load_from_manifest':
        use_clean = not args.use_raw
        load_db_from_manifest(use_clean=use_clean,
                              use_raw_if_missing=args.use_raw_if_missing,
                              drop_tables=args.drop_tables,
                              download_api_data=args.get_api_data,
                              load_dependents=args.load_dependents,
                              database_choice=database_choice)

    if args.service == 'send_log_file':
        send_log_file_to_admin(debug=args.debug)

    # handle args related to recalculating zone_facts table
    if args.service == 'recalculate_only' or not args.skip_calculations:
        recalculate(database_choice=database_choice)


if __name__ == '__main__':
    description = ('Scripting module for interfacing with ingestion mediator '
                   'for getting raw data from api and loading into db and '
                   'and other additional tools.')
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("database", help='which database the data should be '
                                         'loaded to',
                        choices=['docker', 'docker_local', 'local',
                                 'codefordc'], default='docker')
    parser.add_argument("service", help='which service method to run',
                        choices=['weekly_update', 'load_from_raw',
                                 'load_from_clean', 'load_from_manifest',
                                 'send_log_file', 'recalculate_only'],
                        default='load_from_clean')
    parser.add_argument('--uid', nargs='+',
                        help='unique data ids that should be loaded into db')
    parser.add_argument('--use-raw-if-missing', help='use clean psv but if '
                                                     'missing use raw data to '
                                                     'update db',
                        action='store_true', default=False)
    parser.add_argument('--get-api-data',
                        help='make an api request for new data if '
                             'data_method = api',
                        action='store_true', default=False)
    parser.add_argument('--load-dependents',
                        help='determine whether to automatically process '
                             'dependent data ids next',
                        action='store_true', default=False)
    parser.add_argument('--use-raw',
                        help='for load_from_manifest, flag that determines '
                             'whether to load from clean psv file or use '
                             'raw data file',
                        action='store_true', default=False)
    parser.add_argument('--drop-tables', nargs='+',
                        help='drops tables before running the load data code. '
                             ' Add the name of each table to drop in format '
                             '"table1 table2" If you want to drop all tables,'
                             ' use the keyword "all"')
    parser.add_argument('--debug', action='store_true', default=False,
                        help="raise exceptions as they occur")
    parser.add_argument('--skip-calculations', action='store_true',
                        default=False,
                        help="don't do any calculations")
    parser.add_argument('-s', '--sample', help='load with sample data',
                        action='store_true')

    main(parser.parse_args())
