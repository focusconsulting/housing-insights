//Map projection
var projection = d3.geo.mercator()
    .scale(87238.56343084128)
    .center([-77.0144701798118, 38.89920210515231]) //projection center
    .translate([$('#mapView').width() / 2,
        $('#mapView').height() / 2]); //translate to center the map in view
  
//Generate paths based on projection
var path = d3.geo.path()
    .projection(projection);
  
//Define Colorscales for mapView
var colorScaleMap = d3.scale.ordinal()
    .domain(["T", "F"])
    .range(["#0097FF", "#c8c8c8"]);
  
//Define tooltip
var tooltip = d3.select("body").append("div").attr("class", "tooltip");
  
//Define position of the tooltip relative to the cursor
var tooltipOffset = { x: 5, y: -25 };
   
//Define function for populating bar chart
d3.csv("js/MapData.csv", function(data){

        var barChart = d3.select('#detailView')

        //Define y-scale and axis
        var yScale = d3.scale.ordinal()
                            .domain(data.map(function(d){ return d.location; }))
                            .rangeBands([0, $('#detailView').height()],
                                         .3, 0); //Includes x-axis

        var barWid = yScale.rangeBand(); //How wide does that make each bar?

        var yAxis = d3.svg.axis()
                    .scale(yScale)
                    .orient('left');

        var yAxisGrp = barChart.append('g')
                            .attr("class", "y axis")
                            .style("stroke-width", "0px")
                            .style("font-size", '10px')
                            .call(yAxis);
        //Define x-scale and axis
        console.log(d3.extent(data, function (d){ return d.value; }));
        var xScale = d3.scale.linear()
                            .domain(d3.extent(data, function (d){ return d.value; }))
                            .range([0, 30])
                            .nice(); 

        var xAxis = d3.svg.axis()
                  .scale(xScale)
                  .tickSize(5)
                  .orient("bottom");

        var xAxisGrp = barChart.append('g')
                            .attr("class", "x axis")
                            .style("stroke-width", "1px")
                            .style("font-size", '10px')
                            .call(xAxis);

        //Position and format axes
        yAxisGrp.attr("transform", "translate(" + $('#detailView').height() + "," + 0 + ")");

        xAxisGrp.attr("transform", "translate(" + $('#detailView').height() + "," + 0 + ")"); 

        d3.selectAll(".y.axis line, .x.axis line, .y.axis path, .x.axis path")
         	.style("shape-rendering","crispEdges")
         	.style("fill","none")
         	.style("stroke","#ccc");

        barChart.selectAll(".bar")
                .data(data)
                .enter()
                .append("rect")
                .classed('bar', true)
                .attr("x", 50) //plot.x here
                .attr("y", function(d,i){ return yScale(d.location); })
                .attr("width", function(d){ return xScale(d.value); })
                .attr('height', function(d){ return barWid; }); 
});

//Define function for populating mapView 
d3.json("../scripts/small_data/Neighborhood_Clusters_shapefile/Neighborhood_Clusters.geojson", function (geodata) {
var map = d3.select("#mapView").append("g").classed("DC", true)

map.selectAll("path")
    .data(geodata.features)
    .enter()
    .append("path")
    .classed("zipcodes", true)
    .attr("d", path)
    .on("mouseover", enterTooltip)
    .on("mousemove", refreshTooltip)
    .on("mouseout", exitTooltip);
  });
   
//Define functions to update tooltip location and map coloration
function enterTooltip(d, i) {
    tooltip.style("display", "block")
        .text(d.properties.NBH_NAMES);
    //.text(d.properties.zipcode);

    //d3.select(this).attr("fill", function (d, i) {
    //    return colorScaleActiveMap(d.properties.haveData);
    //});
}

function refreshTooltip() {
    tooltip.style("top", (d3.event.pageY + tooltipOffset.y) + "px")
        .style("left", (d3.event.pageX + tooltipOffset.x) + "px");
}

//Define function to remove tooltip on exit 
function exitTooltip() {
    tooltip.style("display", "none");

    //d3.select(this).attr("fill", function (d, i) {
    //    return colorScaleMap(d.properties.haveData);
    //});
}