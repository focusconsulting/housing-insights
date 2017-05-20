# Housing Insights - Coding and Workflow conventions

## Git conventions
We use a fork-and-pull request method, which should be familiar to most people who have contributed to an open source project before.

For info on setting up Git to work with a triangular workflow, follow [these configuration instructions](http://housinginsights.org/resources/onboarding/triangular-git.html). If you need more help, ask a project lead. 


### Branching
We use a loose [git flow](https://datasift.github.io/gitflow/IntroducingGitFlow.html) model. This means:

* `dev` is the best place to look for the most recent (but maybe incomplete) code.
* Before starting work, you should usually update and checkout `dev` first, and then make your own feature branch (e.g. `3-modal-fixes`)
* It will make us very happy if you start your branch name with the Github issue number  &#x263A;
* All pull requests should go into `dev`
* `master` always matches what is on our live website, and is tagged with version numbers.

If you know how to do that sort of thing, squashed and rebased pull requests bring great joy to our repo history! If you don't know what that means, it's not necessary and is best to learn only when you are confident in your Git skills.

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
