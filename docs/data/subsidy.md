---
layout: datasource
tablename: subsidy
title: Subsidy
---

This table details all projects covered by each individual subsidy program represented in the data, and includes information related to the subsidizing agency, the number of units covered, and subsidy expiration dates.

Unlike the projects table which has a unique row per project (building), there is one row per subsidy, so the subsidy table can have multiple rows for the same project (project -> subsidy is one->many).

The records in this table were originally copied from the [DC Preservation Catalog](http://www.neighborhoodinfodc.org/dcpreservationcatalog/).  Information in the DC Preservation Catalog is drawn from HUD and other national and local administrative data sources, supplemented by personal observations of Preservation Network members.

> Because of delays in updating and reporting, these sources may not always reflect the current status of the property. While efforts are made to ensure its accuracy and completeness, the Catalog may not be comprehensive and is continually being updated and improved.

The Housing Insights project has augmented the original set of records obtained from the Preservation Catalog with additional subsidy data. Most notably, while the Preservation Catalog primarily reflects federal subsidy programs, the subsidy data in this table also includes subsidies funded by the DC Government, as reported via [opendata.dc.gov](http://opendata.dc.gov/datasets/34ae3d3c9752434a8c03aca5deb550eb_62).

> As with data in the Preservation Catalog, because of delays in updating and reporting, these sources may not always reflect the current status of the property, and this table is continually being updated and improved.

## DC's Open Data Affordable Housing Dataset
DMPED manages a Quickbase database that pulls from the DMPED, DHCD, DCHFA and DCHA data (some from the APIs mentioned in this ticket and #136, some from manual sources). They've put that data from the affordable housing database onto opendata.dc.gov

To manage partially overlapping information, if the project existed in the database a new record was not created. Then, if the subsidy table, every time that a project shows up in a new data source, we add a new subsidy record. These are not deduplicated. We bias toward what the data sources say.

Some notes on the Affordable Housing data source opendata.dc.gov dataset scope:

* Includes All units from the DMPED, DHCD, DCHFA and DCHA lists since 2015.
* Includes Inclusionary Zoning units since 2015.
* Does not include units from the ADU program. These are typically units that went through PUD process outside of the IZ prorgam.
* Fields include the address and number of affordable units.
* DMPED updates the master database monthly, and opendata.dc.gov gets a pull monthly, so it will probably be between 1 and 2 months behind.

## Remaining Issues

* Continue augmenting the table with additional data for DC subsidy programs (e.g. unit breakdown by AMI requirement, loan amount information, etc).
* Find data sources for individual buildings and their AMI requirements.
* Write summary of federal and local subsidy programs and rules.
* All of the same issues with regard to project timelines are an issue, e.g. pre-2015 data inconsistencies.
