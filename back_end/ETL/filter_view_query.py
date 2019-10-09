# This query is very long, but serves the purpose of sending data to the
# "filter view". Some of the columns could be renamed in the future when the
# front end is refactored, and the entire view could be simplified to avoid
# using a query like this at all.

query = '''
    SELECT
      new_project.nlihc_id,
      new_project.census_tract,
      new_project.neighborhood_cluster,
      new_project.ward,
      new_project.proj_name,
      new_project.proj_addre,
      new_project.proj_units_tot,
      new_project.proj_units_assist_max,
      new_project.proj_owner_type,
      sub.portfolio,
      sub.poa_end,
      sub.poa_start,
      new_project.most_recent_topa_date,
      new_project.topa_count,
      new_project.most_recent_reac_score_num,
      new_project.most_recent_reac_score_date,
      new_project.sum_appraised_value_current_total,

      tract.violent_crime_rate       AS violent_crime_count_census_tract,
      cluster.violent_crime_rate     AS violent_crime_count_neighborhood_cluster,
      ward.violent_crime_rate        AS violent_crime_count_ward,

      tract.non_violent_crime_rate   AS non_violent_crime_rate_census_tract,
      cluster.non_violent_crime_rate AS non_violent_crime_rate_neighborhood_cluster,
      ward.non_violent_crime_rate    AS non_violent_crime_rate_ward,

      tract.crime_rate               AS crime_rate_census_tract,
      cluster.crime_rate             AS crime_rate_neighborhood_cluster,
      ward.crime_rate                AS crime_rate_ward,

      tract.construction_permits     AS construction_permits_rate_census_tract,
      cluster.construction_permits   AS construction_permits_rate_neighborhood_cluster,
      ward.construction_permits      AS construction_permits_rate_ward,

      tract.total_permits            AS building_permits_rate_census_tract,
      cluster.total_permits          AS building_permits_rate_neighborhood_cluster,
      ward.total_permits             AS building_permits_rate_ward,

      tract.poverty_rate             AS poverty_rate_census_tract,
      cluster.poverty_rate           AS poverty_rate_neighborhood_cluster,
      ward.poverty_rate              AS poverty_rate_ward,

      tract.income_per_capita           AS income_per_capita_census_tract,
      cluster.income_per_capita         AS income_per_capita_neighborhood_cluster,
      ward.income_per_capita            AS income_per_capita_ward,

      tract.labor_participation         AS labor_participation_census_tract,
      cluster.labor_participation       AS labor_participation_neighborhood_cluster,
      ward.labor_participation          AS labor_participation_ward,

      tract.fraction_single_mothers     AS fraction_single_mothers_census_tract,
      cluster.fraction_single_mothers   AS fraction_single_mothers_neighborhood_cluster,
      ward.fraction_single_mothers      AS fraction_single_mothers_ward,

      tract.fraction_foreign            AS fraction_foreign_census_tract,
      cluster.fraction_foreign          AS fraction_foreign_neighborhood_cluster,
      ward.fraction_foreign             AS fraction_foreign_ward,

      tract.acs_median_rent             AS acs_median_rent_census_tract,
      cluster.acs_median_rent           AS acs_median_rent_neighborhood_cluster,
      ward.acs_median_rent              AS acs_median_rent_ward

      FROM
        new_project
        LEFT JOIN (SELECT * FROM new_zone_facts WHERE zone_type = 'census_tract') AS tract
        ON new_project.census_tract = tract.zone

        LEFT JOIN (SELECT * FROM new_zone_facts WHERE zone_type = 'neighborhood_cluster') AS cluster
        ON new_project.neighborhood_cluster = cluster.zone

        LEFT JOIN (SELECT * FROM new_zone_facts WHERE zone_type = 'ward') AS ward
        ON new_project.ward = ward.zone

        LEFT JOIN (
            SELECT
              nlihc_id,
              MIN(poa_start) AS poa_start,
              MAX(poa_end) AS poa_end,
              MAX(portfolio) AS portfolio
              FROM new_subsidy
              GROUP BY nlihc_id) AS sub
        ON new_project.nlihc_id = sub.nlihc_id
    ;
'''



