"use strict";

var ChartProto = function(chartOptions) {    //chartOptions is an object, was DATA_FILE, el, field, sortField, asc, readableField                                                              
    
    this.initialize(chartOptions); 
};

ChartProto.prototype = {
    
    initialize: function(chartOptions) {
      var chart = this; 
      this.field = chartOptions.field;
      this.width = chartOptions.width;
      this.height = chartOptions.height;
      this.margin = chartOptions.margin || {top:10,right:10,bottom:10,left:10};
      this.svg = d3.select(chartOptions.container)
        .append("svg")
        .attr('width', this.width)
        .attr('height', this.height); // TODO allow margins to be passed in
      this.label = chart.svg.append('text')
        .attr('y', chart.height - 5 ) // TODO 
        .attr('x', chart.width / 2)
        .attr('class','pie_text')
        .attr('text-anchor','middle');
        
       
      chartOptions.dataRequest.callback = chartCallback;         
      controller.getData(chartOptions.dataRequest) // dataRequest is an object {name:<String>, url: <String>[,callback:<Function>]]}
      
      function chartCallback(data){
        chart.data = data.items;
        if (chartOptions.sort !== undefined ) {
          chart.data.sort(function(a, b) { 
            if (chartOptions.sort.direction === 'asc') return a[chartOptions.sort.field] - b[chartOptions.sort.field];
            return b[chartOptions.sort.field] - a[chartOptions.sort.field]; 
          });            
        }
        chart.minValue = d3.min(chart.data, function(d) { 
              return d[chartOptions.field]
        });
        chart.maxValue = d3.max(chart.data, function(d) { 
              return d[chartOptions.field]
        });
        chart.setupType(chartOptions); 
      }

    },                       
    extendPrototype: function(destinationPrototype, obj){ 
      for(var i in obj){
          destinationPrototype[i] = obj[i];
      } 
    } 
};