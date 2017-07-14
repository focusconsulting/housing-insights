


def items_divide(numerator_data, denominator_data):
    '''
    Divides items in the numerator by items in the denominator by matching
    the appropriate groupings. 

    Takes data that is formatted for output the API, i.e. a dictionary 
    with key "items", which contains a list of dictionaries each with 'grouping' 
    and 'count'
    '''
    items = []
    if numerator_data['items'] == None:
        items=None
    else:
        for n in numerator_data['items']:
            #TODO what should we do when a matching item isn't found?
            matching_d = next((item for item in denominator_data['items'] if item['group'] == n['group']),{'group':'_unknown','count':None})
            if matching_d['count'] == None or n['count']== None:
                divided = None
            else:
                divided = n['count'] / matching_d['count']

            item = dict({'group':n['group'], 'count':divided}) #TODO here and elsewhere need to change 'count' to 'value' for clarity, but need to fix front end to expect this first
            items.append(item)

    return {'items':items, 'grouping':numerator_data['grouping'], 'data_id':numerator_data['grouping']}
