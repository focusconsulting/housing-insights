SELECT 
program_1
, round(avg(num_programs_in_building),2) AS avg_num_programs

FROM (
    SELECT 
    id
    , program_1
    , count(subsidy_2) AS num_programs_in_building
    
    FROM (
        --running just this inner query produces a pivotable table for exploration
        SELECT 
        v1.nlihc_id AS id
        ,v1.program AS program_1
        ,v2.program AS program_2
        ,v1.subsidy_id AS subsidy_1
        ,v2.subsidy_id AS subsidy_2

        FROM subsidy AS v1
        INNER JOIN subsidy AS v2
        ON v1.nlihc_id = v2.nlihc_id

        --optionally filter to better understand what the query produces
        --where v1.nlihc_id in ('NL000001','NL000003')
        
        ) AS program_pairs
       
    --data problem: this double-counts programs when there are more than 1 of the same program on a building (i.e. 2 section 8 contracts). 
    GROUP BY program_1, id
        
) AS counts_by_program
GROUP BY program_1
ORDER BY avg_num_programs
    
    