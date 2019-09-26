---
layout: main
title: H.I. Onboarding - Docker
---

# Running our website and database locally with Docker

If you are adding new data sources or writing code for our API, we want you to do this with your own local copy of the database instead of the live server used by our website. This means you need several pieces of software installed on your computer to be able to do this:

* Postgres is the software that runs our database

* A database client lets you view the data in the database, and write SQL queries

* Jekyll is the software used to build our website. If you are adding new data sets, you need to be able to write documentation about those data sources on our website.

* Python runs the code that adds data to our database and that powers our API. You need a virtual environment with both the right version (3.5) of Python installed as well as the necessary packages we use (Flask, others).

Since installing each of these pieces of software and configuring their settings to talk to each other can be difficult on different computers, Docker provides a way for us to do the configuration once and then you can run our pre-configured combination. Docker creates a virtual machine - this is a virtual computer running Linux, so any software you run in the virtual machine thinks it has been installed on a Linux computer that is configured exactly the same as the one we used to make the setup files. While there are sometimes issues setting up Docker, once you have it installed properly it makes it much faster to start working with a new software stack.

We have a Docker setup for all 4 of these components.

If you have problems installing or setting up Docker, you can also configure Postgres, Jekyll, and a database client independently - ask for help if this is the case.


### Secrets.json

This file stores configuration information, such as the url and password to our database. `secrets.json` is in our .gitignore file so is not included with the code when you cloned our Github repository. You can easily make your own version of the file, though:

* In the project repository, navigate to `/housing-insights/python/housinginsights`
* make a copy of the file `secrets.example.json`.
* Rename this copy to `secrets.json`.

This version only includes connection information for a local copy of the database. Later you may need the complete version (for example, if you are updating our production server). Ask a project lead when you run into issues.

## 1) Running Docker

### 1a) One time setup

Start by installing Docker. If you're on Windows, [Docker Toolbox](https://www.docker.com/products/docker-toolbox) is best. Mac is better off using the native [Docker for Mac](https://docs.docker.com/docker-for-mac/install/) and Linux the [Docker for Linux](https://www.docker.com/community-edition)


### 1b) Day-to-day use

When you start each work session, navigate into wherever you keep your housing-insights repository. The current directory should appear just above the `$` in the Quickstart Terminal. You'll need to use these standard Unix command line commands to get to the right place:

```
cd ..         //move up a level
cd myfolder   //move down a level into "myfolder"
ls            //lists all files and folders in your current directory.
```

In your housing-insights repository folder, run this command:

```
docker-compose up -d
```

Once it starts up (might take a moment), you can go to these web addresses:

* `<yourip>:8081`: a web-based Postgres SQL client that lets you run commands on the database, much like pgAdmin or any other database client.
* `<yourip>:4000`: a local copy of our website, housinginsights.org. If you edit any file in the housing-insights/docs folder and save it, the website will be regenerated and you can see the changes when you reload the page.
* `<yourip>:5432`: This one does not work in a browser, but you can use this IP address and port to connect to your local Docker database via your preferred SQL client ([Valentina Studio](https://valentina-db.com/en/get-free-valentina-studio) is a good one). This can sometimes be easier to use than the web version at 8081.

Use `docker-compose stop` to terminate the processes. 

### 1c) Updating your docker containers
Sometimes if we make updates to the required Python packages, or if one of your containers gets corrupted, you will need to build new copies of the Docker containers. When you run `docker-compose up -d` the first time, new container copies are built - however, when you run it again, it uses the old copies. To force docker to build fresh copies, run these commands:

```
$ docker-compose down
$ docker-compose build
$ docker-compose up -d
```

After the final command you should see additional output saying that Docker is downloading and building each of the 4 containers. 


## 2) Add data to your local database copy

If you've got Docker running, you should be able to see your database in the web browser at port `8081`. But there's nothing there!

### Loading Data

1)  `docker-compose ps` to see the containers that are running.  One of them should be **housinginsights_sandbox_1**.  This is the container that is running the miniconda3 python environment.  There is no need to activate or deactivate an virtualenv since it is already sourced.

2) `docker-compose exec sandbox bash` to get inside the container.

3) `cd /repo` to get into the base directory.  The /repo directory is a direct mount of the housing-insights repository on your local computer.  You can make changes locally on your machine and they will be available in the docker container.

4) `cd /repo/python/scripts` to get to the scripts directory.

5) `python load_data.py docker` to load the data

Alternatively, you can use this one liner to load in the data:

```
docker-compose exec sandbox bash -c 'cd /repo/python/scripts && source activate /opt/conda/envs/housing-insights/ && python load_data.py docker'
```


You can also update just some parts of the data:

```
# Deletes all rows with the id 'prescat_project' and then loads new copies of this data from the file listed in manifest.csv
$ python load_data.py docker --update-only prescat_project

# Delete the whole project table, then add the prescat_project and dchousing_project data sources (useful when new columns are added)
$ python load_data.py docker --remove-tables project --update-only prescat_project dchousing_project

# Don't load any new data, but recalculate fields in zone_facts and project tables. 
$ python load_data.py docker --recalculate-only

```

Typically, the data you've loaded previously should still be available after shutting down and starting up Docker again. To check, use your database client to view the contents of the Docker database (for example, visiting localhost:8081 and looking at the list of tables on the left). 