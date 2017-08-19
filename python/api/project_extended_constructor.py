from flask import Blueprint
from api.utils import get_zone_facts_select_columns
from flask import jsonify

from sqlalchemy.sql import text

def construct_project_extended_blueprint(name, engine, tables, models):
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
            q+= "WHERE nlihc_id =:nlihc_id"#.format(nlihc_id)

        conn = engine.connect()
        proxy = conn.execute(text(q), nlihc_id=nlihc_id)

        results = [dict(x) for x in proxy.fetchall()]
        

        #Add one-to-many table results
        if nlihc_id != None and len(results) > 0:
            for tablename in ['topa', 'subsidy','real_property','reac_score']:
                if tablename in tables:
                    try:
                        q = """
                            select t.*
                            from {} as t
                            where nlihc_id=:nlihc_id;
                            """.format(tablename) #using if tablename in tables above to protect against sql injection

                        proxy = conn.execute(text(q),tablename=tablename, nlihc_id=nlihc_id)
                        res = [dict(x) for x in proxy.fetchall()]
                        results[0][tablename] = res
                    except Exception as e:
                        results[0][tablename] = 'Error'

        conn.close()
        output = {'objects': results}
        return jsonify(output)

    return blueprint