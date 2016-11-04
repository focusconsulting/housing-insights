/*
SELECT * from dc_tax limit 10;
SELECT count(*), count (distinct ssl) as distinct_ssl, count (distinct index) as distinct_index from dc_tax;+
SELECT * from parcel limit 10;
*/




/* Investigating double counting. 


--Records in	project	only					362
--		project left join real_property			1109
--		project left join parcel			910
--		project left join parcel left join dc_tax	910

SELECT COUNT(*)
FROM project
LEFT JOIN public.parcel
	ON project."nlihc_id" = parcel."nlihc_id"
LEFT JOIN public.dc_tax
		ON parcel."ssl" = dc_tax."ssl"
LEFT JOIN public.real_property
	ON project."nlihc_id" = parcel."nlihc_id"



This query reveals a few data quality issues:
	--when run on 'Cluster 26' reveals one method of double counting: Potomac Gardens Senior and Potomac Gardens Family are two separate projects but have the same SSL, so appraisal is double counted
	--Run with 'Cluster 3' for missing data problem - 1425 T Street Cooperative is not found in tax records
	
SELECT proj_name
    , parcel.ssl
    , dc_tax.ssl
    , dc_tax.index
    , appraised_value_current_land
    , parcel.*

FROM project
LEFT JOIN public.parcel
	ON project."nlihc_id" = parcel."nlihc_id"
LEFT JOIN public.dc_tax
	ON parcel."ssl" = dc_tax."ssl"
WHERE 
project.cluster_tr2000 = 'Cluster 3';


--Searching for 1425 T Street - doesn't appear in Tax database. Also searched online, doesn't appear. 

SELECT * 
FROM dc_tax
WHERE dc_tax.ssl ILIKE '0205%'
*/





--Total land value by Neighborhood Cluster
--Currently this query double counts cases with multiple projects sharing the same SSL

--These outer queries just append calculated columns using the renamed fields from the inner SELECT statement.
SELECT *, ROUND(missing_tax_count::numeric / ssl_count::numeric, 2) AS percent_ssl_missing 
FROM ( 
	--This inner query is the main deal.
	SELECT 
	project.cluster_tr2000
	    , count (distinct project.nlihc_id) as project_nlihc_count
	    , count (distinct parcel."ssl") as ssl_distinct_count
	    , count (parcel."ssl") as ssl_count
	    , count (dc_tax."appraised_value_current_land") as appraised_value_count
	    , sum (
		CASE WHEN dc_tax.appraised_value_current_land IS NULL then 1
		ELSE 0 END)
		AS missing_tax_count
	    , coalesce(sum(dc_tax."appraised_value_current_land"), 0) as sum_appraised_value_current_land
	    , round(avg(zillow_zri_zip."2016-09")) as avg_zip_rent --should actually be weighted average, but doing this temporarily    
	    , project.cluster_tr2000_name

	FROM project
	LEFT JOIN public.zillow_zri_zip
		ON project."proj_zip" = zillow_zri_zip."regionname"
	LEFT JOIN public.parcel
		ON project."nlihc_id" = parcel."nlihc_id"
	LEFT JOIN public.dc_tax
		ON parcel."ssl" = dc_tax."ssl"
	GROUP BY project.cluster_tr2000
		, project.cluster_tr2000_name       
	ORDER BY project.cluster_tr2000
	) AS summary_table
;


/*
--Total unit count of the projects by cluster. Doing this in the lower table is inaccurate because the LEFT JOIN duplicates this data. 
SELECT project.cluster_tr2000
	, SUM(
		CASE WHEN project.proj_units_assist_max = 'N' THEN 0
		     ELSE project.proj_units_assist_max::bigint
		     END
		 ) AS sum_assisted_units
	, SUM (
	    CASE WHEN project.proj_units_assist_max IS NULL then 1
		 WHEN project.proj_units_assist_max = 'N' THEN 1
	         ELSE 0 END
	    ) AS missing_assist_max
	 , AVG(
		CASE WHEN project.proj_units_assist_max = 'N' THEN 0
		     ELSE project.proj_units_assist_max::bigint
		     END
		 ) AS avg_assisted_per_project
from project
group by project.cluster_tr2000
ORDER BY project.cluster_tr2000
;
*/