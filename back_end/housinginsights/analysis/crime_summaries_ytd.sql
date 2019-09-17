SELECT COALESCE(census_tract,'Unknown') AS census_tract
,count(offense) AS total_offenses_past_1_year
FROM crime
WHERE report_date BETWEEN (now()::TIMESTAMP - INTERVAL '1 year')
                 AND now()::TIMESTAMP
GROUP BY census_tract 
ORDER BY census_tract


