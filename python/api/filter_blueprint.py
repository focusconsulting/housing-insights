
from flask import Blueprint
from flask import jsonify
from api.utils import get_zone_facts_select_columns

import logging

from flask_cors import cross_origin

def construct_filter_blueprint(name, engine):

    blueprint = Blueprint(name, __name__, url_prefix='/api')

    @blueprint.route('/filter/', methods=['GET'])
    @cross_origin()
    def filter_data():

        ward_selects, cluster_selects, tract_selects = get_zone_facts_select_columns(engine)

        q = """
                select
                p.nlihc_id
                , p.proj_addre
                , p.proj_name
                , CONCAT(p.proj_name, ': ', p.proj_addre) as proj_name_addre
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

        conn = engine.connect()
        proxy = conn.execute(q)
        results = [dict(x) for x in proxy.fetchall()]
        conn.close()
        output = {'objects': results}
        return jsonify(output)

    #End of the constructor returns the assembled blueprint
    return blueprint
