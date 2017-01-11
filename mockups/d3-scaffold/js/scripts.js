document.addEventListener("DOMContentLoaded", function() { // vanilla js doc ready w/ enough browswr support for this exercise

    // USING D3 v3.x
    // NOT YET USING CONSTRUCTOR METHOD
    var svg = d3.select('#chart-0')
      .attr({
        width: 600,
        height: 600
      });

    var dataSet = [51, 46, 78, 35, 97, 78, 61, 62, 45, 80, 32, 38, 20, 75, 22, 31, 36, 97, 12, 90, 84, 48, 68, 93, 13, 63, 21, 18, 23, 72, 98, 17, 90, 28, 52, 52, 65, 17, 91, 27, 12, 42, 16, 17, 29, 58, 59, 61, 47, 80, 64, 95, 69, 11, 18, 26, 69, 86, 55, 86, 27, 21, 48, 99, 70, 39, 58, 54, 99, 17, 57, 22, 82, 21, 53, 49, 55, 77, 96, 39, 56, 11, 38, 59, 49, 79, 86, 26, 12, 67, 53, 59, 84, 35, 92, 24, 69, 49, 64, 8, 15, 72, 38],
        width = 10, // size of each square
        spacer = 2, // space between each square
        columns = 8; 

    var xScale = d3.scale.linear().domain([0,d3.max(dataSet)]).range([0,1]); // in v4 this would be d3.scaleLinear() . . .

    var square = svg.selectAll('rect')
        .data(dataSet)
        .enter()
        .append('rect')
        .attr({
            width:width,
            height:width,
            fill: '#325d88',
            'fill-opacity': function(d){return xScale(d)}, // fill-opacity is a function of the value
            x: function(d,i){return (i * width + spacer *  i) - Math.floor( i / columns) * (width + spacer) * columns}, // horizontal placement is function of the index of the value and the number of columns desired
            y: function(d,i){return Math.floor(i / columns) * width + (Math.floor(i / columns) * spacer)} // vertical placement function of index and number of columns. Math.floor rounds down to nearest integer
        });

});