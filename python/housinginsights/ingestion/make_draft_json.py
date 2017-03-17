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

#configuration
#See /logs/example-logging.py for usage examples
logging_filename = "../../logs/ingestion.log"
logging_path = os.path.abspath("../../logs")
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())     #Pushes everything from the logger to the command line output as well.

def make_draft_json(filename, tablename): #use the name from constants as default

    # Function to clean column names for the sql_name JSON field. 
    def sql_name_clean(name):
        for item in ["-"," ","."]:
            if item in name:
                name = name.replace(item, "_")
        return name.lower()

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
        data = {
                "type": str(dataframe_file[field].dtypes), 
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

if __name__ == '__main__':

    csv_filename = os.path.abspath("C:/Users/humph/Documents/Github/housing-insights/data/raw/zillow/Neighborhood_ZriPerSqft_AllHomes.csv")
    table_name = "zillow_zrisqft_neighbor"
    make_draft_json(csv_filename, table_name)


