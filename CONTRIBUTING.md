# Housing Insights - Coding and Workflow conventions

## Git conventions
We use a fork-and-pull request method, which should be familiar to most people who have contributed to an open source project before. When you're starting the project, it's easy:

1. Click 'fork' in the upper right of this page.
1. Click you will now be on *your* copy of the repo on Github (look for YourUserName/housing-insights in the upper left).
1. Click the green 'Clone' button from **your** copy (not the CodeForDC copy)
1. Once you've cloned it to your computer, make a new branch for your feature and then start coding!
1. Push your local changes to your fork regularly
1. When you're done, go to your fork of the repo on Github, make a pull request, and be sure to select 'base fork' on the left (Code for DC) and your fork on the right.

#### Important - Sync Your Fork
But! Don't forget that if changes happen on the Code for DC repo, you need to sync that code

**Easy Way**
1. Make sure you've pushed all local changes to your fork on Github
1. Go to your repo on Github
1. Click 'Pull requests' and 'New Pull Request'
1. Change the left hand 'base fork' to be your fork (`YourUserName/housing-insights`) and choose the dev branch. If this makes the 'base fork' dropdown disappear, click `'compare across forks'` in the helper text to get it back.
1. Change the right hand 'head fork' to be `codefordc/housinginsights` and the branch to be dev.
1. Create the pull request.
1. Merge your own pull request. This will merge the latest `codefordc` changes into your fork of the dev branch.

**Professional Way**
If you want to get fancy, the Github blog has a good walkthrough of setting up two remote repositories (e.g. the codefordc repo and your fork of it) and using this to work in a triangular workflow. Here's [the description](https://github.com/blog/2042-git-2-5-including-multiple-worktrees-and-triangular-workflows#improved-support-for-triangular-workflows) (scroll down to 'Improved support...'). In short, you can configure your local Github client to track multiple remote repositories (instead of just 'origin', you can have 'codefordc' and 'mygithub' or any other fork), and then you can use your local git client to push and pull these changes.

### Branching
We use a loose [git flow](https://datasift.github.io/gitflow/IntroducingGitFlow.html) model. This means:

* `dev` is the best place to look for the most recent (but maybe incomplete) code.
* Before starting work, you should usually update and checkout `dev` first, and then make your own feature branch (e.g. `3-modal-fixes`)
* It will make us very happy if you start your branch name with the Github issue number  &#x263A;
* All pull requests should go into `dev`
* `master` always matches what is on our live website, and is tagged with version numbers.

## Coding conventions
Some miscellaneous coding conventions:
* Write code that doesn't need code comments - variable names that clearly indicate content and type.
* **But**, add more comments than you think is necessary. Lots of beginners will be working on the project, and 'self-documenting' code isn't always self documenting when you are still figuring out the basic language or package syntax.
  * Always add a comment to describe purpose of a function and/or code section.
  * Always use comments to document the meaning of positional parameters; use named parameters whenever possible
    ```
    # Bad
    entries.select(3, 5)

    # Better
    entries.select(3, 5)  #.select(from,to) per mypackage docs.

    # Ideal when language and package allows
    entries.select(from=3, to=5)
    ```
* Use most common language conventions whenever possible
  * Python: `snake_case` for vars and modules, `CapitalCamelCase` for class names, `ALL_UPPER` for constants.
  * Javascript: `camelCase` for vars, `CapitalCamelCase` for constructors.
  * Single-line functions, CSS definitions, etc. are OK when they are short and/or follow a repeatable pattern.

## License
We're publishing this project under the [MIT license](https://github.com/codefordc/housing-insights/blob/master/LICENSE.txt). By contributing code to this repo you are agreeing to make your work available to the public under the terms of this license.
