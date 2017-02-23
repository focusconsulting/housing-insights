SELECT * FROM project WHERE project.proj_name ILIKE '%friendship Terrace%';
SELECT * FROM subsidy WHERE nlihc_id = 'NL000120'

SELECT * FROM real_property WHERE nlihc_id = 'NL000120'

SELECT ssl, proj_name FROM project 
INNER JOIN parcel
ON parcel.nlihc_id = project.nlihc_id
WHERE project.proj_name ILIKE '%friendship Terrace%';




SELECT * FROM dc_tax WHERE dc_tax.ssl ILIKE '%1676%0015%'
