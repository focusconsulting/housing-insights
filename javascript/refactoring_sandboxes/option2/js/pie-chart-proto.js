"use strict";

var PieChartProto = function(chartOptions) { //
    ChartProto.call(this, chartOptions); 
    this.extendPrototype(PieChartProto.prototype, PieProtoExtension);
}

PieChartProto.prototype = Object.create(ChartProto.prototype);

var PieProtoExtension = {
  setupType: function(chartOptions){    
    var chart = this;
    this.radius =  Math.min(this.width, this.height) / 2;
    this.arc = d3.arc()
      .outerRadius(chart.radius - chart.width/20)
      .innerRadius(chart.radius - chart.width/4)
      .startAngle(0); // TODO set programmatically
    this.background = this.svg  
        .append('path')
        .datum({endAngle: 2 * Math.PI})
        .style("fill", "#ddd")
        .attr("d", chart.arc);

    this.setup(chartOptions);
    } 
};