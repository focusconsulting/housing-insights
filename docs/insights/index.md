---
layout: main
title: Insights
---

<h1>Insights</h1>
<p>Each of the pages linked below contains an individual analysis created by one of our project team members. Click on a link to view the visualization!</p>

<p>For team members: to add a visualization, make a new markdown file (.md extension) and put it in the folder `/docs/_insights`. You can model your markdown file off of one of the existing ones. Be sure to include the Jekyll frontmatter (the stuff between the --- at the top of the file). In the body, you should copy-paste in the 'embed code' that is available by clicking on the 'Share' link on the Tableau Public webpage for your visualization. Your visualization will automatically show up in the list, and the url will be created from whatever you name your markdown file. 
</p>

{% for insight in site.insights %}
<div class="insight-block">
    <a href="{{insight.url}}">
        <h3>{{forloop.index}}) {{insight.title}} </h3>
    </a>
    <p> {{insight.author}} </p>
</div>
{% endfor %}