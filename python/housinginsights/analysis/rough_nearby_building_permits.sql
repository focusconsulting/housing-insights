--select * from project where proj_name ILIKE '%Friendship Terrace%'

/* 
Calculated approximate lat/lon square using haversine formula
0.5 miles:
+-0.008 lat
+- 0.011 lon
*/

--Friendship Terrace
SELECT
    (latitude - 38.94907321 ) AS lat_diff
    ,(longitude - -77.08236855 ) AS lon_diff
    ,to_date(issue_date, 'YYYY-MM-DD') AS issue_date_asdate
    ,*
FROM building_permits

WHERE latitude < (38.94907321 + .004)::DECIMAL
AND   latitude > (38.94907321 - .004)::DECIMAL
AND   longitude < (-77.08236855 + .005)::DECIMAL
AND   longitude > (-77.08236855 - .005)::DECIMAL

AND to_date(issue_date, 'YYYY-MM-DD') > CURRENT_DATE - INTERVAL '3 months'

/*
where latitude::decimal between (38.94907321 + 1)::decimal and (38.94907321 - 0.008)::decimal
and longitude::decimal between (-77.08236855 + 1)::decimal and(-77.08236855 - .011)::decimal

limit 100
*/