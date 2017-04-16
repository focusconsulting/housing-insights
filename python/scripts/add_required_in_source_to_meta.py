import json

original_json = 'old_meta.json'
new_json = 'meta.json'

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
            field['required_in_source'] = False
        contents['fields'].append(new_field)

    with open(new_json, 'w') as new:
        json.dump(data, new, sort_keys=True)

if __name__ == '__main__':
    main()
