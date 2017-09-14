
from flask import Blueprint
from flask import jsonify
from flask_cors import cross_origin

import logging


from api.utils import objects_divide
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import text

def construct_zone_facts_blueprint(name, engine):

    blueprint = Blueprint(name, __name__, url_prefix='/api')
      

    @blueprint.route('/zone_facts/<column_name>/<grouping>', methods = ['GET'])
    @cross_origin()
    def slice_zone_facts(column_name = 'poverty_rate', grouping='ward'):
        '''
        API endpoint to return just the column and grouping matching the passed
        values, in the format needed by the chloropleth map
        '''
        try:
            q = 'SELECT zone, :column_name FROM zone_facts \n'#.format(column_name)
            q += "WHERE zone_type =:grouping  \n"#.format(grouping)
            q += "ORDER BY zone \n"

            conn = engine.connect()
            proxy = conn.execute(text(q), 
                                column_name=column_name,
                                grouping=grouping)
            results = [dict(x) for x in proxy.fetchall()]
            status = 'success'
            conn.close()
        except ProgrammingError:
            #Occurs if column or group name is not in database
            results = []
            status = 'Not found'

        output = {'status': status, 'grouping': grouping, 'column_name': column_name, 'objects': results}
        return jsonify(output)

  
    #End of the constructor returns the assembled blueprint
    return blueprint
