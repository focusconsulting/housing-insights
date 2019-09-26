"use strict";
/*
This file provides a copy-paste ready template for making a custom D3 chart that inherits from the chart-prototype. 
It sets up the core object structure of _setup, _resize, and _update functions that every chart needs to implement
Also included are some boiler plate examples of commonly needed attributes - these should be edited/removed as needed. 
*/

//Rename this variable to be your specific chart
var myCustomChart = function(container) { //
    this.extendPrototype(myCustomChart.prototype, CustomExtension);
    ChartProto.call(this, container); 
}

//Rename this prototype to match chart type above
myCustomChart.prototype = Object.create(ChartProto.prototype);

//Rename this variable to be globally unique!
var CustomExtension = {
    _setup: function(container){ 
        /*
        Add graph-specific defaults and insert one-time DOM elements like axes
        This is called from ChartProto.setup()
        */
        //namespace assignment - allow access to 'this' inside child functions
        var chart = this 


        //Assign defaults for all graph-specific items (others are set in ChartProto.setup())
        //All assignable parameters should be prefixed with _ to distinguish them from the public getter/setter method
        //Also, for every parameter added here, add a getter/setter at the bottom. 
        //Adding getter/setter methods allows method chaining. 
        chart._myCustomParameter //be sure to add a matching getter/setter below!


        //Add DOM elements that won't change in the chart. Not all charts will need this, but axes are a common example. 
        chart.yAxis = chart.svg
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

        //namespace assignment - allow access to 'this' inside child functions, like in things like: function(d){return d[chart.field]}
        var chart = this;
        

        //Draw the chart here




        //Some boiler plate stuff commonly needed in charts:

        ////////////////////////
        //Axes
        ///////////////////////

        //Scales translate from data value to pixels
        chart.xScale = d3.scaleLinear()
                .domain([0,1])
                .range([0,chart.innerWidth()])

        chart.yScale = d3.scaleLinear()
                .domain([0,1])
                .range([0,chart.innerHeight()])

        //Axes use the scales to set up a readable labeled axis with labels and tick marks
        var xAxis = d3.axisBottom(chart.xScale)
        var yAxis = d3.axisLeft(chart.yScale)

        //Apply the axis labels to the proper <g> element in the chart. 
        chart.svg.select('.x-axis')
            .transition()
            .delay(chart.delay())           //Suggest using a chart-wide delay and duration for most transitions
            .duration(chart.duration())
            .call(xAxis);
        chart.svg.select('.y-axis')
            .transition()
            .delay(chart.delay())
            .duration(chart.duration())
            .call(yAxis);


        ////////////////////////
        //SVG Elements bound to data
        ///////////////////////

        //General update pattern for D3
        //Join data to DOM elements, including any DOM elements that already exist on the page
        var shapes = this.innerChart.selectAll('rect.values')
            .data(chart.data(), function(d) { return d[chart.label()];})    //A key function makes items match to some data property instead of the order in the DOM

        //Make changes to existing DOM elements that are staying on the page
        shapes.classed("update",true)
            .attr('style','fill:gray')

        var rectSide = 20 //could be stored as chart property, but not doing in this simple example
        //Add elements that are in the data but not the page yet
        var newShapes = shapes.enter().append('rect')
            .classed("values", true)    //starting position/state goes here - note that the allShapes transition below will animate to a new state!             
            .attr("x", 0 - rectSide)
            .attr("y", 0)
            .attr("width",rectSide)
            .attr("height",rectSide)

        //Make changes that need to happen to ALL elements staying on the page (existing + new)
        var allShapes = newShapes.merge(shapes)
                .transition()
                    .delay(chart.delay())          
                    .duration(chart.duration())
                        .attr("y",100)
                        .attr("x", function(d) {return d.value})               //Existing 
                    
        var leavingShapes = shapes.exit()
                    .transition()
                        .delay(chart.delay())
                        .duration(chart.duration())
                            .attr("x", chart.innerWidth() + rectSide)
                            .attr("y",0)
                            .attr('style','fill:red')

            leavingShapes.remove()

        

    },



    /* 
    Custom Getter/Setter functions for any attributes that were initialized in the _setup function
    */
    //Don't put _ in the getter/setter method name
    myCustomParameter: function(_){
        //Custom getter setter - if a value is passed in, it assigns the value and returns the chart so that another method can be chained on
        //If no value is passed in, the currently set value is returned. This allows for one method instead of a getParam, setParam pair. 
        if (!arguments.length) return this._myCustomParameter;
        this._myCustomParameter = _;
        return this;
    }

    //Add more getter/setters as needed


}; //end specific chart Extension



