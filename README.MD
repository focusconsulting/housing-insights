# Housing Insights
> Bringing open data to affordable housing decision makers

Welcome! If you're just arriving at this project, we recommend you check out our [onboarding page on our website](http://housinginsights.org/resources/onboarding) for new contributors to the project.


# Project Folder Structure
`\docs`
A Jekyll-based static website that is used as a project informational page while developing the project.

`\javascript`
Code for our front-end tool.

`\data` 
This is not synced to Github, but it is where you can download the raw data if you are working on a ticket that needs that. Use the [AWS CLI sync instructions]({{site.baseurl}}/resources/aws-sync.html) for how to get this data.

`\python`
Folder for Python scripts used for processing data sources.

`\python\scripts`
The code that is actually executed to do things like download data, rebuild the database, etc. These scripts should contain very little code, instead leveraging our package.

`\python\housinginsights`
Our python package, which contains all the object-oriented code used by our data ingestion pipeline. 

`\mockups`
Store any brainstorming, images, pictures of napkin drawings, or other ideas for implementation here. "Live mockups" during the prototype phase, i.e. code-based mockups, can typically go directly into the insights-site folder instead.

# Basic Workflow Concept
This is very much a work in progress so any suggestions to clean up or change this approach are welcome!

1. Any tabular data sources that need to be analyzed should be loaded into our PostgreSQL server on Amazon, so that they are easily accessible to all users without having to re-download or process them.
2. Python code should perform all data upload and analysis queries, so that ingestion scripts can be re-run any time they are needed.
3. Our server will provide an API that our front end website can access. 

# Setting up your local environment

Check out our [onboarding page on our website](http://housinginsights.org/resources/onboarding) for information on setting up your local dev environment. We use Docker to provide a consistent approach. If you're working on the front end website, we have not yet set up a Docker image to serve the website - ask a front end team member or project lead for help setting up your local environment. 
