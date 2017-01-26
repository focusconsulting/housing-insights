---
layout: main
title: D3 Scaffolding
---

# D3.js mockups of Housing Insights visualization types

## The latest versions 

### Prototype #1: Moving blocks
a.
<svg id="chart-0"></svg>
<!-- next prototype goes below -->
<!--b.
<svg id="chart-1"></svg>-->
Codebase: [https://github.com/codefordc/housing-insights/tree/dev/docs/d3-mockup](https://github.com/codefordc/housing-insights/tree/dev/docs/d3-mockup)

### Prototype #2: Dashboard library

To come

## Beginning examples (newest first, reverse chron)

Contributors new to D3.js or new to housing insights are encouraged to check out some of the tutorials listed in [issue 52 on the github repository](https://github.com/codefordc/housing-insights/issues/52#issue-199017844).

The examples embedded below are the D3 scaffolding team's first forays into a proof of concept for [prototype #1 (moving blocks)](https://github.com/codefordc/housing-insights/issues/48#issue-197904171).

Please click through to edit in JSFiddle.

**#4 Using a constructor method to initialize the chart; separates cooncerns somewhat for more maintainable code**
<script async src="//jsfiddle.net/ostermanj/h8xutLtr/35/embed/result/"></script>

**#3 Refactoring the code from D3 v3 to D3 v4**
<script async src="//jsfiddle.net/ostermanj/h8xutLtr/29/embed/result/"></script>

**#2 Using raw CSV data from the housing insight repo, brought in as a JSON object**
<script async src="//jsfiddle.net/ostermanj/h8xutLtr/28/embed/result/"></script>

**#1 Using made-up data provide inline**
<script async src="//jsfiddle.net/ostermanj/h8xutLtr/26/embed/result/"></script>


<!-- scripts for D3, D3-tip, and the visualizations -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/4.4.1/d3.min.js"></script>
<script src="{{ site.baseurl }}/d3-mockup/js/d3-tip.js"></script>
<script src="{{ site.baseurl }}/d3-mockup/js/prototype-1a.js"></script>
<!-- for additional prototpe sub-version, add link to js files follwowing prototype-1b, prototype-1c, etc
     with the main d3 selector point to the corresponding svg element toward the top -->