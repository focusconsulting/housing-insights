
from flask import Blueprint
from flask import jsonify

import logging

from flask_cors import cross_origin

def construct_filter_blueprint(name, engine):

    blueprint = Blueprint(name, __name__, url_prefix='/api')

    @blueprint.route('/filter/', methods=['GET'])
    @cross_origin()
    def filter_data():

        conn = engine.connect()
        proxy = conn.execute("select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='zone_facts'")
        zcolumns = [x[0] for x in proxy.fetchall()]

        ward_selects = ''
        cluster_selects = ''
        tract_selects = ''

        for c in zcolumns:
            ward_selects += (',z1.' + c + ' AS ' + c + '_ward')
            cluster_selects += (',z2.' + c + ' AS ' + c + '_neighborhood_cluster')
            tract_selects += (',z3.' + c + ' AS ' + c + '_census_tract')

        q = """
                select
                p.nlihc_id
                , p.proj_units_tot
                , p.proj_units_assist_max
                , cast(p.proj_units_assist_max / p.proj_units_tot as decimal(3,2)) as percent_affordable_housing --TODO make this calculated field in projects table
                , p.hud_own_type
                , p.ward
                , p.anc
                , p.census_tract
                , p.neighborhood_cluster
                , p.neighborhood_cluster_desc
                , p.zip

                , s.portfolio
                , s.agency
                , to_char(s.poa_start, 'YYYY-MM-DD') as poa_start
                , to_char(s.poa_end, 'YYYY-MM-DD') as poa_end
                , to_char(s.poa_start_orig, 'YYYY-MM-DD') as poa_start_orig

                , s.units_assist
                , s.subsidy_id
                
            """
        q += ward_selects
        q += cluster_selects
        q += tract_selects

        q += """
                from project as p
                
                left join zone_facts as z1 on z1.zone = p.ward
                left join zone_facts as z2 on z2.zone = p.neighborhood_cluster
                left join zone_facts as z3 on z3.zone = p.census_tract

                left join subsidy as s on s.nlihc_id = p.nlihc_id
            """

        
        proxy = conn.execute(q)
        results = [dict(x) for x in proxy.fetchall()]
        conn.close()
        output = {'objects': results}
        return jsonify(output)

    #End of the constructor returns the assembled blueprint
    return blueprint
