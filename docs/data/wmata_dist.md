---
layout: datasource
tablename: example_table_name
title: Example Table
---
<!--No need to put a header; the title in the front matter (above) will be used as a header-->

The wmata_dist table tells how far it is to walk from an affordable housing project to nearby transit stops. A record is created for each stop within 0.5 miles for each building. Walking distance is provided by the Mapbox API, buildings are from the projects table and transit stops are from the wmata_info table. 