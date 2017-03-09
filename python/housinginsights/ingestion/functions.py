import logging
import json


# Completed, tests not written.
def load_meta_data(filename='meta.json'):
    """
    Expected meta data format:
        { tablename: {fields:[
            {   "display_name": "Preservation Catalog ID",
                "display_text": "description of what this field is",
                "source_name": "Nlihc_id",
                "sql_name": "nlihc_id",
                "type": "object"
            }
            ]}
        }
    """
    with open(filename) as fh:
        meta = json.load(fh)

    json_is_valid = True
    try:
        for table in meta:
            for field in meta[table]['fields']:
                for key in field:
                    if key not in ('display_name', 'display_text', 'source_name', 'sql_name', 'type'):
                        json_is_valid = False
                        first_json_error = "Location: table: {}, section: {}, attribute: {}".format(table, field, key)
                        raise ValueError("Error found in JSON, check expected format. {}".format(first_json_error))
    except:
        raise ValueError("Error found in JSON, check expected format.")

    logging.info("{} imported. JSON format is valid: {}".format(filename, json_is_valid))

    return meta
