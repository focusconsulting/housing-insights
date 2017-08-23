import os, sys
python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir))
sys.path.append(python_filepath)
from housinginsights.tools.logger import HILogger
import get_api_data

logger = HILogger(name=__file__, logfile="sources.log", level=10)


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


def run_load_data():
    pass


def run_scripts(debug=False):
    run_get_api_data(debug=debug)
    run_load_data()


if __name__ == '__main__':
    run_scripts(debug=True)
