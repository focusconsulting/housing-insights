"use strict";

var DonutChart = function(container) { //
    this.extendPrototype(DonutChart.prototype, DonutChartExtension);
    ChartProto.call(this, container); 
}

DonutChart.prototype = Object.create(ChartProto.prototype);

var DonutChartExtension = {
    _setup: function(container){ 
        var chart = this 
        chart._chart = this

        chart._dataLabel = null;

        chart.arcTween = function(newAngle) { // HT: http://bl.ocks.org/mbostock/5100636
          return function(d){
            var interpolate = d3.interpolate(d.endAngle, newAngle);
            return function(t) {
              d.endAngle = interpolate(t);
              return chart.arc(d);
            };
          };    
        }


        chart.background = chart.innerChart 
            .append('path')
            .classed("pie-background",true)
            .datum({endAngle: 2 * Math.PI})
            .style("fill", "#ddd")

        chart.foreground = chart.innerChart.append('path')
          .classed("values",true)
          .datum({endAngle: Math.PI})       
        
        chart.percentage = chart.innerChart.append("text")
            .attr("text-anchor", "middle")
            .attr('class','pie_number')
            .attr('y',5)
            .text(d3.format(".0%")(1));

        chart.labelElement = chart.svg.append('text')
            .attr('class','pie_text')
            .attr('text-anchor','middle'); 

    }, // end setupType
    _resize: function() {
        /*
        Perform graph specific resize functions, like adjusting axes
        This should also work to initialize the attributes the first time
        DOM elements will typically be created in the _setup function
        */

        //namespace assignment - allow access to 'this' inside child functions
        var chart = this;
        chart.innerChart.attr("transform", "translate(" + (chart.innerWidth()/2 + chart.margin().left) + "," + (chart.innerHeight()/2 + chart.margin().top) +")"); // Moving the center point

        chart.arc = d3.arc()
          .outerRadius(chart.radius())
          .innerRadius(chart.radius() - chart.width() / 4)
          .startAngle(0); 
        
        chart.background.attr("d", chart.arc);

        chart.labelElement
            .attr('y', chart.height() - 5 )
            .attr('x', chart.width() / 2)

    },
    _update: function(){
        /*
        Draw the graph using the current data and settings. 
        This should draw the graph the first time, and is always run after both '_setup' and '_resize' are run
        */

        var chart = this;
        
        var percent = chart.data()[0][chart.field()] //assume data comes in form [{'field':0.9,'unusedfield':'unusedvalue'},{ignored objects after first}]
        var angle = percent * (Math.PI * 2)

        chart.foreground
            .transition()
            .duration(chart.duration())
            .attrTween("d", chart.arcTween(angle));

        chart.percentage
            .text(d3.format(".0%")(percent));

        chart.labelElement
            .text(chart.data()[0][chart.label()]);
    },

   

    dataLabel: function(_){ 
        if (!arguments.length) {
            if (this._dataLabel=== null) {
                return this.field()
            }
            else {
                return this._dataLabel; 
            }
        } 
        this._dataLabel = _;
        return this;
    },

    radius: function(_) {
        if (!arguments.length) {
            return Math.min(this.innerWidth(), this.innerHeight()) / 2; 
        }
        console.log("can't set radius, it's calculated")
        return this;
    } 

    //Add more getter/setters as needed


}; //end specific chart Extension



