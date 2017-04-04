---
layout: main
title: Setting up a Triangular Workflow
---

# Triangular workflow in Git

Start by **forking** [the repository](https://github.com/codefordc/housing-insights), and then cloning the forked version of the repository to your computer. We use a triangular workflow - you should push to your fork, but fetch/pull from the Code for DC repo. Setting this up is easy. Use these commands:

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

Here's [more information](https://github.com/blog/2042-git-2-5-including-multiple-worktrees-and-triangular-workflows#improved-support-for-triangular-workflows) on setting up triangular workflows (scroll to "Improved support..."). 

Never worked with a triangular workflow before? Ask a project lead for help. 

