---
layout: main
title: Summary
---

# Project Summary
We want to help DC government officials and affordable housing advocates better spend the time and money available for affordable housing preservation. We will do this by providing better access to data and analysis for both the current affordable buildings and the neighborhoods they are part of.

## What is Affordable Housing Preservation?
Beginning in the 1970's, most affordable housing is owned privately. Both the federal and DC government provide subsidies to these owners in exchange for offering reduced rents to eligible low income residents. These subsidies take different forms depending on the building, but they can be direct rent subsidies, long-term low interest loans, or tax credits. Buildings last a long time, so even if a particular program has been ended existing contracts are still active.

Private owners can choose to either renew their contracts or stop participating (usually when contracts expire). If they stop participating, DC loses affordable housing that low income tenants need; often when the property was participating in an expired program the subsidy money cannot be redirected elsewhere and there is less funding available for supporting affordable housing.

Affordable Housing Preservation is the process of getting these owners to continue participation in these programs to keep units available to low income tenants. Usually this is done by refinancing and rehabing the property as a way to renew the incentives, or by legal action. DC renters get the right of first refusal through the [Tenant Opportunity to Purchase Act (TOPA)](http://dc.urbanturf.com/articles/blog/first-timer_primer_what_is_the_right_of_first_refusal/7484), or the DC government can purchase it on their behalf with the [District Opportunity to Purchase Act (DOPA)](http://dhcd.dc.gov/sites/default/files/dc/sites/dhcd/publication/attachments/2016%20DOPA%20Guideline-Fact%20Sheet.pdf). The DC Government has allocated [over $100M per year](https://wamu.org/news/16/10/13/bowser_says_100_million_for_affordable_housing_is_historic_but_is_it_enough) to spend on affordable housing, including preservation, as well as other government agencies like the [DC Housing Finance Agency (HFA)](http://www.dchfa.org/DCHFAHome/Developers/ProgramDescriptions/MortgageRevenueBonds/tabid/134/Default.aspx).

It's important to also note that one building can participate in multiple programs, making complete data on DC's affordable housing challenging.

[Read descriptions of some of the primary federal incentive programs](http://www.preservationdatabase.org/programdesc.php).

## What is Our Approach?
We're building a web tool that lets decision makers better understand affordable housing properties in DC. The core data source is a list of all subsidized affordable properties, the [Preservation Catalog](http://www.neighborhoodinfodc.org/dcpreservationcatalog). This database also contains information about the buildings themselves and the contracts the provide them subsidies.

We'll connect this to new data sources, primarily public data sets provided by DC government, that give us more information about the buildings themselves as well as the neighborhoods that they are part of. We will perform analysis on these merged data sets both at the building level and the city level to improve decision makers understanding of the factors influencing housing preservation.

Each data source can inform decision makers by indicating its 1) *risk of loss*, indicate its particular 2) *value to the community and residents* and 3) the *cost or effort to preserve*.

### Risk of loss
Some attributes that indicate a high risk of loss include:

* expiring subsidy contract (e.g. Section 8 contract or end of mortgage term).
* 15-year anniversary of a Low Income Housing Tax Credit property (LIHTC).
* Ratio of net rent (subsidized rent) to the neighborhood market rent.
* Ownership type (non-profit vs. for profit owner).
* Upcoming nearby neighborhood investment, potentially indicated by neighborhood building permits.
* Poorly maintained properties.

A [companion project](https://github.com/georgetown-analytics/housing-risk) is being conducted by students in the Georegetown Data Science Graduate Certificate program. Results from this project, in the form of a 'risk of loss' score, will be available for use by this project in January 2017.

### Value to community and residents
Some attributes that are indicate whether a property might be considered higher or lower priority include:

* Federally subsidized with a non-transferrable source (e.g. property based Section 8 subsidy).
* Serves very low income residents, indicated as % of Area Mean Income (AMI) and deduced either from subsidy type (different programs have different AMI requirements) or property data.
* Serves vulnerable populations, e.g. elderly, disabled, minority or others that may have greater difficulty finding replacement housing.
* Needed to maintain economic diversity, for instance if there are few remaining affordable properties in a neighborhood.
* Near DC funded economic development projects.
* Near transit.

### Cost or effort to preserve
This is generally more difficult to quantify, but some available indicators are:

* Large unit count (it is often just as much work to preserve a small building as a large one)
* Lower ratio between net rent and neighborhood market rent (may indicate that the increased subsidy is less)
* Existing tenant association
