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

        //animations
        this.delay = 200
        this.duration = 1000

        //Add some items that won't change in the chart
        this.svg.selectAll('.y-axis').data([0]).enter().append("g")
          .classed("y-axis",true)
          .attr("transform", "translate(" + this.margin.left + "," + 0 + ")");
          
        this.svg.append("g")
          .classed("x-axis",true)
          .attr("transform", "translate(" + this.margin.left + "," + this.innerHeight() + ")")

        
        

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
        

        var min = d3.min(data, function(d) { return d[field]})
        var max = d3.max(data,function(d) {return d[field]})
        
        //Assigning here assumes data is in the order we want to display - updating elements will move
        this.yScale = d3.scaleBand()
            .domain(this.data.map(function(d) { return d[label]; }))
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



