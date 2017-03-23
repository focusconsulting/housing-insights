---
layout: main
title: H.I. Resources
---

# Resources for Coders and Contributors
Yes! We're glad you're interested in helping out on this project.

<div class="well">
  <p><strong>Are you new to this project?</strong> We recommend starting with:
  <ul>
  	<li>Review this page</li>
  	<li>Follow the link for the 'Full project summary' for some additional context</li>
  	<li>Follow the setup instructions under 'Getting ready to code'</li>
  	<li>Check out our Github Issues via Waffle.io</li>
  	<li>Join our Slack and sign up for the weekly email update, and send @nealhumphrey your Github username.</li>
  	<li>Pick an issue you're interested in and post on Slack or talk to one of us at a work session about getting started on it!</li>
  </ul>
  </p>
</div>

## 1) Getting involved

* We hold weekly work sessions every Tuesday night. We also meet whenever Code for DC meets. Specific dates and locations, including save-to-calendar links, are on our [latest updates page]({{site.baseurl}}/resources/latest)
* Neal (the project manager) sends a weekly email update to contributors. <a href="#" class="" data-toggle="modal" data-target="#modal_email">Sign up for emails</a>
* Between sessions, we communicate via Slack. There are several Slack channels - a `housing-insights` channel as well as a channel for each team (data, D3, and prototype). To join, go to the [Code for DC homepage](http://codefordc.org/) and click the 'Join Slack' link. 
* In addition to Slack, we also use the Github Issues to discuss things related to specific new features or updates. See below for more info.
* To edit issues on Github (see below), we need to add you as a contributor. Send `@nealhumphrey` a message on Slack with your Github username.


## 2) Understanding affordable housing policy and why we're building this website
* Just getting started? [Read the full project summary]({{site.baseurl}}/resources/summary.html)
* When you're ready to dig in and are trying to understand our issues better, check out this [list of reports and background resources]({{site.baseurl}}/resources/external).
* The current version of our Data Dictionary (still a work in progress) is [located in this Google Sheet](https://docs.google.com/spreadsheets/d/1hhuCgOIYNXP1VovA8TXuBRIR0drDSLSlBQsUSk-MS2Y/edit#gid=0)
* We've put together some user profiles describing our potential tool users. 


## 3) Finding what to work on and coordinating tasks
We use Github Issues to manage our tasks. You can access our issues two ways:

* [Directly view issues on Github](https://github.com/codefordc/housing-insights/issues)
* [View them in a Kanban board on Waffle.io](https://waffle.io/codefordc/housing-insights)

As a contributor to the project, please use issues frequently! 

* On Waffle, use the 'In Progress' section to indicate something is actively being worked on, so others shouldn't duplicate your work.
* On Waffle, use the 'Coordination needed' section to flag something to discuss at the next meeting.
* Use the 'assign' function to indicate who is working on what. You can always assign yourself. If you assign an issue to someone else, be sure to talk to them about it (via Slack or in person). If you stop working on an issue, unassign yourself. We want the assignees to accurately reflect what is available and what isn't. 
* Are you working on something that isn't listed? Add a new issue for it so that we can keep track!
* See something we should do in the future? Add a new issue for it!

Are you new to the project? Browse our "Ready" issues to find something you'd like to work on. 

Some things (mostly non-coding related) are coordinated through Google Docs. You can find all of the Google Docs in [this Google Drive folder](https://drive.google.com/drive/folders/0B6iVubS2zjk4V2dLWXkzemVFbnc?usp=sharing)


## 4) Getting ready to code
* Start by **forking** [the repository](https://github.com/codefordc/housing-insights), and then cloning the forked version of the repository to your computer. We use a triangular workflow - you should push to your fork, but fetch/pull from the Code for DC repo. Setting this up is easy. Use these commands:

```
$ git clone <url-of-your-fork>
$ cd housing-insights
$ git remote add codefordc https://github.com/codefordc/housing-insights.git
$ git remote -v
  #you should see this:
  codefordc       https://github.com/codefordc/housing-preservation.git (fetch)
  codefordc       https://github.com/codefordc/housing-preservation.git (push)
  origin          <your/forked/url> (push)
  origin          <your/forked/url> (fetch)
```

Now instead of plain `git push` and `git fetch`, use these:

```
$ git push origin <branch-name>       #pushes to your forked repo
$ git fetch codefordc <branch-name>   #fetches from the codefordc repo
```

* We use Python, Javascript, and Jekyll. Follow the instructions for [setting up your dev environment](https://github.com/codefordc/housing-preservation) to make sure you have everything you need installed. **Coming soon** Docker setup files to make configuration quick and easy. 
* Our [CONTRIBUTING](https://github.com/codefordc/housing-insights/blob/master/CONTRIBUTING.md) document in our Github repo has important information on code conventions.

## 5) Adding new data sources

[Read the instructions]({{site.baseurl}}/resources/adding-data-sources.html) on how to add a new data source. 


{% include modal_email.html %}