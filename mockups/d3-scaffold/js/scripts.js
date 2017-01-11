document.addEventListener("DOMContentLoaded", function() { // vanilla js doc ready w/ enough browswr support for this exercise

// USING D3 v4.x
// NOT YET USING CONSTRUCTOR METHOD

/*
 * d3.csv returns all strings regardless of data type. code below
 * uses + operator to convert strings to numbers. if using the
 * + operator would result in NaN (not a number), the value is not
 * converted. alternatively could allow data to pass as strings and 
 * deal with conversion later
 */

// using raw nc_housing.csv from github repo as example of more real data

d3.csv("https://raw.githubusercontent.com/codefordc/housing-insights/dev/scripts/small_data/Neighborhood_Profiles/nc_housing.csv", function(dataset) { 
  var field = 'NumOccupiedHsgUnits_2010'; // define which property you want visualized
  dataset.sort(function(a, b){ //sorting with JS prototype sort function
    return b[field] - a[field];
  });
  dataset.forEach(function(obj) { //iterate over each object of the data array
    for (var key in obj) { // iterate over each property of the object
         if (obj.hasOwnProperty(key)) { // if key is property of obj, not prototype
            obj[key] = isNaN(+obj[key]) ? obj[key] : +obj[key]; //convert to number 
         }
      }
  });
  console.log(dataset);
  
  var width = 10, // size of each square
  spacer = 2, // space between each square
  columns = 7; 
  
  var svg = d3.select('#chart-0')
    .attr('width',100)
    .attr('height',100); // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult
    
  var minValue = d3.min(dataset, function(d) { return d[field] });
  var maxValue = d3.max(dataset, function(d) { return d[field] });
  var scale = d3.scaleLinear().domain([minValue,maxValue]).range([0.1,1]); // in v3 this was d3.scale.linear()
  var square = svg.selectAll('rect')
    .data(dataset)
    .enter()
    .append('rect')
    .attr('width',width)
    .attr('height',width)
    .attr('fill', '#325d88')
    .attr('fill-opacity', function(d){return scale(d[field])}) // fill-opacity is a function of the value
     .attr('x', function(d,i){return (i * width + spacer *  i) - Math.floor( i / columns) * (width + spacer) * columns}) // horizontal placement is function of the index and the number of columns desired
     .attr('y', function(d,i){return Math.floor(i / columns) * width + (Math.floor(i / columns) * spacer)}) // vertical placement function of index and number of columns. Math.floor rounds down to nearest integer
    .append('title')
    .text(function(d) { return d.CLUSTER_TR2000 + ': ' + d3.format(',')(d[field]) + ' occupied units'});

});





});