---
layout: datasource
tablename: project
title: Affordable Housing Inventory
---

The Housing Insights database aims to capture a complete inventory of all the subsidized affordable housing available in DC. The data sources that we are using include:

1) The Preservation Catalog
2) DC's Open Data data set of affordable housing properties
3) DHCD's Quickbase Database

We would also like to cross reference these with additional data sets (this work is pending)

4) The Housing Production Trust Fund annual report (PDF) (current status [on Github](https://github.com/codefordc/housing-insights/issues/77))
5) PUD history from the office of zoning (current status of this work [on Github](https://github.com/codefordc/housing-insights/issues/90))
6) One-time pull of DMPED funded projects from pre-2015 (discuss with Marie Whittaker)
7) Records request from DHCD for older buildings not currently included in the database
8) Records request from DCHFA and DCHA


## Preservation Catalog
Compiles all the federal programs, with sporadic additions of older DC-funded buildings

## DC's Open Data Affordable Housing Dataset
DMPED manages a Quickbase database that pulls from the DMPED, DHCD, DCHFA and DCHA data (some from the APIs mentioned in this ticket and #136, some from manual sources). They've put that data from the affordable housing database onto opendata.dc.gov

Some notes on the Affordable Housing data source opendata.dc.gov dataset scope:

* Includes All units from the DMPED, DHCD, DCHFA and DCHA lists since 2015
* Includes Inclusionary Zoning units since 2015
* Does not include units from the ADU program. These are typically units that went through PUD process outside of the IZ prorgam.
* Fields include address and # of affordable units.
* Unit breakdown by AMI requirement is not included, but @mseew says she can probably have this added to the opendata.dc.gov data.
* Loan amount information is not included. DHCD does publish this through their Quickbase api but if we want this for buildings in other agencies we'd need to investigate.
* DMPED updates the master database monthly, and opendata.dc.gov gets a pull monthly, so it will probably be between 1 and 2 months behind.

## DHCD's Quickbase Database

This database is connected to DHCD's internal record keeping; however, per DHCD's admission it is an incomplete account of buildings they have funded. Per DHCD it should contain all post 2015 buildings, about "80% of buildings they worked on 2013-2015, 50% of those from 2011-2013, and sporadic before that." In addition, the DC Auditor has noted that the records DHCD does keep are unreliable description of available affordable units, due to lack of enforcement with recipients of Housing Production Trust Fund money. The auditor's report is [available here](http://www.dcauditor.org/HPTF).