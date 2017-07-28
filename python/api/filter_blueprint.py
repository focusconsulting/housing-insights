
from flask import Blueprint
from flask import jsonify

import logging


def construct_filter_blueprint(name, engine):

    blueprint = Blueprint(name, __name__, url_prefix='/api')

    @blueprint.route('/filter/', methods=['GET'])
    def filter_data():
        q = """
            select p.nlihc_id
              , p.proj_units_tot
              , p.proj_units_assist_max
              , cast(p.proj_units_assist_max / p.proj_units_tot as decimal(3,2)) as percent_affordable_housing
              , p.hud_own_type
              , p.ward
              , p.anc
              , p.census_tract
              , p.neighborhood_cluster
              , p.neighborhood_cluster_desc
              , p.zip
              , c.acs_median_rent
              , s.portfolio
              , s.agency
              , to_char(s.poa_start, 'YYYY-MM-DD') as poa_start
              , to_char(s.poa_end, 'YYYY-MM-DD') as poa_end
              , s.units_assist
              , s.subsidy_id
            from project as p
            left join census as c on c.census_tract = p.census_tract and c.unique_data_id = 'acs5_2015'
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
