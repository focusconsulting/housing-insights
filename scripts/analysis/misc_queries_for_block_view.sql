
--Ward unit and building counts
SELECT  ward2012 AS WARD
    , count(ward2012) AS building_count
    , sum(
        CASE WHEN proj_units_assist_max = 'N' THEN 0
            WHEN proj_units_assist_max IS NULL THEN 0
            ELSE proj_units_assist_max::INTEGER
        END
        ) AS total_subsidized_units

FROM project
GROUP BY ward2012;


--Building unit counts
SELECT  
    proj_name
    , cluster_tr2000_name
    , ward2012
    ,(
        CASE WHEN proj_units_assist_max = 'N' THEN 0
            WHEN proj_units_assist_max IS NULL THEN 0
            ELSE proj_units_assist_max::INTEGER
        END
        ) AS total_subsidized_units

FROM project
ORDER BY ward2012, proj_units_assist_max DESC;


--All buildings with their most recent REAC score, if it has one available
SELECT * FROM (
    SELECT  project.nlihc_id AS nlihhc_id
            , proj_name
            , reac_date
            , reac_score_num
            , first_value(reac_date) OVER (PARTITION BY proj_name ORDER BY reac_date DESC) AS most_recent_date
    FROM project
    LEFT JOIN reac_score
    ON reac_score.nlihc_id = project.nlihc_id
    --where proj_name = '1330 7th St Apts (Immaculate Conception)'
) AS table_w_most_recent
WHERE reac_date = most_recent_date OR most_recent_date IS NULL







