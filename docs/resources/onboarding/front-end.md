---
layout: main
title: H.I. Onboarding
---

# Front end development setup

Our front end development uses the templating engine [Jekyll](https://jekyllrb.com/). This tool lets you write page content in Markdown, and use simple logic to convert this into HTML. It's also the tool used by Github Pages, a free web hosting option that is part of Github, and so is a useful tool to be familiar with for anyone that works with code in Github. 

# **Recommended:**  Install Jekyll Directly

*  On Mac: 
    1. Install the prerequisites: Ruby, RubyGems, GCC and Make. Instructions and links are on the [Jekyll website](https://jekyllrb.com/docs/installation/)
    2. Run `gem install jekyll` from your terminal

* On Windows:
    1. The instructions for [Installation via RubyInstaller](https://jekyllrb.com/docs/windows/#installation-via-rubyinstaller) seem to be the simplest and most reliable installation method. If that doesn't work for you, there are other options listed on this same page as well. 

Once you have Jekyll installed, open a terminal/command prompt and navigate to the housing-insights repository on your computer ([Mac](https://www.macworld.com/article/2042378/master-the-command-line-navigating-files-and-folders.html) and [Windows](https://www.computerhope.com/issues/chusedos.htm) command line intros if it's your first time). Then:
 
* `cd docs` to change into the `housing-insights\docs` folder
* `jekyll serve --incremental` to build a copy of the website and view it through a local server. The `--incremental` flag tells Jekyll that when you save a file it should regenerate just the part of the website affected by the save. You should see something like this (there may be some additional lines):
    ```
       Generating...
                    done in 2.877 seconds.
        Auto-regeneration: enabled for '.../housing-insights/docs'
        Server address: http://127.0.0.1:4000
        Server running... press ctrl-c to stop.
    ```
* Open a web browser and go to the URL listed in `Server address:` output above - in this example it is `http://127.0.0.1:4000`. This will show you a copy of the website using the current code on your computer. 

Every time you save a file in the `docs` folder, Jekyll will rebuild the website using your changes. Keep the command prompt running where you entered the above commands - every time you save a file, you should see a message like this:

```
Regenerating: 1 file(s) changed at 2017-09-05 11:01:47 ...done in 2.7698 seconds.
Regenerating: 1 file(s) changed at 2017-09-05 11:05:09 ...done in 2.227318 seconds.
Regenerating: 1 file(s) changed at 2017-09-05 11:05:12 ...done in 2.497031 seconds.
```
When you make a change to the code, you can see the change in your browser by doing a hard refresh of the page; however, it will take a few seconds for the changes to be reflected - be sure to watch the command prompt and wait for the `...done in XXX seconds.` part of the message to appear before refreshing the page. 


# **Alternative:** Using Docker

The [Docker installation]({{site.baseurl}}/resources/onboarding/docker.html) used for back-end development includes a copy of Jekyll. Running `docker-compose up -d` will start the website; as with a direct install of Jekyll, editing and saving any file in the `/docs` folder will re-generate the website with those changes. Unfortunately, depending on which operating system you're using and which version of Docker you have, Docker is often much slower to recognize changes to files and execute the rebuild. This can make it much more inefficient to use Docker for day-to-day development. 

If you do want to use Docker for viewing the website, either because of problems installing Jekyll or if you're just editing the website occasionally, follow these steps. 

* [Setup docker as usual]({{site.baseurl}}/resources/onboarding/docker.html) and run `docker-compose up -d`. 
* Run `docker ps` to view a list of the currently running containers. You should see something like this:
    ```
    CONTAINER ID        IMAGE                                 ...  PORTS                    NAMES
    b14b87646f52        sosedoff/pgweb                        ...  0.0.0.0:8081->8081/tcp   housinginsights_web_1
    6767fbc67457        housinginsights_jekyll                ...  0.0.0.0:4000->4000/tcp   housinginsights_jekyll_1
    f5c2e0978683        codefordc2/housing-insights-postgres  ...  0.0.0.0:5432->5432/tcp   housinginsights_postgres_1
    c59b7bfb0ebc        housinginsights_sandbox               ...  0.0.0.0:5000->5000/tcp   housinginsights_sandbox_1
    ```
* Find the name of the jekyll container - in this case it is `housinginsights_jekyll_1`. 
* Run `docker logs -f housinginsights_jekyll_1` to view the realtime output of the container. 
* Visit `localhost:4000` or `<your-docker-ip>:/4000` in your web browser, where `<your-docker-ip>` is the ip address of the docker container (see docker instructions)
* When you save a file, watch the command prompt to see when the changes are reflected - note that refreshing the page in your browser will not show the changes until the `done in XX seconds.` portion of the message is shown. 
* To get your command prompt back (without stopping Docker or Jekyll), type `ctrl+c` in the terminal window. 
