---
layout: main
title: H.I. Onboarding
---

# Connecting to the Amazon RDS Database


If you want to edit the code that creates our database, or add to our documentation, or add new data sources you'll want to [use Docker instead]({{site.baseurl}}/resources/onboarding/docker.html). If you just have slow internet, it can also be better to make a local copy of the database. But, if you just want to get up quickly and do some analysis of the data we've already ingested, you can use any database client to connect to our Amazon database directly. 


## Database Client

This is where you enter SQL commands and view results. We recommend [Valentina Studio](https://valentina-db.com/en/get-free-valentina-studio) if you don't have a preferred database client (warning - slow download), although [pgAdmin](https://www.pgadmin.org/) is another very common choice for working with Postgres. Here's a [comprehensive list](http://wiki.postgresql.org/wiki/Community_Guide_to_PostgreSQL_GUI_Tools) of other choices. 



### Make a new connection

On Valentina, select 'File->Connect to'. On pgAdmin, select the power plug symbol. Fill in this info:

* Host: housing-insights.cozfxhwzlequ.us-east-1.rds.amazonaws.com
* Port: 5432
* User: contact the management team
* Password: contact the management team
* Database: housing_insights

