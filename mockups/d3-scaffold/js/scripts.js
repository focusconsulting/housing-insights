/*
 *  This script is for the d3-based proof of concept for prototype option #1
 *  which is the "moving blocks"  visualizations (issue #48 on the github repository)
 *  Our goal is to have the d3 scaffolding ready by the end of January so that we can put
 *  the prototype into code once the prototype team has finished designing how it should work.
 *
 *  The D3 scaffolding task is covered in issue #52.
 */
var chart0; 

document.addEventListener("DOMContentLoaded", function() { 

/* We wrap the script in a plain-vanilla javascript event callback with enough browser support for 
 * this exercise. This is to make sure the chart's container has rendered and the d3.js library has loaded
 * before we begin these scripts are executed.
 */

// NOW USING CONSTRUCTOR METHOD
// ADDS SEPARATE SORTING FIELD AND DIRECTION ADN SEPARATES THE SORTING FUNCTION

// options

  var options = { // options declared in global scope for access in .json callback below
      width: 10, // size of each square in pixels
      spacer: 2, // space between each square, in pixels
      columns: 7, // i.e., how many squares we want in each row of the block visualization. 
      field: 'PctVacantHsgUnitsForRent_2000', // define which property you want visualized
      sortField: 'NumOccupiedHsgUnits_2010', // which property to sort by
      asc: false // sort direction, ascending or not ascending
      };
      
    /* note: so far the size of the squares and the size of the svg container is hard-coded
     * We will eventually need to the sizes to be return from functions that adjust for viewport size
     * and / or use d3's resize() method to adjust for device sizes.
     */


    /*
     * d3.csv returns an array of objects representing the data in the csv. each object is a row
     * of the data. they keys of the objects are the columns headers and the values and the values. 
     * D3 returns all the values as strings regardless of the orginal data type.

     * The code below uses a + operator to convert strings to numbers. if using the
     * + operator would result in NaN (not a number), the value is not
     * converted. Alternatively we could allow data to pass as strings and 
     * deal with conversion later, when appending elements
     * 
     * d3.csv(<source>,<callback>); c
     * in this case, sources is a string, and callback is a function literal (right term? -JO)
     */
     
     
    d3.csv("https://raw.githubusercontent.com/codefordc/housing-insights/dev/scripts/small_data/Neighborhood_Profiles/nc_housing.csv", function(error, json) {
      if (error) throw error;
      
      json.forEach(function(obj) { //iterate over each object of the data array
        for (var key in obj) { // iterate over each property of the object
          if (obj.hasOwnProperty(key)) { 
          /* ^ if key is property of obj, not of the prototype [for (var key in obj)
           * iterates through keys that are properties of the object prototype, 
           * not just the data properties we need]  
           */
            obj[key] = isNaN(+obj[key]) ? obj[key] : +obj[key]; // + operator converts to number unless result would be NaN
          }
        }
      })
      console.log(json);
      /* 
       * CONSTRUCTOR to create new d3 chart
       * 
       * new Chart(param1,param2, param3) p1 = dataset; p2 = options object; p3 = css selector of the container element
       */
      chart0 = new Chart(json, options, '#chart-0'); // call constructor. this pattern 

    });

    function Chart(data, options, el) { // constructor

      chart = this; 
    /* ^ stashing `this` (the Chart) object away in a variable so that in can be accessed in
     * the functions below where `this` refers to something else
     */
      console.log(options);
      data = data.sort(function(a, b) { //sorting with JS prototype sort function
          if (options.asc) return a[options.sortField] - b[options.sortField]; // if options abov was to sort ascending
          return b[options.sortField] - a[options.sortField]; // if not
        });
      chart.svg = d3.select(el)
          .attr('width', 100)
          .attr('height', 100); // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult

/*
 * d3 min function runs through the dataset and finds the min valueof the field selected. d3 max does the same for max
 * the `d` parameter is one part of the magic of d3. function(d){...} in effect is shorthand for iterating over the
 * object in `data`
 */
      chart.minValue = d3.min(data, function(d) { 
        return d[options.field]
      });

      chart.maxValue = d3.max(data, function(d) { 
        return d[options.field]
      });
/*
 * d3 scale functions map the actual values (domain) to output values (range). In this case, the range is from
 * 0.1 opacity to 1 opacity in a linear fashion. d3 also handles mapping domain to value in logarithmic or square-root
 * scales
 */
      chart.scale = d3.scaleLinear().domain([chart.minValue, chart.maxValue]).range([0.1, 1]); // in v3 this was d3.scale.linear()
      /*
       * select(selector) is another part of the magic. the selected elements don't need to exist yet.
       */

      chart.svg.selectAll('rect')
        .data(data)
        .enter() // for all `rect`s that don't yet exist
        .append('rect')
        .attr('width', options.width)
        .attr('height', options.width)
        .attr('fill', '#325d88')
        .attr('fill-opacity', function(d) { // fill-opacity is a function of the value
          
          return chart.scale(d[options.field]); // takes the field value and maps it according to the scaling function defined above
        }) 
        .attr('x', function(d, i) {
          return (i * options.width + options.spacer * i) - Math.floor(i / options.columns) * (options.width + options.spacer) * options.columns;
        }) // horizontal placement is function of the index and the number of columns desired
        .attr('y', function(d, i) {
          return Math.floor(i / options.columns) * options.width + (Math.floor(i / options.columns) * options.spacer);
        }) // vertical placement function of index and number of columns. Math.floor rounds down to nearest integer
        .on('mouseover', tool_tip.show)
        .on('mouseout', tool_tip.hide);

    }

    var svg = d3.select('svg');

    var tool_tip = d3.tip()
          .attr("class", "d3-tip")
          .offset([-8, 0])
     /*
      * here the text of the tooltip is hard coded in but we'll need a human-readable field in the data to provide that text
      */
          .html(function(d) { return "Percentage of vacant housing units for rent: " + d[options.field]; });


    svg.call(tool_tip);






});