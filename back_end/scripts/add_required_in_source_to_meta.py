'''
One-off script used to add the new required_in_source field to the meta.json
'''

import json

original_json = '../tests/test_data/meta_sample.json'
new_json = '../tests/test_data/meta_sample_updated.json'

#All tables should have a 'unique_data_id' in them; this value 
#is not required_in_source because it is always added by our ingestion code.
new_field = {
            "display_name": "Unique data ID",
            "display_text": "Identifies which source file this record came from",
            "source_name": "unique_data_id",
            "sql_name": "unique_data_id",
            "type": "text",
            "required_in_source": False
        }

def main():
    with open(original_json) as json_data:
      data = json.load(json_data)

    for source_name, contents in data.items():
        for field in contents['fields']:
            field['required_in_source'] = True
        contents['fields'].append(new_field)

    with open(new_json, 'w') as new:
        json.dump(data, new, sort_keys=True, indent=2)

if __name__ == '__main__':
    main()
