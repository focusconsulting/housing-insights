from argparse import ArgumentParser
import importlib

from housinginsights.config.base import HousingInsightsConfig

API_MODULE = 'housinginsights.sources'

def main():
    description = "Get csv data from api(s)."
    parser = ArgumentParser(description=description)
    parser.add_argument("--config", "-c", help="Path to the configuration file.")
    parser.add_argument("--output", "-o", help="Output file.")
    parser.add_argument("--outtype", "-t", default="stdout", help="Type of output")
    parser.add_argument("--params", help="Input parameters in semicolon \
                                            separated key=value;key2=value2 format")
    parser.add_argument("api", help="Name of the api module.")
    parser.add_argument("method", help="Method of the api to call")
    ns = parser.parse_args()
    result = call_module(ns)

def call_module(ns):
    try:
        kwargs = parse_params(ns.params)
        kwargs['output_type'] = ns.outtype
        kwargs['output_file'] = ns.output
        # Hack. for now to have sensible defaults...
        if ns.output:
            kwargs['output_type'] = 'csv'
        apimod = API_MODULE + '.' + ns.api
        classname = ns.api[0].upper() + ns.api[1:] + 'ApiConn'
        module = importlib.import_module(apimod)
        api_class = getattr(module, classname)
        api = api_class()
        apifunc = getattr(api, ns.method)
        result = apifunc(**kwargs)
    except Exception as e:
        print('Your request failed. {0}'.format(e))

def parse_params(params):
    kwargs = {}
    if not params:
        return kwargs
    for kv in params.split(';'):
        key, value = kv.split(':')
        kwargs[key] = value
    return kwargs

if __name__ == '__main__':
    main()
