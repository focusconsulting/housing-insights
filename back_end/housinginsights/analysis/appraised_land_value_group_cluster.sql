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

--This outer query just appends calculated columns using the renamed fields from the inner SELECT statement.
SELECT *
	, ROUND(missing_tax_count::numeric / ssl_count::numeric, 2) AS percent_ssl_missing
	, ROUND(sum_appraised_value_current_land / appraised_value_count) as average_land_appraisal  --this can be used to fill in missing appraisals for the sum
FROM ( 
	--This inner query is the main deal.
	SELECT 
	unique_ssls.cluster_tr2000
	    , sum (unique_ssls.project_count) as project_count
	    , count (distinct unique_ssls.ssl) as ssl_distinct_count
	    , count (unique_ssls.ssl) as ssl_count
	    , count (dc_tax."appraised_value_current_land") as appraised_value_count
	    , sum (
		CASE WHEN dc_tax.appraised_value_current_land IS NULL then 1
		ELSE 0 END)
		AS missing_tax_count

	    , sum(dc_tax."appraised_value_prior_land") as sum_appraised_value_prior_land
	    , sum(dc_tax."appraised_value_prior_total") as sum_appraised_value_prior_total
	    , sum(dc_tax."appraised_value_current_land") as sum_appraised_value_current_land
	    , sum(dc_tax."appraised_value_current_total") as sum_appraised_value_current_total

	    , unique_ssls.cluster_tr2000_name

	--To avoid double counting projects that have the same SSL, we need to make a summary table of projects that contains just unique ssls
	FROM (
		SELECT parcel.ssl
                    , count(project.nlihc_id) as project_count
		    , cluster_tr2000
		    , cluster_tr2000_name
		FROM project
		LEFT JOIN parcel
		     ON parcel.nlihc_id = project.nlihc_id
		WHERE project.status = 'Active'

			--Temporarily excluding these properties from analysis due to suspicious data. TODO - investigate data issues. 
			AND project.nlihc_id NOT IN
				('NL000215' --Distorting the Cluster 19 avg value. Maybe high appraised improvement value or too low unit count? 
				)
		GROUP BY parcel.ssl
		    , cluster_tr2000
		    , cluster_tr2000_name
		) as unique_ssls

	LEFT JOIN public.dc_tax
		ON unique_ssls.ssl = dc_tax.ssl
	GROUP BY unique_ssls.cluster_tr2000
		, unique_ssls.cluster_tr2000_name       
	ORDER BY unique_ssls.cluster_tr2000
	) AS summary_table
;

/*Investigating why Cluster 19 has such high assessed values
SELECT *
FROM project
LEFT JOIN parcel
	ON parcel.nlihc_id = project.nlihc_id
LEFT JOIN public.dc_tax
		ON parcel.ssl = dc_tax.ssl
WHERE cluster_tr2000 = 'Cluster 19'

--This is the property that has a much higher assessed value. Either value or unit count might be wrong?
AND project.nlihc_id NOT IN ('NL000215')
*/


/*
--Total unit count of the projects by cluster, to be appended to the land value table
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