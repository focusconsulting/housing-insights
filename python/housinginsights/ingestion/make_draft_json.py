##########################################################################
## Summary
##########################################################################

'''
Loads our flat file data into the Postgres database
'''
import logging
import json
import pandas as pandas
import sys, os

if __name__ == '__main__':
    sys.path.append(os.path.abspath('../../'))

from housinginsights.ingestion import ManifestReader


#configuration
#See /logs/example-logging.py for usage examples
logging_filename = "../../logs/ingestion.log"
logging_path = os.path.abspath("../../logs")
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())     #Pushes everything from the logger to the command line output as well.

# Function to clean column names for the sql_name JSON field. 
def sql_name_clean(name):
    for item in ["-"," ","."]:
        if item in name:
            name = name.replace(item, "_")
    return name.lower()

def pandas_to_sql_data_type(pandas_type_string):
    mapping = {
        'object':'text',
        'int64':'integer',
        'float64':'decimal',
        'datetime64':'timestamp'
    }
    try:
        sql_type = mapping[pandas_type_string]
    except KeyError:
        sql_type = 'text'
    return sql_type


def make_draft_json(filename, tablename): #use the name from constants as default



    # Reads the initial CSV and sets up the basic output structure. 
    dataframe_file = pandas.read_csv(filename, encoding='latin1')
    dataframe_iterator = dataframe_file.columns
    output = {
        tablename: {
            "cleaner": tablename + "{}".format("_cleaner"),
            "replace_table": True,
            "fields": []
        }
    }

    # The meat of the JSON data.  
    for field in dataframe_iterator:
        pandas_type =  str(dataframe_file[field].dtypes)
        sql_type = pandas_to_sql_data_type(pandas_type)

        data = {
                "type": sql_type, 
                "source_name": field, 
                "sql_name": sql_name_clean(field),
                "display_name": sql_name_clean(field),
                "display_text":""
            }
        output[tablename]["fields"].append(data)

    output_path = os.path.join(logging_path,(tablename+".json"))
    with open(output_path, "w") as results:
        json.dump(output, results, sort_keys=True, indent=4)

    print(tablename + " JSON table file created.")



def make_all_json(manifest_path):

    completed_tables = {}
    manifest = ManifestReader(path=manifest_path)
    if manifest.has_unique_ids():
        for manifest_row in manifest:
            tablename = manifest_row['destination_table']
            if tablename not in completed_tables:
                if manifest_row['include_flag'] == 'use':
                    filepath = os.path.abspath(
                            os.path.join(manifest_row['local_folder'],
                                        manifest_row['filepath']
                                        ))
                    make_draft_json(filepath, tablename)
                    completed_tables[tablename] = filepath
                    print("completed {}".format(tablename))
            else:
                print("skipping {}, already loaded".format(manifest_row['unique_data_id']))

    print("Finished! Used these files to generate json:")
    print(completed_tables)

if __name__ == '__main__':

    if 'single' in sys.argv:
        #Edit this filepaths before running
        csv_filename = os.path.abspath("C:/Users/humph/Documents/Github/housing-insights/data/raw/zillow/Neighborhood_ZriPerSqft_AllHomes.csv")
        table_name = "zillow_zrisqft_neighbor"
        make_draft_json(csv_filename, table_name)
    if 'multi' in sys.argv:
        manifest_path = os.path.abspath('../../scripts/manifest.csv')
        make_all_json(manifest_path)


