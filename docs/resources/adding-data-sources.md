---
layout: main
title: Adding Data Sources
---

# How to add a new data source

<i><strong>NOTE</strong>: There's a good chance these instructions will get outdated as we improve our data ingestion process! The fundamental principles will stay roughly the same - syncing data from your local machine to S3, creating json for each SQL table and a manifest row for each raw file, and creating a Cleaner. If you run into any problems ask a data team member for help.</i>

## 0) Setup

### Docker

**One time setup**

Start by installing [Docker Toolbox](https://www.docker.com/products/docker-toolbox). After it's installed, run the Docker Quickstart Terminal. Once this is open and running, you'll have a command prompt. Run this command:

```
$docker-machine ip
```

This will print the IP address of your local Docker instance. Open up `/python/housinginsights/secrets.json` and make sure you have a couple lines like this:

```
    "docker_database": {
        "connect_str": "postgresql://codefordc:codefordc@192.167.55.100:5432/housinginsights_docker"
    },
```

Substitute your IP address for the one that says `192.167.55.100` in this example (but keep `:5432` at the end).

**Day-to-day use**

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

### Add data to your local database copy

If you've got Docker running, you should be able to see your database in the web browser at port `8081`. But there's nothing there! 

**One time setup**

1) Make sure you have Python installed (we're currently using Python 3.5, though this may change soon). We recommend [Miniconda](https://conda.io/miniconda.html). Select the Python 3.6 version - you can use Miniconda to install any other Python version. 

2) Open a regular command line (not Docker - though we will have a Docker option for this soon!) and navigate to `path\to\housing-insights\python`

3) Run `>conda env create`. This will create a virtual environment using the `environment.yml` file. (If you're not using Anaconda/Miniconda, we try to keep both requirements.txt and environment.yml in sync, but let us know if you have any problems)


<strong>Regular use</strong>

Any time you need to recreate the database:

1) Make sure you're using the virtual environment: `>activate housing-insights`

2) Navigate to `path\to\housing-insights\python\scripts`

3) On the command line, run `>python load_data.py docker rebuild sample`. This will use the docker version of the database (frome secrets.json), first delete any data in the repository, and then re-load a set of sample data into the repository. If you want to rebuild the data with actual data (i.e. what is in manifest.csv instead of manifest_sample.csv), run the same command without 'sample' at the end. 

### Downloading Data

We recommend that if you are going to be someone adding new data sources, you should first download all the raw data files. Downloading all the data locally helps us all keep a consistent folder structure; you'll also need much of this data to recreate a local copy of the database. 

Follow the instructions under [Get the latest data](https://github.com/codefordc/housing-insights/tree/dev/python) in the /python/readme.md file. If you use the virtual environment from above, you will already have the awscli installed.

As of 3/23/2017, this will download approximately 1.6Gb, so make sure you have both bandwidth and space (i.e. don't do this at a hacknight). 

<br/>
<br/>
## 1) Download the raw data file for your new data source

Store the raw data file on your local hard drive. 

* For historical data that is broken into sections by when it was collected (like census data), you can make a folder corresponding to the data's timeframe:  
    `housing-insights/data/raw/acs/B25057_lower_rent_by_tract/2014_5year/ACS_14_5YR_B25057_with_ann.csv`
    `housing-insights/data/raw/acs/B25057_lower_rent_by_tract/2015_5year/ACS_15_5YR_B25057_with_ann.csv`


* If the data version is tied to when it was collected, be sure to put it into a data-stamped folder. For example, we can take a snapshot of the Preservation Catalog at any point in time and it could include small changes to the previous snapshot, so we store it like this:  

    `housing-insights/data/raw/preservation_catalog/20170315/Project.csv`  
    `housing-insights/data/raw/preservation_catalog/20160401/Project.csv`

## 2) Add a new table to `meta.json`

If this is a new data source that can't go into an existing table in SQL, you'll need to add a new table so our code knows where to put it. 

* Open the file `housing-insights/python/housinginsights/ingestion/make_draft_json.py` and edit the file to link to the file you want to load, and the SQL table you want to put it in. If making a new table, be sure to follow good SQL conventions (no spaces, capitalization, etc.). 
* Open a command prompt
* Use the command `cd path/to/housinginsights/python/housinginsights/ingestion` to navigate to the folder that contains make_draft_json.py
* Run `dir` (windows) or `ls` (mac) and make sure you see make_draft_json.py in the list. 
* type `python make_draft_json.py single` to make draft json for that file. This will be output to `/housing-insights/python/logs`
* Manually check each field of the draft json. Make sure to change:
	* Anything that is an ID of some sort should be type:'text', even if draft_json thought it should be an integer. 
	* Date fields should be changed to type: 'date'. 
	* Verify that decimal, text, integer, date, and timestamp fields are appropriate. 
	* Add a better display_name and display_text to any field that will be displayed on the website. 
	* Change any field names that are not intuitive to use a better sql_name. Do not edit the source_name. 
* Copy the updated json into meta.json. Be sure to watch out for proper use of nested { } and commas. The updated meta.json should look like this:
	    
	    {
	        "tablename": {
	            "cleaner": "MyCleanerName",
	            "replace_table": false, //or true
	        	"fields": [ blah blah blah]
	        },

	        "othertable": {
	            "cleaner": "MyCleanerName",
	            "replace_table": false,
	        	"fields": [ blah blah blah]
	        }
	    }

    Note that the { } for the last object doesn't have a comma but the earlier ones do. 

## 3) Add the file to `manifest.csv`

Every file that gets added to the database needs to be in `manifest.csv`. Add a row. The keyword 'use' under include_flag means the data will be used; any other value can be used to indicate some other status and the file will not be loaded the next time the database is recreated. 

## 4) Add a cleaner

Make a custom class in /ingestion/Cleaners.py. It should inherit from the CleanerBase and implement any changes needed to the data before it arrives in our database - replacing null, parsing dates, parsing boolean, and handling weird values. See examples there. 

Be sure that the name of this class matches the name associated with this table in meta.json - the class name is used to load the correct cleaner. 

## 5) Try it locally

Make sure you have a local Postgres database up and running, and a valid connect string in the section 'local_database' in secrets.json. Although it takes longer to build, until you're fully familiar with the code we recommend using the 'rebuild' option to dump your existing database first. You can change the value of 'use' in the manifest.csv to something else (like "skip_while_testing") to focus only on the table you're working on. You'll probably need to iterate a few times to get your Cleaner object working correctly. 

Be sure to test joining the table to whatever appropriate other tables the data would need to get connected to. These might be zip code, census tract, or ward. If geographical data has latitude/longitude, this can be used directly without a SQL join; but, other data might need to be joined to an intermediate table using things like the Master Address Repository table using SSL (square suffix lot) or block, to connect it to DC geography. Make sure you know how the data will be connected to our other data. If there are naming discrepancies (e.g. "Census Tract 20.1" vs "Tract 20.1") you can resolve this in the cleaner. 

## 6) Add documentation

Every file should have a page located at `housinginsights/docs/data`. Use the `example.md` as a model. Name the file `table_name.md`. If possible, test your site using Jekyll. With Jekyll installed, navigate to `housinginsights/docs` from the command line and enter the command `jekyll serve`. You can then visit the local URL provided (typically `http://localhost:8080` or something similar) and check for errors in your markdown. The files named `filename.md` will be converted to `filename.html` in the website url. 

## 7) Upload the data to S3

Follow the instructions under the heading "[If you add or update any data files](https://github.com/codefordc/housing-insights/tree/dev/python)" in the /python/readme.md file. Note that this will only upload any new data files - it will not remove any files you have deleted locally. If you have moved or renamed a folder since the last time it was synced, ask for help on deleting existing files to avoid breaking our data archive. Be sure to use `--dryrun` and make sure your commands will do what you think they should.

## 8) Commit your changes in Git and push them to Github. 

Before doing any coding related work, you'll want to make a new feature branch in Git - as you go through the steps above you should be committing your changes to that branch. When you've finished everything, be sure to do a final push and open a 'pull request' on Github. 

