"use strict";

var DonutChart = function(chartOptions) { 
    this.extendPrototype(DonutChart.prototype, DonutChartExtension);
    PieChartProto.call(this, chartOptions); 
}

DonutChart.prototype = Object.create(PieChartProto.prototype);

var DonutChartExtension = { 
  
  setup: function(chartOptions){
    
    var chart = this;

    this.countType = chartOptions.count; 

    this.totalUnits = this.countTotalUnits();

    
    chart.foreground = chart.svgCentered.append('path')
      .style("fill", '#fd8d3c')
      .datum({endAngle: Math.PI});

    chart.percentage = chart.svgCentered.append("text")
        .attr("text-anchor", "middle")
        .attr('class','pie_number')
        .attr('y',5)
        .text(d3.format(".0%")(1));

    chart.label 
        .text(chart.countType);

    chart.foreground.transition().duration(750)
      .attrTween("d", chart.arcTween(Math.PI * 2));

    
  },
  countTotalUnits: function(){
      var units = 0;
      this.data.forEach(function(datum){
        units += datum.proj_units_tot;
      });
      return units;
  },
  returnTextPercent: function(){
    /*var chart = this;    
    var textPercent;
        textPercent = d3.format(".0%")((chart.pieVariable[0].value)/(chart.pieVariable[1].value+chart.pieVariable[0].value));        
    return textPercent; */
  },
  updateSubscriber: function(msg,data){
    resultsView.charts.forEach(function(chart){
      DonutChart.prototype.update.call(chart,data);
    })
  /*  var chart = this;
    chart.foreground
      .transition().duration(750)
      .attrTween("d", chart.arcTween(chart.pieVariable[2].value * Math.PI * 2));
    chart.percentage
        .text(this.returnTextPercent());
    chart.label 
        .text(chart.field); // TODO: use meta.json to provide readable field names, or arrange for API to return them*/
  },
  update: function(filterData){
    var chart = this;
    var factor;
    if ( this.countType === 'Buildings' ) {
      factor = filterData.length / this.data.length;
    } else {
      factor = returnUnitFactor();
    }

    this.foreground.transition().duration(750)
      .attrTween("d", this.arcTween(factor * Math.PI * 2));

    this.percentage
      .text(d3.format(".0%")(factor));

    function returnUnitFactor(){
      var filteredProjects = chart.data.filter(function(datum){
        return filterData.indexOf(datum.nlihc_id) !== -1;
      });
      var unitCounts = 0;
      filteredProjects.forEach(function(project){
        unitCounts += project.proj_units_tot;
      });
      return unitCounts / chart.totalUnits;
    }
  }

};

