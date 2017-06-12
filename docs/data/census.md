---
layout: datasource
tablename:
title: Census
---
<!--Need content on census data overall-->



## "Good Neighborhood" Variables
Recent research on the Moving to Opportunity program shows the results of a long term longitudinal study looking at the effect on children of living in better neighborhoods.  This section describes the census-derived variables used in the study to define a "good neighborhood", and the associated ACS5 2015 fields and transformations used to replicate (as closely as we can) those variables.

*Note, as of this writing, only 6 of the variables from the original study are implemented.*

### Background on the Study
- [Original paper, with table of variables at the very end](http://scholar.harvard.edu/files/hendren/files/nbhds_paper.pdf)
- [New York Times article describing the report](https://www.nytimes.com/2015/05/05/upshot/why-the-new-research-on-mobility-matters-an-economists-view.html?_r=0)

#### Census-Derived Variables (from original paper):

|Variable |Definition |Source |
|:---|:---|:---|
|Fraction Black |Number of individuals who are black alone divided by total population |2000 Census SF1 100% Data Table P008 |
|Poverty Rate |Fraction of population below the poverty rate |2000 Census SF3 Sample Data Table P087 |
|Racial Segregation |Multi-group Theil Index calculated at the census-tract level over four groups: White alone, Black alone, Hispanic, and Other |2000 Census SF1 100% Data Table P008|
|Income Segregation |Rank-Order index estimated at the census-tract level using equation (13) in Reardon (2011) the δ vector is given in Appendix A4 of Reardon's paper. H(pk) is computed for each of the income brackets given in the 2000 census. See Appendix D for further details. |2000 Census SF3 Sample Data Table P052|
|Segregation of Poverty (<p25) |H(p25) estimated following Reardon (2011); we compute H(p) for 16 income groups defined by the 2000 census. We estimate H(p25) using a fourth-order polynomial of the weighted linear regression in equation (12) of Reardon (2011). |2000 Census SF3 Sample Data Table P052 |
|Segregation of Affluence (>p75) |Same definition as segregation of poverty, but using p75 instead of p25 |2000 Census SF3 Sample Data Table P052 |
|Fraction with Commute < 15 Mins |Number of workers that commute less than 15 minutes to work divided by total number of workers. Sample restricts to workers that are 16 or older and not working at home. |2000 Census SF3 Sample Data Table P031|
|Logarithm of Population Density |Logarithm of the Population Density where the Population Density is defined as the Population divided by the Land Area in square miles. |2000 Census Gazetteer Files|
|Household Income per Capita |Aggregate household income in the 2000 census divided by the number of people aged 16-64 |2000 Census SF3 Sample Data Table P054|
|Labor Force Participation |Share of people at least 16 years old that are in the labor force |2000 Census SF3 Sample Data Table P043|
|Share Working in Manufacturing |Share of employed persons 16 and older working in manufacturing. |2000 Census SF3 Sample Data Table P049|
|Fraction Foreign Born |Share of CZ residents born outside the United States |2000 Census SF3 Sample Data Table P021|
|Fraction of Single Mothers |Number of single female households with children divided by total number of households with children |2000 Census SF3 Sample Data Table P015 |
|Fraction of Adults Divorced |Fraction of people 15 or older who are divorced |2000 Census SF3 Sample Data Table P018|
|Fraction of Adults Married |Fraction of people 15 or older who are married and not separated |2000 Census SF3 Sample Data Table P018|
|Median Monthly Rent |Median "Contract Rent" (monthly) for the universe of renter-occupied housing |2000 Census SF3a (NHGIS SF3a, code: GBG) units paying cash rent |
|Median House Price |Median value of housing units at the county level (population weighted to CZ level for CZ covariate). |2000 Census SF3a (NHGIS SF3a, code: GB7) |

#### ACS5 2015 API Field Names

|Name |Label |Concept |
|:---|:---|:---|
|[B02001_003E](http://api.census.gov/data/2015/acs5/variables/B02001_003E.json) | Black or African American alone | B02001. Race |
|[B17020_002E](http://api.census.gov/data/2015/acs5/variables/B17020_002E.json) |Income in the past 12 months below poverty level |B17020. Poverty Status in the Past 12 Months by Age|
|[B19025_001E](http://api.census.gov/data/2015/acs5/variables/B19025_001E.json) |Aggregate household income in the past 12 months (in 2015 Inflation-adjusted dollars) |B19025. Aggregate Household Income in the Past 12 Months (in 2015 Inflation-Adjusted Dollars) |
|[B23025_002E](http://api.census.gov/data/2015/acs5/variables/B23025_002E.json) |In labor force |B23025. Employment Status for the Population 16 Years and Over |
|[B16008_019E](http://api.census.gov/data/2015/acs5/variables/B16008_019E.json) |Foreign-born population |B16008. Citizenship Status by Age by Language Spoken At Home and Ability to Speak English for the Population 5+ Yrs |
|[B09002_015E](http://api.census.gov/data/2015/acs5/variables/B09002_015E.json) |In other families:!!Female householder, no husband present |B09002. OWN CHILDREN UNDER 18 YEARS BY FAMILY TYPE AND AGE |

#### Calculated Good Neighborhood Variables
**Notes:**
- Pseudocode includes API field names per above.
- All variables are fractions of the total population: B01003_001E
- All calculations are at the appropriate geographic level (with associated API or code wrappers)

|Name |Definition |Pseudocode|
|:---|:---|:---|
|Fraction Black | Number of individuals who are black alone divided by total population | `fract_black = B02001_003E / B01003_001E` |
|Poverty Rate |Fraction of population below the poverty rate | `fract_below_pov = B17020_002E / B01003_001E` |
|Household Income per Capita |Aggregate household income in the 2000 census divided by the number of people aged 16-64 |`household_inc_percap = B19025_001E / B01003_001E` |
|Labor Force Participation |Share of people at least 16 years old that are in the labor force |`labor_part_rate = B23025_002E / B01003_001E`|
|Fraction Foreign Born |Share of CZ residents born outside the United States |`fract_foreign_born = B16008_019E / B01003_001E` |
|Fraction of Single Mothers *(replaces original Fraction of Children with Single Mothers)* |Number of single mothers divided by total population |`fract_single_mom = B09002_015E / B01003_001E` |
