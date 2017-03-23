"use strict";
// NOW USING CONSTRUCTOR METHOD
// ADDS SEPARATE SORTING FIELD AND DIRECTION ADN SEPARATES THE SORTING FUNCTIONS
  

/*
 * d3.csv returns all strings regardless of data type. code below
 * uses + operator to convert strings to numbers. if using the
 * + operator would result in NaN (not a number), the value is not
 * converted. alternatively could allow data to pass as strings and 
 * deal with conversion later, when appending elements
 */

//start new
var PieChart = function(DATA_FILE, dataName, el, field, width, height) { // set text of tooltip with 'readableField' arg
    Chart.call(this, DATA_FILE, dataName, el, field, width, height); // First step of inheriting from Chart
    this.extendPrototype(PieChart.prototype, PieExtension);
}

PieChart.prototype = Object.create(Chart.prototype);

var PieExtension = { // Final step of inheriting from Chart.
  setup: function(el, field, width, height){
        var chart = this,

data=chart.data;


//aggregate data by unique values in [field] defined for each pie at bottom
var pieVariable = d3.nest()
  .key(function(d) { return d[field]; })
  .rollup(function(v) { return v.length; })
  .entries(data);

var textPercent= d3.format(".0%")((pieVariable[0].value)/(pieVariable[1].value+pieVariable[0].value));

chart.radius=Math.min(width, height)/2;

chart.color = d3.scaleOrdinal()
  .range(["#b3cde3","#fbb4ae"]);

// old colors "#bebada","#fb8072","#80b1d3","#fdb462","#b3de69","#fccde5","#d9d9d9","#bc80bd","#ccebc5","#ffed6f","#2C93E8","#F56C4E"]);

//d3 pie layout, which calculates the section angles for you
chart.pie = d3.pie()
    .sort(null)
    .value(function(d) { return d.value; })(pieVariable);

//lets you see the angles
console.log(chart.pie);
console.log(chart.options);

chart.arc = d3.arc()
    .outerRadius(chart.radius - width/20)
    .innerRadius(chart.radius - width/4);

chart.svg = d3.select(el)
    .append("svg")
    .attr('width', width+10)
    .attr('height', height+20) // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult
    .append("g")
    .attr("transform","translate(" + width /2 + "," + height /2 + ")");

chart.g = chart.svg.selectAll("arc")
    .data(chart.pie)
    .enter().append("g")
    .attr("class", "arc");
    //.on("mouseover", function(d) {
        //  options.groceryName=d.data.key;
        //  options.groceryNumber=d.value;
        //  });
chart.g.append("path")
      .attr("d", chart.arc)
      .style("fill", function(d) { return chart.color(d.data.key); });

chart.g.append("text")
    .attr("text-anchor", "middle")
    .attr('class','pie_number')
    .text(textPercent);

//this is bad. 
chart.g.append("text")
    .attr("x",-30)
    .attr("y",45)
    .attr('class','pie_text')
    .text(field);
}
};


var DATA_FILE ='data/Project.csv';
//var DATA_FILE = 'https://raw.githubusercontent.com/codefordc/housing-insights/dev/scripts/small_data/PresCat_Export_20160401/Project.csv';

// first Chart loads new data
new PieChart(DATA_FILE,'#pie', 'Subsidized',75,75); 


    new PieChart(DATA_FILE,'#pie-1','Cat_Expiring',75,75); 
    new PieChart(DATA_FILE,'#pie-2','Cat_Failing_Insp',75,75); 
    new PieChart(DATA_FILE,'#pie-3','Cat_At_Risk',75,75);
    new PieChart(DATA_FILE,'#pie-4','PBCA',75,75); 








