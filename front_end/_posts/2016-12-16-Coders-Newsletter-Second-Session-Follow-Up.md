---
layout: blog_post
title: Second Design Session Follow Up
author: Neal
permalink: /blog/:year/:month/:day/:title/
---
Hey Housing Insights team!

Thanks for everyone that came last night! All the sketches from last night have been scanned and I've put them in the '/mockups' folder in our Github repo. You can view them [on the Github website](https://github.com/codefordc/housing-insights/tree/dev/mockups/early-stage%20ideation) (the dec15-hacknight.pdf file is the file with all of last nights ideas.

As I said last night, our next step is to sift through these ideas, and turn them into a clear plan of what to build for our first prototype. Based on the Doodle poll, we will do this at a design session** on Tuesday, Dec. 20, 6:30-9:00 **at the [NY Code and Design Academy](https://goo.gl/maps/N5PUTw1bVLF2) (*tentatively confirmed). For ongoing work in the month of January, I'm proposing splitting the group into 4 teams (see descriptions below).

**How you can participate:**

**1)** [**Most important] **Tell me whether or not you plan to come on Tuesday. At the same time, tell me which team(s) you are interested in joining. **Take 1 minute to fill in your preferences [on this sheet](https://docs.google.com/spreadsheets/d/1gjOu2WRdGH-FiJ1u8GBRLVJo118hnfiH8SGT9fD3mVI/edit?usp=sharing). **

**More stuff: **

**2) **Draw more one-page design ideas before our Tuesday meeting, like the ones we did last night. Scan them or take a picture and add them to [this Github issue](https://github.com/codefordc/housing-insights/issues/42).

**3)** Explore our data. 

- Salomone put together this [data dictionary](https://github.com/codefordc/housing-insights/issues/38) of the sources we have collected so far (just a subset of the ones we want to include)
- You can connect to the data via postgres:
    - Server: [housing-insights-raw.ccmqak7fm8oa.us-east-1.rds.amazonaws.com](http://housing-insights-raw.ccmqak7fm8oa.us-east-1.rds.amazonaws.com/)
    - Port: 5432  

    - username: housingcrud
    - password: CrudRules

> > Don't know how to use this? We can help you get set up next time. Also, please don't drop our tables :)

Thanks! I hope to see many of you on Tuesday; if you can't make it or just want to wait to see the plan, I'll be in touch re: teams before the new year.


---------------------
**Prototype Team:**

We'll use Google Slides and Tableau to make a fake (but real-looking) version of our proposed design, or potentially 2-3 different versions. We'll show this to some affordable housing users and watch their interactions with it. 

**General Data Team:**

Responsible for wrangling and locating our data sources, making sure we can link them, and writing Python / SQL code to analyze them. Also can do some data exploration to find interesting stories. 

**Location Data Team:**

Writing code to do spatial-analysis related data. For example, this team would start working on putting affordable buildings on a map and calculating the distance to public transit, or find the other buildings within X miles. Most likely will do this client-side via [Mapbox GL JS](https://www.mapbox.com/mapbox-gl-js/api/) and the [Directions API](https://www.mapbox.com/api-documentation/#retrieve-directions) (open to alternatives), but could also use [Python SDK](https://github.com/mapbox/mapbox-sdk-py) if it makes sense.

**Javascript/D3 Team: **

Setting up the core structure of our main page code. For now this will focus on the nuts-and-bolts part of the project that we will use no matter what the design, learning about [using D3](https://d3js.org/), and how we connect to our data. 