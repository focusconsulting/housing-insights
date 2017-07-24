"use strict";
/*
This file provides a copy-paste ready template for making a custom D3 chart that inherits from the chart-prototype. 
It sets up the core object structure of _setup, _resize, and _update functions that every chart needs to implement
Also included are some boiler plate examples of commonly needed attributes - these should be edited/removed as needed. 
*/

//Rename this variable to be your specific chart
var DonutChart = function(container) { //
    this.extendPrototype(myCustomChart.prototype, DonutChartExtension);
    ChartProto.call(this, container); 
}

//Rename this prototype to match chart type above
myCustomChart.prototype = Object.create(ChartProto.prototype);

//Rename this variable to be globally unique!
var DonutChartExtension = {
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


    }, // end setupType
    _resize: function() {
        /*
        Perform graph specific resize functions, like adjusting axes
        This should also work to initialize the attributes the first time
        DOM elements will typically be created in the _setup function
        */

        //namespace assignment - allow access to 'this' inside child functions
        var chart = this;


    },
    _update: function(){
        /*
        Draw the graph using the current data and settings. 
        This should draw the graph the first time, and is always run after both '_setup' and '_resize' are run
        */

        //namespace assignment - allow access to 'this' inside child functions, like in things like: function(d){return d[chart.field]}
        var chart = this;
        
        //Scales translate from data value to pixels
        chart.xScale = d3.scaleLinear()
                .domain([0,1])
                .range([0,chart.innerWidth()])

        chart.yScale = d3.scaleLinear()
                .domain([0,1])
                .range([0,chart.innerHeight()])


        ////////////////////////
        //SVG Elements bound to data
        ///////////////////////

        //General update pattern for D3
        //Join data to DOM elements, including any DOM elements that already exist on the page
        var shapes = this.innerChart.selectAll('rect.values')
            .data(chart.data(), function(d) { return d[chart.label()];})    //A key function makes items match to some data property instead of the order in the DOM


        //Add elements that are in the data but not the page yet
        var newShapes = shapes.enter().append('rect')
            .classed("values", true)    //starting position/state goes here - note that the allShapes transition below will animate to a new state!             
            //.attr etc. here

        //Make changes that need to happen to ALL elements staying on the page (existing + new)
        var allShapes = newShapes.merge(shapes)
                .transition()
                    .delay(chart.delay())          
                    .duration(chart.duration())
                        //.attr stuff here
                    
        var leavingShapes = shapes.exit()
                    .transition()
                        .delay(chart.delay())
                        .duration(chart.duration())
                            //.attr stuff here

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



