"use strict";

var PieChartProto = function(chartOptions) { //
    this.extendPrototype(PieChartProto.prototype, PieProtoExtension);
    ChartProto.call(this, chartOptions); 
}

PieChartProto.prototype = Object.create(ChartProto.prototype);

var PieProtoExtension = {
  setupType: function(chartOptions){    
    var chart = this;
    this.radius =  Math.min( this.width - this.margin.right - this.margin.left, this.height - this.margin.top - this.margin.bottom ) / 2;
    this.svgCentered = this.svg.append('g')
      .attr('transform', function(){
        if ( chart.width - chart.margin.left - chart.margin.right < chart.height - chart.margin.top - chart.margin.bottom ) {
          return 'translate(' + ( chart.margin.left + chart.radius ) + ',' + ( chart.margin.top + chart.radius ) + ')';
        }
        return 'translate(' + chart.width / 2 + ',' + ( chart.margin.top + chart.radius ) + ')';
    })
    this.arc = d3.arc()
      .outerRadius(chart.radius)
      .innerRadius(chart.radius - chart.width / 4)
      .startAngle(0); 
    this.background = this.svgCentered  
        .append('path')
        .datum({endAngle: 2 * Math.PI})
        .style("fill", "#ddd")
        .attr("d", chart.arc);

    this.arcTween = function(newAngle) { // HT: http://bl.ocks.org/mbostock/5100636
      var chart = this;
      return function(d){
        var interpolate = d3.interpolate(d.endAngle, newAngle);
        return function(t) {
          d.endAngle = interpolate(t);
          return chart.arc(d);
        };
      };    
    },   
    
    this.setup(chartOptions);
    } 
};