# /big_data notes
This folder is not stored in Git, because the data file sizes are too large. Instead, they are synced to S3.

Most users will not need to have access to the source files in this folder, as they are loaded into our Postgres database once and then can be accessed from there. 


### Integrated_Tax_System_Public_Extract.csv
From opendata.dc.gov, this is a snapshot of the tax records for all properties in DC. 
Unclear how often the data is updated (might be from 2015). 
Source: http://opendata.dc.gov/datasets/496533836db640bcade61dd9078b0d63_53

### Integrated_Tax_System_Public_Extract_Facts.csv
Similar to above, but has more informative column names. It claims it is updated monthly, but 'lastmodifieddate' field is blank in the first rows (need to check all rows). Slight difference in the number of rows available from above (203,084 in 'Facts', 216,608 in original).
Source: http://opendata.dc.gov/datasets/496533836db640bcade61dd9078b0d63_53