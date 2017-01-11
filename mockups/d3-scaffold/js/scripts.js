document.addEventListener("DOMContentLoaded", function() { // vanilla js doc ready w/ enough browswr support for this exercise

// NOW USING CONSTRUCTOR METHOD
// ADDS SEPARATE SORTING FIELD AND DIRECTION ADN SEPARATES THE SORTING FUNCTION

// options

var options = { // options declared in global scope for access in .json callback
  width: 10, // size of each square
  spacer: 2, // space between each square
  columns: 7,
  field: 'PctVacantHsgUnitsForRent_2000', // define which property you want visualized
  sortField: 'NumOccupiedHsgUnits_2010', // which property to sort by
  asc: false // sort direction, ascending or not ascending
  };
  

// data

/*
 * d3.csv returns all strings regardless of data type. code below
 * uses + operator to convert strings to numbers. if using the
 * + operator would result in NaN (not a number), the value is not
 * converted. alternatively could allow data to pass as strings and 
 * deal with conversion later, when appending elements
 */
 
 
d3.csv("https://raw.githubusercontent.com/codefordc/housing-insights/dev/scripts/small_data/Neighborhood_Profiles/nc_housing.csv", function(error, json) {
  if (error) throw error;
  
  json.forEach(function(obj) { //iterate over each object of the data array
    for (var key in obj) { // iterate over each property of the object
      if (obj.hasOwnProperty(key)) { // if key is property of obj, not prototype
        obj[key] = isNaN(+obj[key]) ? obj[key] : +obj[key]; // convert to number unless result would be NaN
      }
    }
  })
  console.log(json);
  new Chart(json, options, '#chart-0'); // call constructor
});

function Chart(data, options, el) { // constructor
chart = this;
console.log(options);
data = data.sort(function(a, b) { //sorting with JS prototype sort function
    if (options.asc) return a[options.sortField] - b[options.sortField];
    return b[options.sortField] - a[options.sortField];
  });
chart.svg = d3.select(el)
    .attr('width', 100)
    .attr('height', 100); // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult

  chart.minValue = d3.min(data, function(d) {
    return d[options.field]
  });
  chart.maxValue = d3.max(data, function(d) {
    return d[options.field]
  });
  chart.scale = d3.scaleLinear().domain([this.minValue, this.maxValue]).range([0.1, 1]); // in v3 this was d3.scale.linear()
  chart.svg.selectAll('rect')
    .data(data)
    .enter()
    .append('rect')
    .attr('width', options.width)
    .attr('height', options.width)
    .attr('fill', '#325d88')
    .attr('fill-opacity', function(d) {
      return chart.scale(d[options.field])
    }) // fill-opacity is a function of the value
    .attr('x', function(d, i) {
      return (i * options.width + options.spacer * i) - Math.floor(i / options.columns) * (options.width + options.spacer) * options.columns
    }) // horizontal placement is function of the index and the number of columns desired
    .attr('y', function(d, i) {
      return Math.floor(i / options.columns) * options.width + (Math.floor(i / options.columns) * options.spacer)
    }) // vertical placement function of index and number of columns. Math.floor rounds down to nearest integer
    .append('title')
    .text(function(d) {
      return d.CLUSTER_TR2000 + ': ' + d3.format(',')(d[options.field]) + ' occupied units'
    });

}







});