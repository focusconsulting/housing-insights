WITH rent_joins AS (
 SELECT proj_name
        , geo2010
        , acs_code
        , acs_rent_lower.hd01_vd01 AS quartile1_neighborhood_rent
        , acs_rent_median.hd01_vd01 AS median_neighborhood_rent
        , acs_rent_upper.hd01_vd01 AS quartile3_neighborhood_rent
        , acs_rent_upper.data_version AS upper_data_version
        , acs_rent_median.data_version AS median_data_version
        , acs_rent_lower.data_version AS lower_data_version
        
    FROM project
    INNER JOIN census_mapping
    ON project.geo2010 = census_mapping.prescat_code
    INNER JOIN acs_rent_median
    ON census_mapping.acs_code::TEXT = acs_rent_median.geo_id2::TEXT
    INNER JOIN acs_rent_lower
    ON census_mapping.acs_code::TEXT = acs_rent_lower.geo_id2::TEXT
    INNER JOIN acs_rent_upper
    ON census_mapping.acs_code::TEXT = acs_rent_upper.geo_id2::TEXT
)
    
, acs_14_rent AS (
    SELECT * FROM rent_joins
    WHERE upper_data_version = 'ACS_14_5YR'
    AND median_data_version = 'ACS_14_5YR'
    AND lower_data_version = 'ACS_14_5YR'
)

, acs_09_rent AS (
    SELECT * FROM rent_joins
       WHERE upper_data_version = 'ACS_09_5YR'
       AND median_data_version = 'ACS_09_5YR'
       AND lower_data_version = 'ACS_09_5YR'
)

SELECT * FROM acs_14_rent
WHERE proj_name ILIKE '%Friendship Terrace%'
UNION
SELECT * FROM acs_09_rent
WHERE proj_name ILIKE '%Friendship Terrace%'



