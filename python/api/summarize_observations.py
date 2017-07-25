'''
This module contains the endpoint for returning the summary of any table that
contains unique observations as each row of data. This includes the crime
table, building permits table, etc, where each row represents one crime incident
and the endpoint counts the number of instances that match the users
criteria per the url params. 


Note, this approach will not typically be needed as this method is being replaced by use
of the ZoneFacts table, which calculates these stats on data load. These endpoints, however
can calculate custom versions of this data (i.e. changing start/enddates etc), so keeping 
them registered in case they are needed. 
'''


from flask import Blueprint, request, jsonify

import dateutil.parser as dateparser

from api.utils import items_divide

def construct_summarize_observations(name, engine):
    '''
    This function returns a blueprint instance that was created using the 
    provided name and database engine. It is necessary to use a constructor
    so that we can instantiate the database engine just once, in the 
    application.py, and make it accessible to all the endpoints that need it. 
    '''

    blueprint = Blueprint(name, __name__, url_prefix='/api')

    @blueprint.route('/<method>/<table_name>/<filter_name>/<months>/<grouping>', methods=['GET'])
    def summarize_observations(method,table_name,filter_name,months,grouping):
        '''
        This endpoint takes a table that has each record as list of observations 
        (like our crime and building_permits tables) and returns summary statistics
        either as raw counts or as a rate, optionally filtered. 

        methods: "count" or "rate"
        table_name: name of the table in the database, e.g. 'building_permits' or 'crime'
        filter_name: code name of the filter to apply to the data, which varies by table
                    "all" - no filtering applied
                    "construction" - only building_permits with permit_type_name = 'CONSTRUCTION'
                    "violent" - only crimes where the offense type is a violent crime (note, not 100% match, need to compare DCPD definitions to official to verify)
                    "nonviolent" - the other crime incidents
        months: The number of months of date to include. By default this is from now() but can be modified by an optional parameter
        grouping: What to use for the 'GROUP BY' clause, e.g. 'ward', 'neighbourhood_cluster', 'zip', 'census_tract'. 
                Can accept any valid column name, so 'offense' for crime or 'permit_type_name' for building_permits are also valid
        
        Optional params:
        start: YYYYMMDD format start date to use instead of now() for the duration filter


        replaces the count_all method that is deprecated

        Example working URLS:
        /api/count/crime/all/12/ward - count of all crime incidents
        /api/count/building_permits/construction/12/neighborhood_cluster - all construction permits in the past year grouped by neighborhood_cluster
        '''


        ###########################
        #Handle filters
        ###########################
        #Be sure concatenated 'AND' statements have a space in front of them
        additional_wheres = ''
        if filter_name == 'all':
            additional_wheres += " "

        # Filter options for building_permits
        elif filter_name == 'construction':
            additional_wheres += " AND permit_type_name = 'CONSTRUCTION' "
        
        # Filter options for crime
        elif filter_name == 'violent':
            additional_wheres += " AND OFFENSE IN ('ROBBERY','HOMICIDE','ASSAULT W/DANGEROUS WEAPON','SEX ABUSE')"
        elif filter_name == 'nonviolent':
            additional_wheres += " AND OFFENSE NOT IN ('ROBBERY','HOMICIDE','ASSAULT W/DANGEROUS WEAPON','SEX ABUSE')"


        # Fallback for an invalid filter
        else:
            additional_wheres += " Incorrect filter name - this inserted SQL will cause query to fail"

        ##########################
        #Handle date range
        ##########################
        date_fields = {'building_permits': 'issue_date', 'crime': 'report_date'}
        date_field = date_fields[table_name]

        #method currently not implemented. 'count' or 'rate'


        start_date = request.args.get('start')
        print("Start_date found: {}".format(start_date))
        if start_date == None:
            start_date = "now()"
        else:
            start_date = dateparser.parse(start_date,dayfirst=False,yearfirst=False)
            start_date = datetime.strftime(start_date,'%Y-%m-%d')
            start_date = "'" + start_date + "'"

        date_range_sql = ("({start_date}::TIMESTAMP - INTERVAL '{months} months')"
                          " AND {start_date}::TIMESTAMP"
                          ).format(start_date=start_date, months=months)


        #########################
        #Optional - validate other inputs
        #########################
        #Should we restrict the group by to a specific list, or allow whatever people want? 
        #Ditto for table name


        ###############
        #Get results
        ###############
        api_results = count_observations(table_name, grouping, date_field, date_range_sql, additional_wheres)

        #Edit the data_id. TODO this is not specific enough, need univeral system for handling unique data ids to be used on front end. 
        #Is this better handled here in the API or front end exclusively?
        api_results['data_id'] += '_' + filter_name


        # Apply the normalization if needed
        if method == 'rate':
            if table_name in ['building_permits']:
                denominator = get_residential_units(grouping)
                api_results = items_divide(api_results, denominator)
                api_results = scale(api_results, 1000) #per 1000 residential units
            if table_name in ['crime']:
                denominator = get_weighted_census_results(grouping, 'population')
                api_results = items_divide(api_results, denominator)
                api_results = scale(api_results, 100000) #crime incidents per 100,000 people
        
        #Output as JSON
        return jsonify(api_results)


    def scale(data,factor):
        '''
        Multiplies each of the items 'count' entry by the factor
        '''

        for idx, d in enumerate(data['items']):
            try:
                data['items'][idx]['count'] = (data['items'][idx]['count'] * factor)
            except Exception as e:
                data['items'][idx]['count'] = None

        return data

    def get_population(grouping):
        '''
        Returns the population count for each zone in the standard 'items' format
        '''
        #TODO implement me
        return None

    def get_residential_units(grouping):
        '''
        Returns the number of residential units in the standard 'items' format
        '''
        #TODO implement me
        return None

    def count_observations(table_name, grouping, date_field, date_range_sql, additional_wheres=''):
        fallback = "'Unknown'"

        try:
            conn = engine.connect()

            q = """
                SELECT COALESCE({grouping},{fallback}) --'Unknown'
                ,count(*) AS records
                FROM {table_name}
                where {date_field} between {date_range_sql}
                {additional_wheres}
                GROUP BY {grouping}
                ORDER BY {grouping}
                """.format(grouping=grouping,fallback=fallback,table_name=table_name,
                    date_field=date_field,date_range_sql=date_range_sql,additional_wheres=additional_wheres)

            proxy = conn.execute(q)
            results = proxy.fetchall()

            #transform the results.
            #TODO should come up with a better generic way to do this using column
              #names for any arbitrary sql table results.
            formatted = []
            for x in results:
                dictionary = dict({'group':x[0], 'count':x[1]})
                formatted.append(dictionary)


            conn.close()
            return {'items': formatted, 'grouping':grouping, 'data_id':table_name}

        #TODO do better error handling - for interim development purposes only
        except Exception as e:
            #conn.close()
            return {'items': None, 'notes':"Query failed: {}".format(e), 'grouping':grouping, 'data_id':table_name}

    return blueprint
