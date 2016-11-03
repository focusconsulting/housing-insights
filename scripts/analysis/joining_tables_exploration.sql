/*Observations:
- Returns multiple rows for same project. Looks like property to Ssl is one to many. Should probably add up the appraised_land value. 
- Need to calculate ratio of avg_zip_rent to whatever the typical property rent is. 
*/

SELECT "Proj_Name"
	, zillow_zri_zip."2016-09" as avg_zip_rent
	, real_property."Nlihc_id"
	, real_property."Ssl"
	, dc_tax."APPRAISED_VALUE_CURRENT_LAND"

    FROM project
	LEFT JOIN public.zillow_zri_zip
	ON project."Proj_Zip" = zillow_zri_zip."RegionName"

	LEFT JOIN public.real_property
	ON project."Nlihc_id" = real_property."Nlihc_id"
	
	LEFT JOIN public.dc_tax
	ON real_property."Ssl" = dc_tax."SSL"

  LIMIT 20;
