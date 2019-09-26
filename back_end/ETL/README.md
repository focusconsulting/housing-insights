# ETL Process

This document outlines the Extract-Transform-Load (ETL) process for the
housing insights project. This portion of the project contains code to:

1. Download raw data from data sources.
2. Clean and transform that raw information into tabular data.
3. Load that data into the Postgres database.

As the Postgres database exists separately from this project repository the
ETL process may be run on a local machine.

## Usage
TBD

## Projects Table
The project table is created by combining data from the Preservation Catalog and 
affordable housing data from Open Data DC.

**Columns**:
- `nlihc_id`: Preservation catalog only
- `address_id`: Preservation catalog and open data DC
- `status`: Preservation catalog and open data DC
- `total_units`: Preservation catalog and open data DC
- `latitude`: Preservation catalog and open data DC
- `longitude`: Preservation catalog and open data DC
- `name`: Preservation catalog and open data DC
- `address`: Preservation catalog and open data DC
- `zip`: Preservation catalog only
- `units_assist_max`: Preservation catalog only
- `owner_type`: Preservation catalog only
- `tract`: Preservation catalog and open data DC
- `neighborhood_cluster`: Preservation catalog and open data DC
- `ward`: Preservation catalog and open data DC
- `source`: Preservation catalog and open data DC

## The Zone Facts Table
Half of the information available to the end user comes from the `zone_facts`
database table. It is constructed through the script `make_zone_facts.py`.

That script:
- Loads raw American Community Survey data.
- Loads raw building permit data.
- Loads raw crime occurrence data.
- Cleans and summarizes that data by census tract neighborhood cluster and ward.

The `zone_facts` table has the following information.

| Column                  | Description                                                              |
|-------------------------|--------------------------------------------------------------------------|
| zone_type               | Census tract, neighborhood cluster, or ward.                             |
| zone                    | Given the zone type, the number for that zone.                           |
| poverty_rate            | The population in poverty divided by the total population.               |
| fraction_black          | The black / African-American population divided by the total population. |
| income_per_capita       | The aggregate household income divided by the total population.          |
| labor_participation     | The number of people in the labor force divided by the total population. |
| fraction_foreign        | The number of foreign born citizens divided by the total populations.    |
| fraction_single_mothers | The number of single mother households divided by the total populations. |
| acs_median_rent         | The median rent in dollars according to the American Community Survey.   |
| crime_rate              | The number of crimes divided by the total populations.                   |
| violent_crime_rate      | The number of violent crimes divided by the total populations.           |
| non_violent_crime_rate  | The number of non violent crimes divided by the total populations.       |



## Raw Data Sources

#### American Community Survey

This project uses the latest 5 year estimates from the ACS, which is currently 2017. The tables used
specifically are:

| Detail Table |	Table Subject |	Description |
|--------------|----------------|-------------|
| B01003_001E	 | Age and Sex	| Total Population
| B25057_001E	 | Housing Characteristics	| LOWER CONTRACT RENT QUARTILE (DOLLARS)
| B25058_001E	 | Housing Characteristics	| MEDIAN CONTRACT RENT (DOLLARS)
| B25059_001E	 | Housing Characteristics	| UPPER CONTRACT RENT QUARTILE (DOLLARS)
| B02001_003E	 | Race | Black population
| B17020_002E	 | Poverty	| Poverty Status by Age
| B19025_001E	 | Income (Households and Families) | Aggregate household income in the past 12 months (in 2016 inflation-adjusted dollars)
| B23025_002E	 | Employment Status; Work Experience; Labor Force	|	Employment status for the labor force population 16 years and over.
| B16008_019E	 | Language Spoken at Home and Ability to Speak English | Citizenship status by age by language spoken at home and ability to speak English for the population 5 years and over.
| B09002_015E	 | Children; Household Relationship	|	Female householder, no husband present with children under 18 years.


#### Crime Occurrences

#### Building Permits
