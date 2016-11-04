SELECT project.proj_name
    , count(project.nlihc_id) as project_nlihc_count
    , count(parcel.ssl) as parcel_count
    , project.cluster_tr2000
    , coalesce(sum(dc_tax."appraised_value_current_land"), 0) as sum_appraised_value_current_land
    , zillow_zri_zip."2016-09" as avg_zip_rent
    , real_property."nlihc_id"
    , real_property."ssl"
FROM project
LEFT JOIN public.zillow_zri_zip
	ON project."proj_zip" = zillow_zri_zip."regionname"
LEFT JOIN public.real_property
	ON project."nlihc_id" = real_property."nlihc_id"
LEFT JOIN public.dc_tax
	ON real_property."ssl" = dc_tax."ssl"
LEFT JOIN parcel
	ON parcel."nlihc_id" = real_property."nlihc_id"
	AND parcel.ssl = dc_tax.ssl
GROUP BY project.cluster_tr2000
        , project.proj_name
        , zillow_zri_zip."2016-09"
        , real_property."nlihc_id"
        , real_property."ssl"
LIMIT 20;