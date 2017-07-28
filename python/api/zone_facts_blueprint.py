
from flask import Blueprint
from flask import jsonify

import logging


from api.utils import items_divide

def construct_zone_facts_blueprint(name, engine):

    blueprint = Blueprint(name, __name__, url_prefix='/api')
      




    #TODO need to add something that draws directly from zonefacts to replace below endpoint









    # this method is deprecated in favor of the zone facts table. Should remove once that is finalized
    @blueprint.route('/census/<data_id>/<grouping>', methods=['GET'])
    def census_with_weighting(data_id,grouping):
        '''
        API Endpoint to get data from our census table. data_id can either be a column
        name or a custom calculated value.

        data_id: if in the list of calculated values, perform custom calculation. Otherwise, 
                try to get it from the census database table as a column name

        grouping: one of 'census_tract', 'ward', or 'neighborhood_cluster'
        '''
        if data_id in ['poverty_rate','fraction_black','income_per_capita',
                        'labor_participation','fraction_foreign','fraction_single_mothers']:

            if data_id == 'poverty_rate':
                denominator = get_weighted_census_results(grouping, 'population')
                numerator = get_weighted_census_results(grouping, 'population_poverty')
            if data_id == 'fraction_black':
                numerator = get_weighted_census_results(grouping, 'population_black')
                denominator = get_weighted_census_results(grouping, 'population')
            if data_id == 'income_per_capita':
                denominator = get_weighted_census_results(grouping, 'population')
                numerator = get_weighted_census_results(grouping, 'aggregate_income')
            if data_id == 'labor_participation':
                denominator = get_weighted_census_results(grouping, 'population')
                numerator = get_weighted_census_results(grouping,'population_working')
            if data_id == 'fraction_foreign':
                denominator = get_weighted_census_results(grouping, 'population')
                numerator = get_weighted_census_results(grouping, 'population_foreign')
            if data_id == 'fraction_single_mothers':
                denominator = get_weighted_census_results(grouping, 'population')
                numerator = get_weighted_census_results(grouping, 'population_single_mother')

            api_results = items_divide(numerator,denominator)
            #api_results = scale(api_results)
            api_results['data_id'] = 'poverty_rate'

        #If the data_id isn't one of our custom ones, assume it is a column name
        else:
            api_results = get_weighted_census_results(grouping, data_id)
        
        return jsonify(api_results)

    def get_weighted_census_results(grouping, field):
        '''
        queries the census table for the relevant field and returns the results as a weighted count
        returns the standard 'items' format

        Currently only implemented for the 'counts' weighting factor not for the proportion version
        '''
        q = "SELECT census_tract, {field} FROM census".format(field=field) #TODO need to add 'year' column for multiple census years when this is added to the data
        conn = engine.connect()
        proxy = conn.execute(q)
        census_results = [dict(x) for x in proxy.fetchall()]

        #Transform the results
        items = []  #For storing results as we go

        if grouping == 'census_tract':
            #No weighting required, data already in proper format
            for r in census_results:
                output = dict({'group':r['census_tract'], 'count':r[field]})
                items.append(output)

        elif grouping in ['ward', 'neighborhood_cluster']:
            proxy = conn.execute("SELECT DISTINCT {grouping} FROM census_tract_to_{grouping}".format(grouping=grouping))
            groups = [x[0] for x in proxy.fetchall()]

            
            for group in groups:
                proxy = conn.execute("SELECT * FROM census_tract_to_{grouping} WHERE {grouping} = '{group}'".format(grouping=grouping, group=group))
                results = [dict(x) for x in proxy.fetchall()]

                count = 0
                for result in results:
                    tract = result['census_tract']
                    factor = result['population_weight_counts']
                    matching_data = next((item for item in census_results if item["census_tract"] == tract),{field:None})
                    if matching_data[field] == None:
                        logging.warning("Missing data for census tract when calculating weightings: {}".format(tract))
                        matching_data[field] = 0
                        
                    value = matching_data[field]
                    count += (value * factor)

                output = dict({'group':group, 'count':round(count,0)})
                items.append(output)
        else:
            #Invalid grouping
            items = None

        conn.close()
        return {'items': items, 'grouping':grouping, 'data_id':field}




    #End of the constructor returns the assembled blueprint
    return blueprint