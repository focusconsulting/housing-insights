# Housing Insights
> Bringing open data to affordable housing decision makers.

Welcome! If you're just arriving at this project, we recommend you check out our [onboarding page on our website](http://housinginsights.org/resources/onboarding) for new contributors to the project.


# Project Folder Structure
`front_end/`
A Jekyll-based static website that is used as a project informational page while developing the project.

`back_end/`
A python application that collects and transforms raw data, loads data into a database, and runs an API for the front end to access data.

# Basic Workflow Concept
This is very much a work in progress so any suggestions to clean up or change this approach are welcome!

1. Any tabular data sources that need to be analyzed should be loaded into our PostgreSQL server on Amazon, so that they are easily accessible to all users without having to re-download or process them.
2. Python code should perform all data upload and analysis queries, so that ingestion scripts can be re-run any time they are needed.
3. Our server will provide an API that our front end website can access. 

# Setting up your local environment

Check out our [onboarding page on our website](http://housinginsights.org/resources/onboarding) for information on setting up your local dev environment. We use Docker to provide a consistent approach. If you're working on the front end website, we have not yet set up a Docker image to serve the website - ask a front end team member or project lead for help setting up your local environment. 


## Coding and Workflow conventions

## Git conventions
We use a fork-and-pull request method, which should be familiar to most people who have contributed to an open source project before.

For info on setting up Git to work with a triangular workflow, follow [these configuration instructions](http://housinginsights.org/resources/onboarding/triangular-git.html). If you need more help, ask a project lead. 


### Branching
We use a loose [git flow](https://datasift.github.io/gitflow/IntroducingGitFlow.html) model. This means:

* `dev` is the best place to look for the most recent (but maybe incomplete) code.
* Before starting work, you should usually update and checkout `dev` first, and then make your own feature branch (e.g. `3-modal-fixes`)
* It will make us very happy if you start your branch name with the Github issue number  &#x263A;
* All pull requests should go into `dev`
* `master` always matches what is on our live website, and is tagged with version numbers.

If you know how to do that sort of thing, squashed and rebased pull requests bring great joy to our repo history! If you don't know what that means, it's not necessary and is best to learn only when you are confident in your Git skills.

## License
This project is published under an [MIT license](https://github.com/codefordc/housing-insights/blob/master/LICENSE.txt). By contributing code to this repo you are agreeing to make your work available to the public under the terms of this license.
