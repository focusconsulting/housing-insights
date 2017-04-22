+---
 +layout: www.consumerfinance.org
 +tablename: hmda
 +title: Home Mortgage Disclosure Act Data - DC Only - 2007-2015
 +---
 +<!--No need to put a header; the title in the front matter (above) will be used as a header-->
 +
 +The Home Mortgage Disclosure Act (HMDA) requires many financial institutions to maintain, report, and publicly disclose information about mortgages. These public data are important because they help show whether lenders are serving the housing needs of their communities; they give public officials information that helps them make decisions and policies; and they shed light on lending patterns that could be discriminatory. HMDA records provide useful context on mortgages in DC. 
 +
 +This data was downloaded from [www.consumerfinance.org](https://www.consumerfinance.gov/data-research/hmda/explore). It does not contain any unique building or property identifiers, however each record reflects an individual mortgage application. The highest level of geospatial fidelity available per record is the Census tract.
 +
 +We should be able to join these records to other tables in the Preservation Catalog based on the ‘census_tract_number’ value.
 +
 +The cleaner for this dataset replaced null values and appended the label "Tract" to the numeric Census tract value in order to make it consistent with our production database.
 +
 +## Remaining issues
 +
 +The following issues will need to be addressed:
 +
 +* run a test to ensure that the records can be joined to the rest of the database using the 'census_tract_number' value.
 +