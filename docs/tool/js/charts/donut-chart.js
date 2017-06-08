"use strict";

var DonutChart = function(chartOptions) { //
    this.extendPrototype(DonutChart.prototype, DonutChartExtension);
    PieChartProto.call(this, chartOptions); 
}

DonutChart.prototype = Object.create(PieChartProto.prototype);

var DonutChartExtension = { 
  
  setup: function(chartOptions){
    var chart = this;    
    
    chart.foreground = chart.svgCentered.append('path')
      .style("fill", '#fd8d3c')
      .datum({endAngle: 0});

    chart.percentage = chart.svgCentered.append("text")
        .attr("text-anchor", "middle")
        .attr('class','pie_number')
        .attr('y',5);

    //this.update();
  },
  
  returnTextPercent: function(){
    /*var chart = this;    
    var textPercent;
        textPercent = d3.format(".0%")((chart.pieVariable[0].value)/(chart.pieVariable[1].value+chart.pieVariable[0].value));        
    return textPercent; */
  },
  update: function(){
  /*  var chart = this;
    chart.foreground
      .transition().duration(750)
      .attrTween("d", chart.arcTween(chart.pieVariable[2].value * Math.PI * 2));
    chart.percentage
        .text(this.returnTextPercent());
    chart.label 
        .text(chart.field); // TODO: use meta.json to provide readable field names, or arrange for API to return them*/
  }

};

