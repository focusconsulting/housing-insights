"use strict";

var BarChart = function(container) { //
    this.extendPrototype(BarChart.prototype, BarExtension);
    ChartProto.call(this, container); 
}

BarChart.prototype = Object.create(ChartProto.prototype);

var BarExtension = {
    _setup: function(container){ 
        /*
        Add graph-specific defaults and insert one-time DOM elements like axes
        This is called from ChartProto.setup()
        */
        console.log("adding bar chart")
        //namespace assignment - allow access to 'this' inside child functions
        var chart = this 

        //Assign defaults for all graph-specific items (others are set in ChartProto.setup())
        chart._barPadding = 0.1;
        chart._percentMode = false;
        

        //Add some items that won't change in the chart
        chart.yAxis = chart.svg.selectAll('.y-axis').data([0]).enter()
            .append("g")
            .classed("y-axis",true)
        chart.xAxis = chart.svg
            .append("g")
            .classed("x-axis",true)

    }, // end setupType
    _resize: function() {
        /*
        Perform graph specific resize functions, like adjusting axes
        This should also work to initialize the attributes the first time
        DOM elements will typically be created in the _setup function
        */

        //namespace assignment - allow access to 'this' inside child functions
        var chart = this;

        chart.yAxis
            .attr("transform", "translate(" + chart.margin().left + "," + chart.margin().top + ")")

        chart.xAxis
            .attr("transform", "translate(" + chart.margin().left + "," + (chart.innerHeight()+chart.margin().top) + ")")

    },
    _update: function(){
        /*
        Draw the graph using the current data and settings. 
        This should draw the graph the first time, and is always run after both '_setup' and '_resize' are run
        */


        //namespace assignment - allow access to 'this' inside child functions
        var chart = this;

        var min = d3.min(chart.data(), function(d) { return d[chart.field()]})
        var max = d3.max(chart.data(),function(d) {return d[chart.field()]})
        
        //Assigning scales within the update function assumes data is in the order we want to display - updating elements will move
        chart.yScale = d3.scaleBand()
            .domain(chart.data().map(function(d) { return d[chart.label()]; }))
            .range([chart.innerHeight(),0])
            .padding(chart.barPadding())

        
        var yScale = chart.yScale;
        var xScale = d3.scaleLinear()
                .range([0,chart.innerWidth()])

        var xAxis = d3.axisBottom(xScale)
                    .ticks(3)

        var yAxis = d3.axisLeft(yScale)

        //Some percent-dependent axis esttings
        if (chart.percentMode()) {
            xScale.domain([0,1])
            xAxis.tickFormat(d3.format(".0%"))
        }
        else {
            xScale.domain([0,max])
            xAxis.tickFormat(d3.format(",")) //TODO look up proper format
        }

        chart.svg.select('.x-axis')
            .transition()
            .delay(chart.delay())
            .duration(chart.duration())
            .call(xAxis);

        // add the y Axis
        chart.svg.select('.y-axis')
            .transition()
            .delay(chart.delay())
            .duration(chart.duration())
            .call(yAxis);


        if (chart.percentMode()) {
            //Rest of the percent bars
            //var backgroundBars = d3.selectAll(this.container + ' rect.filler')
            var backgroundBars = this.innerChart.selectAll('rect.filler')
                .data(chart.data())
                .classed("update",true)

            backgroundBars.enter().append('rect')
                .classed("filler",true)
                
            //enter + update selection
            .merge(backgroundBars)
                .attr("y", function(d,i) {return yScale(d[chart.label()])})
                .attr("height", yScale.bandwidth())
                .attr("x", 0)
                .attr("width", xScale(1))

            backgroundBars.exit().remove()
        }


        //Actual quantity bars
        var bars = this.innerChart.selectAll('rect.values')
            .data(chart.data(), function(d) { return d[chart.label()];})
            .classed("update",true) //only existing bars

        var newBars = bars.enter().append('rect')
                .classed("values", true)                    
                .attr("x", 0)
                .attr("height", yScale.bandwidth())
                .attr("y", function(d,i) {return yScale(d[chart.label()])})
                .attr("width", 0)
                
        
        var allBars = newBars.merge(bars)
                .transition()
                    .delay(this.delay())          //Allows chart to load slightly before starting animation
                    .duration(this.duration())
                    .attr("x", 0)
                    .attr("height", yScale.bandwidth())
                    .attr("y", function(d,i) {return yScale(d.group)})
                    .attr("width", function(d) { 
                        return xScale(d[chart.field()]);})
                    

        var leavingBars = bars.exit().remove()

        

    },

    /* 
    Custom Getter/Setter functions for any attributes that were initialized in the _setup function
    */
    barPadding: function(_){
        if (!arguments.length) return this._barPadding;
        this._barPadding = _;
        return this;
    },
    percentMode: function(_){
        if (!arguments.length) return this._percentMode;
        this._percentMode = _;
        return this;
    },
    

}; //end BarExtension



/*
Example Usage - demonstrates resize, reorder, animating bar values, percentMode

//Do a demo of the chart
var apiData = {
  "data_id": "matching_projects", 
  "grouping": "ward", 
  "items": [
    {"matching": 124, "total": 350, "group": "Ward 1"}, 
    {"matching": 112, "total": 350, "group": "Ward 2"}, 
    {"matching": 12,  "total": 350, "group": "Ward 3"}, 
    {"matching": 110, "total": 350, "group": "Ward 4"}, 
    {"matching": 157, "total": 350, "group": "Ward 5"}, 
    {"matching": 122, "total": 350, "group": "Ward 6"}, 
    {"matching": 291, "total": 350, "group": "Ward 7"}, 
    {"matching": 229, "total": 350, "group": "Ward 8"}
  ]
}

//Calculate percents
var calculatePercents = function(data) {
    for (var i = 0; i < data.length; i++) {
        var d = data[i]
        d.percent = d['matching'] / d['total'] 
    };   
};

calculatePercents(apiData.items);

var demoValueChart = new BarChart('.demoValueChart')
            .width(400)
            .height(200)
            .margin({top: 20, right: 20, bottom: 20, left: 50})
            .data(apiData['items'])
            .field('matching')
            .label('group')
            .percentMode(false)
            .create()


var demoPercentChart = new BarChart('.demoPercentChart')
            .width(300)
            .height(200)
            .margin({top: 20, right: 20, bottom: 20, left: 50})
            .data(apiData['items'])
            .field('percent')
            .label('group')
            .percentMode(true)
            .create()

setTimeout(function(){
        //Change some data to demonstrate animation, both swapping and stretching
        //Important - when updating data, need a new object not a modified object to ensure object constancy (i.e. bars move if needed)
        newApiData = JSON.parse(JSON.stringify(apiData))    //make deep copy
        newApiData.items[0].group = "Ward 4";
        newApiData.items[3].group = "Ward 1";

        newApiData.items[0].matching = 350;
        newApiData.items[1].matching = 300;
        newApiData.items[2].matching = 250;
        newApiData.items[3].matching = 200;
        newApiData.items[4].matching = 150;
        newApiData.items[5].matching = 100
        newApiData.items[6].matching = 50
        newApiData.items[7].matching = 10;
        calculatePercents(newApiData.items);
        

        demoValueChart.update(newApiData.items);
        demoPercentChart.update(newApiData.items);

    }, 4000);

setTimeout(function(){
        demoValueChart.width(200)
            .height(200)
            .resize();

     }, 2000);

*/
