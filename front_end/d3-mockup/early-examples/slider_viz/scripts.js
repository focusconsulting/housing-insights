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
 
 
d3.csv("https://s3.amazonaws.com/housinginsights/raw/neighborhood_info_dc/neighborhood_clusters/nc_housing.csv", function(error, json) {
  if (error) throw error;
  
  json.forEach(function(obj) { //iterate over each object of the data array
    for (var key in obj) { // iterate over each property of the object
      if (obj.hasOwnProperty(key)) { // if key is property of obj, not prototype
        obj[key] = isNaN(+obj[key]) ? obj[key] : +obj[key]; // convert to number unless result would be NaN
      }
    }
  })
  console.log(json);
  new ChartWithSlider(json, options, '#chart-1'); // call constructor
});

function ChartWithSlider(data, options, el) { // constructor
chart = this;
console.log(options);

var tool_tip = d3.tip()             //create a tool tip using the D3 Tips library
        .attr("class", "d3-tip")
        .offset([-8, 0])
        .html(function(d) { return "Percentage of vacant housing units for rent: " + d[options.field]; });

data = data.sort(function(a, b) { //sorting with JS prototype sort function
    if (options.asc) return a[options.sortField] - b[options.sortField];
    return b[options.sortField] - a[options.sortField];
  });
chart.svg = d3.select(el)  // setting up the svg
    .attr('width', "40vw")
    .attr('height', "40vw"); // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult

  chart.minValue = d3.min(data, function(d) {
    return d[options.field]
  });
  chart.maxValue = d3.max(data, function(d) {
    return d[options.field]
  });
  chart.scale = d3.scaleLinear().domain([this.minValue, this.maxValue]).range([0.1, 1]); // in v3 this was d3.scale.linear()
  chart.svg.selectAll('rect')  // create rects in the svg and tie data to them
    .data(data)                 // this is the core process of D3
    .enter()
    .append('rect')
    .attr('width', options.width + "%")
    .attr('height', options.width + "%")
    .attr('fill', '#325d88')
    .attr('fill-opacity', function(d) {
      return chart.scale(d[options.field])
    }) // fill-opacity is a function of the value
    .attr('x', function(d, i) {
      return ((i * options.width + options.spacer * i) - Math.floor(i / options.columns) * (options.width + options.spacer) * options.columns) +"%"
    }) // horizontal placement is function of the index and the number of columns desired
    .attr('y', function(d, i) {
      return (Math.floor(i / options.columns) * options.width + (Math.floor(i / options.columns) * options.spacer)) + "%"
    }) // vertical placement function of index and number of columns. Math.floor rounds down to nearest integer
    .on('mouseover', tool_tip.show)  // attaching a tool tip to each rect
    .on('mouseout', tool_tip.hide);

  d3.select('#min').text(chart.minValue);  // fills out the min and max value divs on the page
  d3.select('#max').text(chart.maxValue);

  
  chart.svg.call(tool_tip);  // attaches the tool tip configuration to the tool tip on the rects




  function setSliderListeners(){  // inserts slider functionality
    var rail = document.getElementById('rail'),
        railStart = rail.offsetLeft ,
        railEnd = railStart + rail.offsetWidth,
        slider = document.getElementById('slider');

    rail.addEventListener('mousedown', startSlide, false); // starts the slide event


    function set_perc(e){
      return ((e.pageX-railStart)/(railEnd-railStart));  // calculates how far the slider is on the rail
    }

    function startSlide(e){                                   // updates rects, slider, and current percent
      rail.addEventListener('mousemove', moveSlide, false);   // div based on initial click on the rail
      window.addEventListener('mouseup', stopSlide, false);  
      current.innerText = (set_perc(e)*100).toFixed(0);
      slider.style.left = (set_perc(e) * 100) + '%';
      slider.setAttribute('data-percent', set_perc(e));
      updateRects();
    }

    function moveSlide(e){                                // updates everything based on mousemove
      var current = document.getElementById('current');   // over the rail
      current.innerText = (set_perc(e)*100).toFixed(0);
      slider.style.left = (set_perc(e) * 100) + '%';
      slider.setAttribute('data-percent', set_perc(e));
      updateRects();
    }

    function stopSlide(e){
      rail.removeEventListener('mousemove', moveSlide, false);  // removes slider listeners
    }                                                           // after mouseup

    function sliderPercent() {          // grabs the slider percent from the custom data-percent attribute
      return document.getElementById('slider').getAttribute('data-percent');
    }

    function breakPoint() {    // calculates the breakpoint around which the colors shift
      let min = parseFloat(document.getElementById('min').innerText),
          max = parseFloat(document.getElementById('max').innerText);
      return ((max - min) * parseFloat(sliderPercent()));
    }

    function updateRects(){    // changes the rects based on their relationship to the breakpoint
      d3.selectAll('rect').attr('fill', function(d){
          if(d[options.field] < breakPoint()){
            return 'gray';
          } else {
            return 'blue';
          }
        });
    }

}

setSliderListeners(); 

}









});