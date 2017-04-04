---
layout: main
title: H.I. Onboarding
---

# Running our website and database locally with Docker


# Running Docker

### One time setup

Start by installing [Docker Toolbox](https://www.docker.com/products/docker-toolbox). After it's installed, run the Docker Quickstart Terminal. Once this is open and running, you'll have a command prompt. Run this command:

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

### Day-to-day use

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

Once it starts up (might take a moment), you can go to these web addresses:

* `<yourip>:8081`: a web-based Postgres SQL client that lets you run commands on the database, much like pgAdmin or any other database client. 
* `<yourip>:4000`: a local copy of our website, housinginsights.org. If you edit any file in the housing-insights/docs folder and save it, the website will be regenerated and you can see the changes when you reload the page. 
* `<yourip>:5432`: This one does not work in a browser, but you can use this IP address and port to connect to your local Docker database via your preferred SQL client ([Valentina Studio](https://valentina-db.com/en/get-free-valentina-studio) is a good one). This can sometimes be easier to use than the web version at 8081. 

You can press `ctrl+c` or `command+c` at any time to end the process. Give it about 10 seconds to shut down, if it hasn't shut down yet you can hit `ctrl+c` again to force it. 

## Add data to your local database copy

If you've got Docker running, you should be able to see your database in the web browser at port `8081`. But there's nothing there! 

### One time setup

1) Make sure you have Python installed (we're currently using Python 3.5, though this may change soon). We recommend [Miniconda](https://conda.io/miniconda.html). Select the Python 3.6 version - you can use Miniconda to install any other Python version. 

2) Open a regular command line (not Docker - though we will have a Docker option for this soon!) and navigate to `path\to\housing-insights\python`

3) Run `conda env create`. This will create a virtual environment using the `environment.yml` file. (If you're not using Anaconda/Miniconda, we try to keep both requirements.txt and environment.yml in sync, but let us know if you have any problems)


### Regular use

Any time you need to recreate the database:

1) Make sure you're using the virtual environment: `activate housing-insights`

2) Navigate to `path\to\housing-insights\python\scripts`

3) On the command line, run `python load_data.py docker rebuild sample`. This will use the docker version of the database (frome secrets.json), first delete any data in the repository, and then re-load a set of sample data into the repository. If you want to rebuild the data with actual data (i.e. what is in manifest.csv instead of manifest.csv), run the same command without 'sample' at the end. 
