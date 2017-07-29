
from flask import Blueprint
from flask import jsonify

import logging


def construct_filter_blueprint(name, engine):

    blueprint = Blueprint(name, __name__, url_prefix='/api')

    @blueprint.route('/filter/', methods=['GET'])
    def filter_data():
        q = """
            select p_z_w_nc.*,
            poverty_rate as census_tract_poverty_rate,
            fraction_black as census_tract_fraction_black,
            income_per_capita as census_tract_income_per_capita,
            labor_participation as census_tract_labor_participation,
            fraction_foreign as census_tract_fraction_foreign,
            fraction_single_mothers as census_tract_fraction_single_mothers,
            acs_lower_rent_quartile as census_tract_acs_lower_rent_quartile,
            acs_median_rent as census_tract_median_rent,
            acs_upper_rent_quartile as census_tract_acs_upper_rent_quartile,
            crime_count as census_tract_crime_count,
            violent_crime_count as census_tract_violent_crime_count,
            non_violent_crime_count as census_tract_non_violent_crime_count,
            crime_rate as census_tract_crime_rate,
            violent_crime_rate as census_tract_violent_crime_rate,
            non_violent_crime_rate as census_tract_non_violent_crime_rate,
            building_permits as census_tract_building_permits,
            construction_permits as census_tract_construction_permits
            from zone_facts
            right join (  select p_z_w.*,
              poverty_rate as neighborhood_cluster_poverty_rate,
              fraction_black as neighborhood_cluster_fraction_black,
              income_per_capita as neighborhood_cluster_income_per_capita,
              labor_participation as neighborhood_cluster_labor_participation,
              fraction_foreign as neighborhood_cluster_fraction_foreign,
              fraction_single_mothers as neighborhood_cluster_fraction_single_mothers,
              acs_lower_rent_quartile as neighborhood_cluster_acs_lower_rent_quartile,
              acs_median_rent as neighborhood_cluster_median_rent,
              acs_upper_rent_quartile as neighborhood_cluster_acs_upper_rent_quartile,
              crime_count as neighborhood_cluster_crime_count,
              violent_crime_count as neighborhood_cluster_violent_crime_count,
              non_violent_crime_count as neighborhood_cluster_non_violent_crime_count,
              crime_rate as neighborhood_cluster_crime_rate,
              violent_crime_rate as neighborhood_cluster_violent_crime_rate,
              non_violent_crime_rate as neighborhood_cluster_non_violent_crime_rate,
              building_permits as neighborhood_cluster_building_permits,
              construction_permits as neighborhood_cluster_construction_permits
              from zone_facts
              right join ( select project.*,
                poverty_rate as ward_poverty_rate,
                fraction_black as ward_fraction_black,
                income_per_capita as ward_income_per_capita,
                labor_participation as ward_labor_participation,
                fraction_foreign as ward_fraction_foreign,
                fraction_single_mothers as ward_fraction_single_mothers,
                acs_lower_rent_quartile as ward_acs_lower_rent_quartile,
                acs_median_rent as ward_median_rent,
                acs_upper_rent_quartile as ward_acs_upper_rent_quartile,
                crime_count as ward_crime_count,
                violent_crime_count as ward_violent_crime_count,
                non_violent_crime_count as ward_non_violent_crime_count,
                crime_rate as ward_crime_rate,
                violent_crime_rate as ward_violent_crime_rate,
                non_violent_crime_rate as ward_non_violent_crime_rate,
                building_permits as ward_building_permits,
                construction_permits as ward_construction_permits
                from project
                left join zone_facts on project.ward = zone_facts.zone
                ) as p_z_w
              on p_z_w.neighborhood_cluster = zone_facts.zone
              ) as p_z_w_nc
            on p_z_w_nc.census_tract = zone_facts.zone;
            """

        conn = engine.connect()
        proxy = conn.execute(q)
        results = [dict(x) for x in proxy.fetchall()]
        conn.close()
        output = {'items': results}
        return jsonify(output)

    #End of the constructor returns the assembled blueprint
    return blueprint
