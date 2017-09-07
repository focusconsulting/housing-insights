---
layout: datasource
tablename: census
title: U.S. Census American Community Survey Data
---

The [U.S. Census American Community Survey](https://www.census.gov/programs-surveys/acs/) provides useful data on rent that the Housing Insights project uses to create a meaningful estimate of 'market rent' for a given area, which in turn
is useful for understanding how the supply of affordable housing inventory in that area compares to the demand.  

Rent data is also useful for exploring whether or not rising rents in a given area may be an indicator that affordable housing inventory in that same area may be at a higher risk of loss, due to market 
pressures that might create increased incentives for landlords to sell their buildings, thereby jeopardizing existing subsidies for those properties.

<br>

## "Good Neighborhood" Variables  

ACS data is also useful for developing insight into neighborhood-level factors that are relevant to affordable housing preservation, beyond metrics related exclusively to rent.  

By way of example, recent research on the Moving to Opportunity program shows the results of a long term longitudinal study looking at the effect on children of living in better neighborhoods.
This section describes the census-derived variables used in the study to define a "good neighborhood", and the associated ACS5 2015 fields and transformations used to replicate (as closely as we can) those variables.

### Background on the Study  

- [Original paper, with table of variables at the very end](http://scholar.harvard.edu/files/hendren/files/nbhds_paper.pdf)
- [New York Times article describing the report](https://www.nytimes.com/2015/05/05/upshot/why-the-new-research-on-mobility-matters-an-economists-view.html?_r=0)

<br>

#### Fields from the U.S. Census's American Community Survey (ACS) Related to "Good Neighborhoods"  

Census uses code names (like B02001_003E) to uniquely designate specific data fields they provide. We note those field names here, along with a more descriptive title, so that users of Housing Insights can find Census documentation on those fields.

Except where noted, these fields refer to ACS data from 2009 through 2015.

|Name |Label |Concept |
|:---|:---|:---|
|[B02001_003E](http://api.census.gov/data/2015/acs5/variables/B02001_003E.json) | Black or African American alone | B02001. Race |
|[B17020_002E](http://api.census.gov/data/2015/acs5/variables/B17020_002E.json) |Income in the past 12 months below poverty level (*Note: 2013 - 2015 only)|B17020. Poverty Status in the Past 12 Months by Age|
|[B17001_002E](http://api.census.gov/data/2009/acs5/variables/B17001_002E.json) |Income in the past 12 months below poverty level (*Note: 2009 - 2012 only*) |B17001. Poverty Status in the past 12 Months by Sex by Age
|[B19025_001E](http://api.census.gov/data/2015/acs5/variables/B19025_001E.json) |Aggregate household income in the past 12 months (in 2015 Inflation-adjusted dollars) |B19025. Aggregate Household Income in the Past 12 Months (in 2015 Inflation-Adjusted Dollars) |
|[B23025_002E](http://api.census.gov/data/2015/acs5/variables/B23025_002E.json) |In labor force (*Note: 2011 - 2015 only*)|B23025. Employment Status for the Population 16 Years and Over |
|[B16008_019E](http://api.census.gov/data/2015/acs5/variables/B16008_019E.json) |Foreign-born population |B16008. Citizenship Status by Age by Language Spoken At Home and Ability to Speak English for the Population 5+ Yrs |
|[B09002_015E](http://api.census.gov/data/2015/acs5/variables/B09002_015E.json) |In other families:!!Female householder, no husband present |B09002. OWN CHILDREN UNDER 18 YEARS BY FAMILY TYPE AND AGE |

<br>

#### Housing Insights Fields Related to "Good Neighborhoods"  

The following fields on Housing Insights correspond to some of the key variables used in the Harvard study cited above to identify what is a "good" neighborhood.

Please note that the values in the "Calculation" column refers to U.S. Census ACS fields described above.  All of these fields are calculated as a fraction of the total population in the given geographic area, listed as: `B01003_001E`

|Name |Definition |Calculation|
|:---|:---|:---|
|Fraction Black | Number of individuals who are black alone divided by total population | `B02001_003E / B01003_001E` |
|Poverty Rate |Fraction of population below the poverty rate | `B17020_002E / B01003_001E` |
|Household Income per Capita |Aggregate household income in the 2000 census divided by the number of people aged 16-64 |`B19025_001E / B01003_001E` (2013 - 2015) OR `B17001_002E / B01003_001E` (2009 - 2012) |
|Labor Force Participation |Share of people at least 16 years old that are in the labor force |`B23025_002E / B01003_001E` (2011 - 2015)|
|Fraction Foreign Born |Share of CZ residents born outside the United States |`B16008_019E / B01003_001E` |
|Fraction of Single Mothers  |Number of single mothers divided by total population |`B09002_015E / B01003_001E` |
