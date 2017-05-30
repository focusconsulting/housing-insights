---
layout: main
title: Command Line Cheatsheet
---

# Command Line Cheatsheet

First, make sure you've installed and configured Docker appropriately - [instructions here]({{site.baseurl}}/resources/onboarding/docker.html). 

# Command line navigation

Remember, every command you enter at the command line can use the current 'command line location' to change how it operates. Make sure you are in the right place before you enter a command. 

```
cd ..               //move up a level
cd myfolder         //move down a level into "myfolder". This is relative to your current location. 
ls                  //lists all files and folders in your current directory. use dir on windows instead of ls
cd /path/to/folder  //inside the Docker machine, on Mac or on Linux, starting with a / means it is a full path, not relative.
                    //On windows this would be done with "C:/path/to/folder"
```

# Docker commands

Complete instructions on Docker are part of the [Docker configuration instructions]({{site.baseurl}}/resources/onboarding/docker.html)

```
cd path/to/your/housing-insights        //navigate per above instructions
docker-compose up -d                    //starts the virtual machine with postgres, pgweb, 
                                        //jekyll and a python that has our packages installed.
                                        // -d tells it to run in the background (so you can run more commands)
docker-compose ps                       //See what containers are running (in our project, "up" provides 4 containers)
docker-compose exec sandbox bash        //turns your local command line into a command line inside the virtual machine
                                        //you have to already have the 'sandbox' container running (i.e. from the "up" command)

ctrl + p then ctrl + q                  //get out of the vm command line and back to regular docker command line.
                                        //enter these shortcut key combos one after the other. 
docker-compose stop                     //turns off our 4 containers postgres, pgweb, jekll, python. 
```

### Things you get from Docker:

For most people, replace `<yourip>` with `192.168.99.100`. If that doesn't work, try `localhost` or check what it should be by using `docker-machine ip`
* `<yourip>:8081`: a web-based Postgres SQL client that lets you run commands on the database, much like pgAdmin or any other database client. 
* `<yourip>:4000`: a local copy of our website, housinginsights.org. If you edit any file in the housing-insights/docs folder and save it, the website will be regenerated and you can see the changes when you reload the page. 
* `<yourip>:5432`: This one does not work in a browser, but you can use this IP address and port to connect to your local Docker database via your preferred SQL client ([pgadmin](https://www.pgadmin.org/) is common). This can sometimes be easier to use than the web version at 8081. 
* `sandbox`: A Python installation with a virtual environment already created with the dependencies of our project. Access this via the "exec" command above. 



# Git

A more complete day-to-day checklist on git is [available here](http://nhumphrey.com/git/practical-git-checklist.html)

```
git remote -v       //Checks to make sure you're ready for triangular workflows. 
                    //If this does not have both "origin" and "codefordc" listed you need to fix your configuration. 
                    //If it does, you don't need to check again unless you delete your repository.

git fetch --all     //This should be the first command you type every time you sit down to work.
                    //Makes sure you have latest changes available

git status          //Check what branch you currently have checked out, and if you have unstaged files. 
                    //If you are starting work, this should always say working 
                    //branch clean (if not, see the day-to-day checklist instructions)

git checkout dev            //We use the dev branch as our main place to combine code 
                            //from multiple people. Start new work from here.
git pull codefordc dev      //Add the latest changes from the codefordc repo to your branch
git branch cool-feature     //Make a new branch for your work
git checkout cool-feature   //Move onto that branch

//<write some code and save the files>//

git add -A                  //Add all the files you've edited, including new ones
git commit                  //Commits the added files to your branch
git push origin             //Pushes your code to *your* Github copy. Use a pull request on Github 
```


# Python commands

These instructions assume you're operating inside the above Docker container. 

```
//Adding data to the database
cd /repo                            //The code stored in the housing-insights repository on your computer appears in the `/repo` folder in Docker. 
                                    //You can make changes locally on your machine and they will be available in the docker container.
cd /repo/python/scripts             //change into the scripts folder to find code that you can run
python load_data.py rebuild docker  //Use this in nearly all cases. Adds all the data from scratch to your Docker database. 
                                    //Only need to run this when there are new files to load 
                                    //(data in the database stays available between sessions)

//Other options - keywords added in any order
python load_data.py             //adds data to the database. Only loads new files added to manifest.csv - 
                                //existing files unchanged. Uses defualt of 'local' database

python load_data.py rebuild     //rebuild keyword tells code to drop all tables in the database first
python load_data.py docker      //docker keyword says to use the docker database instead of local database. 
python load_data.py remote      //edit the live data. **WARNING** only maintainers should use this. 
python load_data.py sample      //only use 3 sample tables, useful for testing and first time setup

//Testing the local API
cd /repo/python/api             //change into the api folder for api-related code
python application.py           //starts the local server. Go to http://192.168.99.100:5000 to view.
```
