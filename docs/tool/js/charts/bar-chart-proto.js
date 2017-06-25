"use strict";

var BarChartProto = function(chartOptions) { //
    this.extendPrototype(BarChartProto.prototype, BarProtoExtension);
    ChartProtoStatic.call(this, chartOptions); 
}

BarChartProto.prototype = Object.create(ChartProtoStatic.prototype);

var BarProtoExtension = {
    setupType: function(chartOptions){ 
        
        //Graph-specific attributes from chartOptions
        this.barPadding = chartOptions.barPadding || 0.1;
        this.percentMode = chartOptions.percentMode || false;
        this.label = chartOptions.label || chartOptions.field; 

        //Add some items that won't change in the chart
        this.svg.selectAll('.y-axis').data([0]).enter().append("g")
          .classed("y-axis",true)
          .attr("transform", "translate(" + this.margin.left + "," + 0 + ")");
          
        this.svg.append("g")
          .classed("x-axis",true)
          .attr("transform", "translate(" + this.margin.left + "," + this.innerHeight() + ")")

        //Assigning here allows positional constancy; assumes all groups are present
        this.yScale = d3.scaleBand()
            .domain(this.data.map(function(d) { return d[chartOptions.label]; }))
            .range([this.innerHeight(),0])
            .padding(this.barPadding)

        //Animate data for the first time
        this.update(this.data);
    }, // end setupType

    update: function(data){
        //update the data stored on the chart object
        this.data = data
        
        //namespace assignment for access within child functions
        var chart = this;
        var field = this.field;
        var label = this.label;
        var yScale = this.yScale;


        var min = d3.min(data, function(d) { return d[field]})
        var max = d3.max(data,function(d) {return d[field]})


        

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
            xAxis.tickFormat(d3.format(".0%")) //TODO look up proper format
        }
 

        this.svg.select('.x-axis')
            .transition()
            .duration(500)
            .call(xAxis);

        // add the y Axis
        this.svg.select('.y-axis')
            .transition()
            .duration(500)
                .call(yAxis);


        if (this.percentMode) {
            //Rest of the percent bars
            //var backgroundBars = d3.selectAll(this.container + ' rect.filler')
            var backgroundBars = this.innerChart.selectAll('rect.filler')
                .data(data)
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
            .data(data, function(d) { return d[label];})
            .classed("update",true) //only existing bars

        var newBars = bars.enter().append('rect')
                .classed("values", true)
        
        console.log("new chart")
        var allBars = newBars.merge(bars)
                .attr("x", 0)
                .attr("height", yScale.bandwidth())
                .transition()
                    .duration(500)
                    .attr("y", function(d,i) {console.log(yScale(d.group)); return yScale(d.group)})
                    .attr("width", function(d) { 
                        return xScale(d[field]);})
                    

        var leavingBars = bars.exit().remove()

        

    },
    //Calculated attributes accessible from all functions
    innerHeight: function(_){
        if (!arguments.length) {
            var innerHeight = (this.height - this.margin.top - this.margin.bottom)
            return innerHeight;
        }
        console.log("can't set inner height, it's calculated")
        return this;
    },
    //Calculated attributes accessible from all functions
    innerWidth: function(_){
        if (!arguments.length) {
            var innerWidth = (this.width - this.margin.left - this.margin.right)   
            return innerWidth;
        }
        console.log("can't set inner height, it's calculated")
        return this;
    }

};//end barProtoExtension



