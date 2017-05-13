---
layout: main
title: H.I. Onboarding
---

# Running our website and database locally with Docker

If you are adding new data sources or writing code for our API, we want you to do this with your own local copy of the database instead of the live server used by our website. This means you need several pieces of software installed on your computer to be able to do this:

* Postgres is the software that runs our database

* A database client lets you view the data in the database, and write SQL queries

* Jekyll is the software used to build our website. If you are adding new data sets, you need to be able to write documentation about those data sources on our website. 

* Python runs the code that adds data to our database and that powers our API. You need a virtual environment with both the right version (3.5) of Python installed as well as the necessary packages we use (Flask, others). 

Since installing each of these pieces of software and configuring their settings to talk to each other can be difficult on different computers, Docker provides a way for us to do the configuration once and then you can run our pre-configured combination. Docker creates a virtual machine - this is a virtual computer running Linux, so any software you run in the virtual machine thinks it has been installed on a Linux computer that is configured exactly the same as the one we used to make the setup files. While there are sometimes issues setting up Docker, once you have it installed properly you can use a Docker image to set up any software you want. 

We currently use Docker for the first 3 items - Postgres, pgWeb (a database client), and Jekyll. We would like to soon include Python inside Docker but [currently have a problem](https://github.com/codefordc/housing-insights/issues/183) with the setup (if you are good at Docker we'd love your help fixing this!). For Python, we use a virtual environment instead. 

If you have problems installing or setting up Docker, you can also configure Postgres, Jekyll, and a database client independently - ask for help if this is the case. 


### Secrets.json

This file stores configuration information, such as the url and password to our database. `secrets.json` is in our .gitignore file so is not included with the code when you cloned our Github repository. You can easily make your own version of the file, though:

* In the project repository, navigate to `/housing-insights/python/housinginsights` 
* make a copy of the file `secrets.example.json`. 
* Rename this copy to `secrets.json`. 

This version only includes connection information for a local copy of the database. Later you may need the real version (for example, if you are updating our production server). Ask a project lead when you run into issues. 

## 1) Running Docker

### 1a) One time setup

Start by installing [Docker Toolbox](https://www.docker.com/products/docker-toolbox). If you've used Docker before and already have any version of Docker working, you can use that - Docker Toolbox is the easiest to use the first time (especially on Windows). 

After it's installed, run the Docker Quickstart Terminal. Once this is open and running, you'll have a command prompt. Run this command:

```
$docker-machine ip
```

This will print the IP address of your local Docker instance. Open up `/python/housinginsights/secrets.json` and make sure you have a couple lines like this:

```
    "docker_database": {
        "connect_str": "postgresql://codefordc:codefordc@192.168.99.100:5432/housinginsights_docker"
    },
```

Substitute your IP address for the one that says `192.168.99.100` in this example (but keep `:5432` at the end).

**Troubleshooting note**: If you already have Postgres installed on your machine, it may be using the 5432 port. If you get an error message saying something related to a port in use, you'll need to change the port both here AND in the docker-compose.yml file. 

### 1b) Day-to-day use

When you start each work session, navigate into wherever you keep your housing-insights repository. The current directory should appear just above the `$` in the Quickstart Terminal. You'll need to use these standard Unix command line commands to get to the right place:

```
cd ..         //move up a level
cd myfolder   //move down a level into "myfolder"
ls            //lists all files and folders in your current directory
```

In your housing-insights repository folder, run this command:

```
docker-compose up
```
Leave this window **open and running** while you're working

Once it starts up (might take a moment), you can go to these web addresses:

* `<yourip>:8081`: a web-based Postgres SQL client that lets you run commands on the database, much like pgAdmin or any other database client. 
* `<yourip>:4000`: a local copy of our website, housinginsights.org. If you edit any file in the housing-insights/docs folder and save it, the website will be regenerated and you can see the changes when you reload the page. 
* `<yourip>:5432`: This one does not work in a browser, but you can use this IP address and port to connect to your local Docker database via your preferred SQL client ([Valentina Studio](https://valentina-db.com/en/get-free-valentina-studio) is a good one). This can sometimes be easier to use than the web version at 8081. 

You can press `ctrl+c` or `command+c` at any time to end the process. Give it about 10 seconds to shut down, if it hasn't shut down yet you can hit `ctrl+c` again to force it. 

## 2) Add data to your local database copy

If you've got Docker running, you should be able to see your database in the web browser at port `8081`. But there's nothing there! 

### 2a) One time setup

1) Make sure you have Python installed (we're currently using Python 3.5). We recommend [Miniconda](https://conda.io/miniconda.html). Select the Python 3.6 version - you can use Miniconda to install any other Python version. 

2) Open a regular command line (not Docker) and navigate to `path\to\housing-insights\python`. 

3) Run `conda env create`. This will create a virtual environment using the `environment.yml` file. (If you're not using Anaconda/Miniconda, we try to keep both requirements.txt and environment.yml in sync, but let us know if you have any problems)


### 2b) Regular use
**Open a regular command prompt in a new window/tab** (the command prompt from 1b) should still be running in the background).

Any time you need to recreate the database:

1) Make sure you're using the virtual environment: `activate housing-insights`

2) Navigate to `path\to\housing-insights\python\scripts`

3) On the command line, run `python load_data.py docker rebuild sample`. This will use the docker version of the database (frome secrets.json), first delete any data in the repository, and then re-load a set of sample data into the repository. If you want to rebuild the data with actual data (i.e. what is in manifest.csv instead of manifest.csv), run the same command without 'sample' at the end. 
