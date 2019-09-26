
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
    # TODO: Put this somewhere else
        q = """
            SELECT
                project.nlihc_id,
                project.census_tract,
                project.neighborhood_cluster,
                project.ward,
                project.proj_name,
                project.proj_addre,
                project.proj_units_tot,
                project.proj_units_assist_max,
                project.proj_owner_type,
                subsidy.portfolio,
                to_char(subsidy.poa_start, 'YYYY-MM-DD') as poa_start,
                to_char(subsidy.poa_end, 'YYYY-MM-DD') as poa_end,
                project.most_recent_topa_date,
                project.topa_count,
                project.most_recent_reac_score_num,
                project.most_recent_reac_score_date,
                project.sum_appraised_value_current_total,
            """
        q += ward_selects
        q += cluster_selects
        q += tract_selects

        q += """
                FROM project
                LEFT JOIN zone_facts AS z1
                       ON z1.zone = project.ward
                LEFT JOIN zone_facts AS z2
                       ON z2.zone = project.neighborhood_cluster
                LEFT JOIN zone_facts AS z3
                       ON z3.zone = project.census_tract
                LEFT JOIN subsidy AS s on s.nlihc_id = p.nlihc_id
            """

        conn = engine.connect()
        proxy = conn.execute(q)
        results = [dict(x) for x in proxy.fetchall()]
        conn.close()
        output = {'objects': results}
        return jsonify(output)

    #End of the constructor returns the assembled blueprint
    return blueprint
