"use strict";

var BarChart = function(chartOptions) { //
    this.extendPrototype(BarChart.prototype, BarExtension);
    ChartProto.call(this, chartOptions); 
}

BarChart.prototype = Object.create(ChartProto.prototype);

var BarExtension = {
    _setup: function(chartOptions){ 
        //namespace assignment - inside any of the functions defined below, 'this' no longer
        //refers to the chart. Therefore, we namespace 'this' to 'chart' and then always refer
        //to chart properties as chart.propertyname
        var chart = this 

        //Graph-specific attributes from chartOptions
        chart.barPadding = chartOptions.barPadding || 0.1;
        chart.percentMode = chartOptions.percentMode || false;
        chart.label = chartOptions.label || chartOptions.field; 

        //animations
        chart.delay = 200
        chart.duration = 1000

        //Add some items that won't change in the chart
        chart.yAxis = chart.svg.selectAll('.y-axis').data([0]).enter().append("g")
          .classed("y-axis",true)
          .attr("transform", "translate(" + chart.margin.left + "," + 0 + ")");
          
        chart.xAxis = chart.svg.append("g")
          .classed("x-axis",true)
          .attr("transform", "translate(" + chart.margin.left + "," + chart.innerHeight() + ")")

        //Animate data for the first time
        chart.update(chart.data);
    }, // end setupType
    _resize: function() {
        var chart = this;
        chart.yAxis
            .attr("transform", "translate(" + chart.margin.left + "," + 0 + ")")
            .transition()
            .delay(this.delay)
            .duration(this.duration);
        chart.xAxis
            .attr("transform", "translate(" + chart.margin.left + "," + chart.innerHeight() + ")")
            .transition()
            .delay(this.delay)
            .duration(this.duration);
    },
    _update: function(){
        //namespace assignment - allow access to 'this' inside child functions
        var chart = this;

        var min = d3.min(chart.data, function(d) { return d[chart.field]})
        var max = d3.max(chart.data,function(d) {return d[chart.field]})
        
        //Assigning scales within the update function assumes data is in the order we want to display - updating elements will move
        this.yScale = d3.scaleBand()
            .domain(chart.data.map(function(d) { return d[chart.label]; }))
            .range([this.innerHeight(),0])
            .padding(this.barPadding)

        
        var yScale = this.yScale;
        var xScale = d3.scaleLinear()
                .range([0,chart.innerWidth()])

        var xAxis = d3.axisBottom(xScale)
                    .ticks(3)

        var yAxis = d3.axisLeft(yScale)

        //Some percent-dependent axis esttings
        if (this.percentMode) {
            xScale.domain([0,1])
            xAxis.tickFormat(d3.format(".0%"))
        }
        else {
            xScale.domain([0,max])
            xAxis.tickFormat(d3.format(",")) //TODO look up proper format
        }
 

        this.svg.select('.x-axis')
            .transition()
            .delay(this.delay)
            .duration(this.duration)
            .call(xAxis);

        // add the y Axis
        this.svg.select('.y-axis')
            .transition()
            .delay(this.delay)
            .duration(this.duration)
                .call(yAxis);


        if (this.percentMode) {
            //Rest of the percent bars
            //var backgroundBars = d3.selectAll(this.container + ' rect.filler')
            var backgroundBars = this.innerChart.selectAll('rect.filler')
                .data(chart.data)
                .classed("update",true)

            backgroundBars.enter().append('rect')
                .classed("filler",true)
                
            //enter + update selection
            .merge(backgroundBars)
                .attr("y", function(d,i) {return yScale(d.group)})
                .attr("height", yScale.bandwidth())
                .attr("x", 0)
                .attr("width", xScale(1))

            backgroundBars.exit().remove()
        }


        //Actual quantity bars
        var bars = this.innerChart.selectAll('rect.values')
            .data(chart.data, function(d) { return d[chart.label];})
            .classed("update",true) //only existing bars

        var newBars = bars.enter().append('rect')
                .classed("values", true)                    
                .attr("x", 0)
                .attr("height", yScale.bandwidth())
                .attr("y", function(d,i) {return yScale(d.group)})
                .attr("width", 0)
                
        
        var allBars = newBars.merge(bars)
                .transition()
                    .delay(this.delay)          //Allows chart to load slightly before starting animation
                    .duration(this.duration)
                    .attr("x", 0)
                    .attr("height", yScale.bandwidth())
                    .attr("y", function(d,i) {return yScale(d.group)})
                    .attr("width", function(d) { 
                        return xScale(d[chart.field]);})
                    

        var leavingBars = bars.exit().remove()

        

    },
    //Calculated attributes accessible from all functions
    innerHeight: function(_){
        if (!arguments.length) {
            var innerHeight = (this._height - this.margin.top - this.margin.bottom)
            return innerHeight;
        }
        console.log("can't set inner height, it's calculated")
        return this;
    },
    //Calculated attributes accessible from all functions
    innerWidth: function(_){
        if (!arguments.length) {
            var innerWidth = (this._width - this.margin.left - this.margin.right)   
            return innerWidth;
        }
        console.log("can't set inner height, it's calculated")
        return this;
    }



};//end barProtoExtension



