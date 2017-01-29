##########################################################################
## Summary
##########################################################################

'''
Loads our flat file data into the Postgres database
'''
import logging
import json
import pandas as pandas
import sys

#configuration
#See /logs/example-logging.py for usage examples
logging_filename = "../../logs/ingestion.log"
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
    dataframe_file = pandas.read_csv(filename)
    dataframe_iterator = dataframe_file.columns
    output = {
        tablename: {
            "fields": []
        }
    }

    # The meat of the JSON data.  
    for field in dataframe_iterator:
        data = {
            field: {
                "type": str(dataframe_file[field].dtypes), 
                "source_name": field, 
                "sql_name": sql_name_clean(field),
                "display_name": sql_name_clean(field),
                "display_text":""
            }
        }
        output[tablename]["fields"].append(data)

    with open(tablename + ".json", "w") as results:
        json.dump(output, results, sort_keys=True, indent=4)

    print(tablename + " JSON table file created.")

if __name__ == '__main__':
    if len(sys.argv[1:])!= 2:
         print("Add a filename and/or tablename")
    else:
        csv_filename = sys.argv[1]
        table_name = sys.argv[2]
        make_draft_json(csv_filename, table_name)

    
