---
layout: datasource
tablename: project
title: Affordable Housing Inventory
---

The Housing Insights database aims to capture a complete inventory of all the subsidized affordable housing available in DC. The data sources that we are using include:

1) The Preservation Catalog
2) DC's Open Data data set of affordable housing properties
3) The Quickbase Database maintained by the Department of Housing and Community Development (DHCD)

In the future, the following additional data sources might also be useful to include:

4) The [Housing Production Trust Fund annual report](https://dhcd.dc.gov/node/1203770) includes information such as building name, address, funding level, total project funding amount, etc.  Recent buildings (definitely post 2015 and mostly 2011 and later) are available from DHCD's quickbase API.  It may be worthwhile to scrape the PDF versions of HPTF annual reports for earlier years if needed, and ideally, to cross-reference the PDF data with DHCD's database in order to look for inconsistencies and add additional data as needed.
5) PUD history from the office of zoning - the Affordable Housing Data Set from opendata.dc.gov reportedly includes most inclusionary zoning units. It is only missing those that are part of the [Affordable Dwelling Units program](https://dhcd.dc.gov/service/affordable-dwelling-units), because ADU units typically went through the PUD process outside of the inclusionary zoning program (according to the Office of the Deputy Mayor for Planning and Economic Development). That said, individual Planned Unit Development applications often include details about the quantity and type of affordable units being included in each PUD.  Further analysis would be required in order to determine whether affordable housing details extracted from PUD applications might contain any additional relevant data that is **not** already included in the Affordable Housing Dataset.
6) Although the Affordable Housing Data Set on opendata.dc.gov reflects most inclusionary zoning units from 2015 to the present, the Deputy Mayor for Planning and Economic Development also has historical data on inclusionary zoning projects prior to 2015.  DMPED previously indicated it might be possible to obtain a one-time pull of that historical data.
7) DHCD may have additional historical data on older buildings not currently included in their Quickbase database (which only includes data starting in October 2010)
8) It may be possible to obtain additional data via direct request to the DC Housing Finance Agency (DCHFA) as well as to the DC Housing Authority (DCHA)


## Preservation Catalog
Compiles all the federal programs, with sporadic additions of older DC-funded buildings


## DC's Open Data Affordable Housing Dataset
DMPED manages a Quickbase database that pulls from the DMPED, DHCD, DCHFA and DCHA data (some from APIs, and some from manual sources). They've put that data from the affordable housing database onto opendata.dc.gov

Some notes on the Affordable Housing data source opendata.dc.gov dataset scope:

* Includes all units from the DMPED, DHCD, DCHFA and DCHA lists since 2015
* Includes Inclusionary Zoning units since 2015
* Does not include units from the ADU program. These are typically units that went through PUD process outside of the IZ prorgam.
* Fields include address and # of affordable units.
* Unit breakdown by AMI requirement is not included, but DMPED can probably have this added to the opendata.dc.gov data.
* Loan amount information is not included. DHCD does publish this through their Quickbase api but if we want this for buildings in other agencies we'd need to investigate.
* DMPED updates the master database monthly, and opendata.dc.gov gets a pull monthly, so it will probably be between 1 and 2 months behind.


## DHCD's Quickbase Database

This database is connected to DHCD's internal record keeping; however, per DHCD's admission it is an incomplete account of buildings they have funded. Per DHCD it should contain all post 2015 buildings, about "80% of buildings they worked on 2013-2015, 50% of those from 2011-2013, and sporadic before that."