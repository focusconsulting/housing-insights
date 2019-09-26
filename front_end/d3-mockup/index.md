---
layout: main
title: D3 Scaffolding
customCSS: prototype-1a
---

# D3.js mockups of Housing Insights visualization types

## The latest versions 

### Prototype #1: Moving blocks

**Initial sort is by zip code (top to bottom then right)**

a.
<ul id = "metric_menu">
  <h1>Metrics</h1>
</ul>
<div id="chart-0" class="d3-chart"></div>
<!-- next prototype goes below -->
<!--b.
<div id="chart-1"></div>-->
Codebase: [https://github.com/codefordc/housing-insights/tree/dev/docs/d3-mockup](https://github.com/codefordc/housing-insights/tree/dev/docs/d3-mockup)

**Please visit [this page](/d3-mockup/early-examples/) for earlier examples of the D3 prototypes.**

<!-- scripts for D3, D3-tip, and the visualizations -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/4.4.1/d3.min.js"></script>
<script src="{{ site.baseurl }}/d3-mockup/js/d3-tip.js"></script>
<script src="{{ site.baseurl }}/d3-mockup/js/prototype-1a.js"></script>
<!-- for additional prototpe sub-version, add link to js files follwowing prototype-1b, prototype-1c, etc
     with the main d3 selector point to the corresponding svg element toward the top -->