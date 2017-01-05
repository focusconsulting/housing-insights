Data can be stored here, but remember that Github has a repository limit of 1GB. Only store small original data sources here - ask Neal for help with large files so they can be stored on Amazon S3.

### PresCat_Export_20160401
A (slightly) old version of the Preservation Catalog, our core data source of affordable housing buildings in DC. See the data dictionary in the folder itself for details.


### CensusTractMapping
The Preservation Catalog uses a different formatting convention from the acs_XXX_rent tables for identifying census tracts. This is a table downloaded from census that can be used to map between the two. TXT is the original version downloaded from census, .csv is a (manually) modified version that replaces ; with , and adds the word 'Tract' to match the Preservation Catalog. Downloaded from: https://www.census.gov/geo/maps-data/maps/2010ref/st11_tract.html
