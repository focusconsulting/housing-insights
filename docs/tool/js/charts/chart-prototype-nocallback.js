"use strict";

var ChartProtoStatic = function(chartOptions) {    //chartOptions is an object, was DATA_FILE, el, field, sortField, asc, readableField                                                              
    
    this.initialize(chartOptions); 
};

ChartProtoStatic.prototype = {
    
    initialize: function(chartOptions) {
      /*
      Template for chart options. Inherited charts can add fields. 
      chartOptions = {
        field: 'my_fieldname'
        width: 300,
        height: 300,
        margin: {top: 10, right:10, bottom:10, left:10}
        container: '#divid' //used in a d3.select statement, svg is appended to this
        data: [{my_fieldname: 100, label: 'item1'},{my_fieldname: 200, label:'item2'}]
      }
      */

      //re-assign the chartOptions onto this object
      var chart = this; 
      this.field = chartOptions.field;
      this.width = chartOptions.width;
      this.height = chartOptions.height;
      this.margin = chartOptions.margin || {top:10,right:10,bottom:10,left:10};
      this.data = chartOptions.data;
      this.container = chartOptions.container;

      //Calculated fields as necessary
      chart.minValue = d3.min(chart.data, function(d) { 
            if (chartOptions.field) return d[chartOptions.field];
              return null;
      });
      chart.maxValue = d3.max(chart.data, function(d) { 
            if (chartOptions.field) return d[chartOptions.field];
            return null;
      });

      //Set up basic graph stuff
      this.svg = d3.select(chartOptions.container)
        .append("svg")
        .attr('width', this.width)
        .attr('height', this.height); // TODO allow margins to be passed in
      this.innerChart = this.svg.append('g')
            .classed("bar-chart",true)
            .attr("transform", "translate(" + this.margin.left + "," + 0 + ")");

      //Call the chart-specific setup function for continued setup
      if (typeof chart.setupType === "function"){ chart.setupType(chartOptions); }

    },                       
    extendPrototype: function(destinationPrototype, obj){ 
      for(var i in obj){
          destinationPrototype[i] = obj[i];
      } 
    },
    sort: function(field, direction) {
        chart.data.sort(function(a, b) { 
          if (direction === 'asc') return a[chartOptions.sort.field] - b[chartOptions.sort.field];
          return b[chartOptions.sort.field] - a[chartOptions.sort.field]; 
        });             
    }
};