# Housing Insights
> Bringing open data to affordable housing stakeholders. 

This repository contains code for both [housinginsights.org](http://housinginsights.org) and the AWS hosted API that feeds it. It is divided into two sections.

1. `front_end/`: A Jekyll-based static website that holds legacy information and front end code for the project.
2. `back_end/`: A python Flask application that collects and transforms raw data, loads data into a database, and runs an API for the front end to access data.

Overall, the `back_end` directory hass a Flask application that sends data to and from a Postgres database as seen below. See the README file in either for specific information about that portion of the project. 

![](front_end/assets/tech-stack.png)

# Setting up your local environment
This project uses `Docker` and `docker-compose` to create a consistent environment for development and deployment.
The [onboarding page of housinginsights](http://housinginsights.org/resources/onboarding) has detailed information on setting up the appropriate environment.
There is currently no Docker image for the front end of the website - ask a front end team member or project lead for help setting up your local environment. 

## License
This project is published under an [MIT license](https://github.com/codefordc/housing-insights/blob/master/LICENSE.txt).
By contributing code to this repo you are agreeing to make your work available to the public under the terms of this license.
