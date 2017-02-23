# Housing Insights
> Bringing open data to affordable housing decision makers

Welcome! If you're just arriving at this project, we recommend you check out our info website for a project summary and the [getting started 'Resources' section](http://housinginsights.org/resources/) for new contributors to the project.

If you're already up to speed and are ready to start contributing, read on for installation and setup instructions.

# Project Folder Structure
**Note** some of this stated structure is not yet merged into the Master branch (should be merged by 2/20)
`\docs`
A Jekyll-based static website that is used as a project informational page while developing the project.

`\javascript`
Code for our front-end tool. Currently not in \master, but we are mid-refactor.

`\data` 
This is not synced to Github, but it is where you can download the raw data if you are working on a ticket that needs that. 

`\python`
Folder for Python scripts used for processing data sources. Output of the any scripts should be directed to the \insights-site\data folder. In production, this data will be uploaded to CKAN.

`\mockups`
Store any brainstorming, images, pictures of napkin drawings, or other ideas for implementation here. "Live mockups" during the prototype phase, i.e. code-based mockups, can typically go directly into the insights-site folder instead.

# Basic Workflow Concept
This is very much a work in progress so any suggestions to clean up or change this approach are welcome! Currently we are planning to use a static website approach to the final product, unless it becomes necessary to have a server back end. There is a fundamental separation between processing scripts (which perform one-time analysis) and the live site (which uses output of this analysis).

1. Any tabular data sources that need to be analyzed should be loaded into our PostgreSQL server on Amazon, so that they are easily accessible to all users without having to re-download or process them.
2. Python code (or plain SQL if necessary) should perform all data upload and analysis queries, so that ingestion scripts can be re-run any time they are needed.
3. Final analysis scripts should output flat files (JSON or CSV) that can be used by the Javascript.

# Setting up your local environment
The local environment setup you need depends on which part of the project you want to contribute to:

* Everyone needs Git
* Front-end work just needs some sort of local static file server. We recommend the Python `http.server` but any other alternative will work, including Jekyll.
* Data processing scripts need Python3, preferably via Anaconda.
* Our data is loaded into an Amazon RDS database, so if you want to do manual SQL or if you want to run scripts that connect to it you'll need the log in credentials.
* The informational website (`/docs`) requires Jekyll.

## Git
Start by forking the repo, and cloning your fork to your local machine. Follow the instructions on our [CONTRIBUTING.md](https://github.com/codefordc/housing-insights/blob/master/CONTRIBUTING.md) page (and read our conventions if you haven't yet).

**New to Git?**
You'll definitely need Git on your computer.

* Download [Git](https://git-scm.com/downloads)

If you're new to using Git, we also recommend getting a [GUI client](https://git-scm.com/downloads/guis). Consider GitX-dev or Fork for Mac, Git Extensions for Windows, or SourceTree for either. And, you'll want to read up on some [Git resources](http://codefordc.org/resources/getting-started.html) and practice pulling, pushing, and making a pull request.

## Javascript
If you're just contributing to the front end of our web tool, all you'll need is a simple web server.
* Install Miniconda (or Anaconda) - links below.
* Open a command prompt, and `> cd \path\to\your\repocopy\insights-site`
* `> python -m http.server`
* Open a browser at the path listed (probably `http://localhost:8000/`)

## Data processing code in `\python`
This project uses Python 3 (3.5.2 specifically). If you don't have Python 3 installed already, we recommend using the Anaconda distribution.

* Download [Miniconda](http://conda.pydata.org/miniconda.html). This is the best choice if you are at a Code for DC Hacknight and have limited bandwidth.
* OR download [Anaconda](https://www.continuum.io/downloads). Has lots of extra commonly used Python packages. Select the Python 3.5 version.


## Amazon RDS Database

* Server: housing-insights-raw.ccmqak7fm8oa.us-east-1.rds.amazonaws.com
* Port: 5432
* Ask Neal for login credentials

## Informational Website (`/docs`)
Jekyll is a static website templating engine. This means you can have a simple, static website but still get the benefits of reusing your HTML code on different pages of a website. It also powers Github Pages, where we host our info site.
* Follow the install instructions for your operating system on the [Jekyll website](https://jekyllrb.com/docs/installation/). Note, we don't currently use CoffeeScript so NodeJS is unnecessary.
* Open a command line and `> cd \path\to\housing-insights\docs`
* Run `> jekyll serve`
* Open a browser at the path listed (probably `http://localhost:4000`)
