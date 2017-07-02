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

        //namespace assignment - allow access to 'this' inside child functions
        var chart = this 

        //Assign defaults for all graph-specific items (others are set in ChartProto.setup())
        chart._barPadding = 0.1;
        chart._percentMode = false;
        chart._label = null //"field" will be returned as placeholder by getter if _label is null

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
            .attr("transform", "translate(" + chart.margin().left + "," + 0 + ")")
            .transition()
            .delay(this.delay())
            .duration(this.duration());
        chart.xAxis
            .attr("transform", "translate(" + chart.margin().left + "," + chart.innerHeight() + ")")
            .transition()
            .delay(this.delay())
            .duration(this.duration());
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


    //Calculated attributes accessible from all functions
    innerHeight: function(_){
        if (!arguments.length) {
            var innerHeight = (this._height - this.margin().top - this.margin().bottom)
            return innerHeight;
        }
        console.log("can't set inner height, it's calculated")
        return this;
    },
    //Calculated attributes accessible from all functions
    innerWidth: function(_){
        if (!arguments.length) {
            var innerWidth = (this._width - this.margin().left - this.margin().right)   
            return innerWidth;
        }
        console.log("can't set inner height, it's calculated")
        return this;
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
    label: function(_){
        if (!arguments.length) {
            //Return a default label if none exists yet
            if (this._label == null) return this._field;
            return this._label
        };
        this._label = _;
        return this;
    },

}; //end BarExtension



