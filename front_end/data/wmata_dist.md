---
layout: datasource
tablename: wmata_dist
title: Washington Metropolitan Area Transit Authority Stops Within a Half Mile Walk
---

The wmata_dist table tells how far it is to walk from an affordable housing project to nearby transit stops. 

A record is created for each stop within 0.5 miles for each building. 

Walking distance is provided by the Mapbox API, buildings are from the projects table and transit stops are from the wmata_info table. 