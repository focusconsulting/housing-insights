---
layout: main
title: H.I. Onboarding
---

# Welcome to Housing Insights!

Thanks for joining our project! First we'll do some quick setup to bring you into the project. Then, optionally read on for more info and background about our goals and work plan. 

## Setup steps

1) **Fork our [repository on Github](https://github.com/codefordc/housing-insights)**. Is this your first time forking? [Read detailed instructions here]({{site.baseurl}}/resources/onboarding/git-intro.html)

2) **Join our slack channel**. Between in-person sessions, we communicate via Slack. Go to the [Code for DC homepage](http://codefordc.org/) and click the 'Join Slack' link. There are several Slack channels - a `housing-insights` channel as well as a channel for each team (data, D3, and prototype). 

3) **Fill out our [onboarding survey](https://goo.gl/forms/FsHzS4rzUNwnVnh02)**. It's mostly things like usernames so we can add you to the project.

4) **Clone your fork of the repository** to your computer, and add additional remotes so that you can pull from Code for DC and push to your fork. [Detailed instructions]({{site.baseurl}}/resources/onboarding/triangular-git.html). 

5) **Install [Docker Toolbox](https://www.docker.com/products/docker-toolbox)**. If you've used Docker before and already have any version of Docker working, you can use that - Docker Toolbox is the easiest to use the first time (especially on Windows). 

6) **Configure the `secrets.json` file**. In the project repository, navigate to `/housing-insights/python/housinginsights` and make a copy of the file `secrets.example.json`. Rename this copy to `secrets.json`. You can use the copy with the example keys for now. Later you may need the real version - ask a project lead when you run into issues. 

7) **Run Docker Compose on our code** to get a local copy of our database and our website. [Detailed instructions]({{site.baseurl}}/resources/onboarding/docker.html). 


## How we work

* We hold weekly come-if-you-can work sessions every Tuesday night. We also meet whenever Code for DC meets. Specific dates and locations, including save-to-calendar links, are on our [latest updates page]({{site.baseurl}}/resources/latest)

* Neal (the project manager) sends a weekly email update to contributors.

* Between sessions, we communicate via Slack. There are several Slack channels - a `housing-insights` channel as well as a channel for each team (data, D3, and prototype).

* In addition to Slack, we also use the Github Issues to discuss things related to specific new features or updates. As a contributor to the project, please use issues frequently! 

    * On Waffle, use the 'In Progress' section to indicate something is actively being worked on, so others shouldn't duplicate your work.

    * On Waffle, use the 'Coordination needed' section to flag something to discuss at the next meeting.

    * Use the 'assign' function to indicate who is working on what. You can always assign yourself. If you assign an issue to someone else, be sure to talk to them about it (via Slack or in person). If you stop working on an issue, unassign yourself. We want the assignees to accurately reflect what is available and what isn't.

    * Are you working on something that isn't listed? Add a new issue for it so that we can keep track!

    * See something we should do in the future? Add a new issue for it!

