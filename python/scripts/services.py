import os, sys
python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir))
sys.path.append(python_filepath)

import argparse 

from housinginsights.tools.logger import HILogger
import get_api_data
import load_data
from housinginsights.tools.mailer import HIMailer

loggers = [ HILogger(name=__file__, logfile="services.log", level=10),
            HILogger(name=__file__, logfile="sources.log", level=10),
            HILogger(name=__file__, logfile="ingestion.log", level=10)
            ]
logger = loggers[0]

def run_get_api_data(debug=False):
    # TODO Figure out which parameters should be passed for this to run as a service.
    try:
        get_api_data.get_multiple_api_sources(db='docker_database')
    except Exception as e:
        logger.error("get_api_data failed with error: %s", e)
        if debug:
            raise e
    finally:
        get_api_data.send_log_file_to_admin(debug=debug)

def send_log_file_to_admin(debug=True):
    """
    At conclusion of process, send log file by email to admin and delete or archive from server.


    Currently very much a WIP demo, with some things partially implemented

    """


    #TODO!!! make this count all 3 files
    level_counts = get_log_level_counts(loggers[2].logfile)

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


def get_log_level_counts(logfile):
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



def weekly_update(db_choice, drop_tables_first = False):
    #TODO should update the secrets.json keys to make them simpler so that this mapping is irrelevant

    send_log = True
    debug = True


    #Run the jobs
    try:
        if drop_tables_first:
            remove_table_flag = '--remove-tables'
            tables_to_remove = 'all'
        else:
            remove_table_flag = ''
            tables_to_remove = ''

        #Get and load data in order so that we appropriately deal with duplicate records

        #Start with MAR so that we can geocode things
        arguments = get_api_data.parser.parse_args([db_choice,'--modules','opendata','--ids','mar'])
        get_api_data.get_multiple_api_sources(arguments)
        arguments = load_data.parser.parse_args([db_choice,'--update-only','mar', '--skip-calculations' , remove_table_flag, tables_to_remove])
        load_data.main(arguments)


        #prescat
        arguments = get_api_data.parser.parse_args([db_choice,'--modules','prescat'])
        get_api_data.get_multiple_api_sources(arguments)
        arguments = load_data.parser.parse_args([db_choice,'--update-only','prescat_project',
                                                                            'prescat_subsidy',
                                                                            'prescat_addre',
                                                                            'prescat_reac',
                                                                            'prescat_real_property',
                                                                            'prescat_parcel',

                                                                            '--skip-calculations' ])
        load_data.main(arguments)


        #then DHCD since it has better data when duplicate entries appear in DCHousing
        arguments = get_api_data.parser.parse_args([db_choice,'--modules','dhcd'])
        get_api_data.get_multiple_api_sources(arguments)
        arguments = load_data.parser.parse_args([db_choice,'--update-only','dhcd_dfd_properties_project',
                                                                        'dhcd_dfd_properties_subsidy',
                                                                        'dhcd_dfd_properties_addre',
                                                                        '--skip-calculations' ])
        load_data.main(arguments)


        #Then DCHousing
        arguments = get_api_data.parser.parse_args([db_choice,'--modules','DCHousing'])
        get_api_data.get_multiple_api_sources(arguments)
        arguments = load_data.parser.parse_args([db_choice,'--update-only','dchousing_project',
                                                                        'dchousing_subsidy',
                                                                        'dchousing_addre',
                                                                        '--skip-calculations'])
        load_data.main(arguments)


        #Then everything else
        #TODO it's a little bit clunky to do it this way but to do "everything else" we'd need to modify load_data to accept a negative list
        arguments = get_api_data.parser.parse_args([db_choice,'--modules',
                                'opendata',
                                #TODO temporarily skipped because it's slow: 'wmata_distcalc',
                                'census'])

        get_api_data.get_multiple_api_sources(arguments)
        arguments = load_data.parser.parse_args([db_choice,'--update-only',
                            'tract2010_ward2012',
                            'tract2010_cluster2000',
                            'tax',
                            #'hmda_all_dc',
                            'topa_rcasd_2017',
                            'topa_rcasd_2016',
                            'topa_rcasd_2015',
                            'building_permits_2016',
                            'building_permits_2017',
                            'crime_2016','crime_2017',
                            'acs5_2015',
                            'wmata_stops',
                            'wmata_dist'
                            ])
        load_data.main(arguments)


        
    except Exception as e:
        logger.error("Weekly update failed with error: %s", e)
        if debug:
            raise e

    finally:
        if send_log:
            send_log_file_to_admin(debug=debug)
    


if __name__ == '__main__':
    services_parser = argparse.ArgumentParser("Services.py for running the weekly update job")  
    services_parser.add_argument("database", help="""which database we should connect to 
                    when using existing data as part of the download process""",
                    choices=['docker', 'docker_local', 'local', 'codefordc'])

    services_parser.add_argument('--drop-all', help="drop all tables before starting the update", 
            action='store_true')



    services_arguments = services_parser.parse_args()

    weekly_update(services_arguments.database, services_arguments.drop_all)