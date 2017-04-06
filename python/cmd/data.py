"""
Data.py provides command line convenience access to the modules in the housinginsights.sources
directory. Here is a brief explanation.

BRIEF EXPLANATION
-----------------

Use this script to download a csv file from an API. Specify the output file with the -o flag.
Specify whatever parameters you need with --params in key:value;k2:val2 format. For example,
if the find_location method requires a location, you would specify that location with:
    --params "location: some street somewhere in dc".

Example usage:

bin/data.sh -o ~/csvfile --params "location:641 S St NW" mar find_location


DETAILED EXPLANATION:
--------------------
data.py expects the user to supplies at least 4
things when it is run:
1. Output Type [--outtype]
2. Output File (optional) [--output, -o]
3. Api Module name
4. Api Method name

It then tries to import housinginsights.sources + whatever module you specified.
For example if the api module name supplied by the user is "mar", then it tries to import
"housinginsights.sources.mar". It then looks for a class with the module name + "ApiConn"
as a suffix. In this case it would be "MarApiConn". It then calls whatever method the user specied
from that ApiConn class. Whatever parameters specified by the user with the --params argument
are split and passed as keyword arguments (**kwargs) to the function.
The --outtype argument is added as output_type, and --o or --output is added as output_file.
Thus, each public function compatible with data.sh needs to have as a minimum those two parameters
(output_type and output_file). See the mar.py file for an example.
"""

from argparse import ArgumentParser
import importlib

from housinginsights.config.base import HousingInsightsConfig

API_MODULE = 'housinginsights.sources'

def main():
    description = "Get csv data from api(s)."
    output_help = "Path and filename of a csv file where you'd like to write the output. \
                   Required if outtype=csv, omit if outtype=stdout"
    outtype_help = "Where the output should be written. Options: 'stdout', 'csv'"
    params_help = "Keyword variables that passed directly to the api method; \
                   check the method for required parameters. Parameters are given in \
                   semicolon separated key:value;key2:value2 format."
    parser = ArgumentParser(description=description)
    parser.add_argument("--config", "-c", help="Path to the configuration file. \
                                                [Not implemented YET!]")
    parser.add_argument("--output", "-o", help=output_help)
    parser.add_argument("--outtype", "-t", default="stdout", help=outtype_help)
    parser.add_argument("--params", help=params_help)
    parser.add_argument("api", help="The name of the api module located in housinginsights.source.")
    parser.add_argument("method", help="Method of the api to call.")
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
