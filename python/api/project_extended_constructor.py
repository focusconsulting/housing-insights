from flask import Blueprint
from api.utils import get_zone_facts_select_columns
from flask import jsonify

def construct_project_extended_blueprint(name, engine):
    '''
    Provides an endpoint that provides an extended version of the project table that has been joined to 
    other tables. In particular, it joins to the zone_facts table to provide de-normalized statistics 
    about nearby developments. All endpoints still return one record per project. 
    '''

    blueprint = Blueprint(name, __name__, url_prefix='/api/project')

    @blueprint.route('/')
    @blueprint.route('/<nlihc_id>')
    def project_with_zone_facts(nlihc_id= None):

        ward_selects, cluster_selects, tract_selects = get_zone_facts_select_columns(engine)
        
        q = """
            select
            p.*
            """
        q += ward_selects
        q += cluster_selects
        q += tract_selects

        q +="""
            from project as p
            left join zone_facts as z1 on z1.zone = p.ward
            left join zone_facts as z2 on z2.zone = p.neighborhood_cluster
            left join zone_facts as z3 on z3.zone = p.census_tract
            """
        if nlihc_id != None:
            q+= "WHERE nlihc_id = '{}'".format(nlihc_id)

        conn = engine.connect()
        proxy = conn.execute(q)
        results = [dict(x) for x in proxy.fetchall()]
        conn.close()
        output = {'objects': results}
        return jsonify(output)

    return blueprint