"use strict";

var ChartProto = function(chartOptions) {    //chartOptions is an object, was DATA_FILE, el, field, sortField, asc, readableField                                                              
    this.setup(chartOptions); 
};

ChartProto.prototype = {
    update: function(data){
      /*This is the public method used to call the private _update method of each chart
      
      Every chart that inherits from ChartProto should include an _update method, which 
      redraws the inner contents of the chart when needed. When the _update method is called, 
      it uses this.data as the basis of the drawing. 

      This public method ensures a consistent approach to the update method for all charts:
      Users can call the method with or without new data - if no data is passed, the previously
      used data will be used. Typically this will occur when the user has updated some other 
      property, such as 'field' or some other setting. 

      When using method chaining to update the properties of the graph, use the update() function
      to trigger the changes in the graph itself. 
      */
      var chart = this
      if (arguments.length) {
        this.data = data;

        //Calculated fields as necessary
        this.minValue = d3.min(this.data, function(d) { 
              if (chart.field) return d[chart.field];
              return null;
        });
        this.maxValue = d3.max(this.data, function(d) { 
              if (chart.field) return d[chart.field];
              return null;
        });

      };

      this._update();
    },
    resize: function(){
      var chart = this;
      chart.svg
        .attr('width', chart._width)
        .attr('height', chart._height)
        .transition()
        .delay(this.delay)
        .duration(this.duration)

      chart.innerChart.attr("transform", "translate(" + this.margin.left + "," + 0 + ")");

      if (typeof chart._resize === "function"){ chart._resize(); };
      var temp_duration = chart.duration
      var temp_delay = chart.delay
      chart.duration = 0
      chart.delay = 0
      
      chart.update();

      chart.duration =temp_duration
      chart.delay = temp_delay

    },
    setup: function(chartOptions) {
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
      chart.field = chartOptions.field;
      chart._width = chartOptions.width;
      chart._height = chartOptions.height;
      chart.margin = chartOptions.margin || {top:10,right:10,bottom:10,left:10};
      chart.data = chartOptions.data;
      chart.container = 'chartOptions.container';

      //Set up basic graph stuff
      this.svg = d3.select(chartOptions.container)
        .append("svg")
        .attr('width', chart._width)
        .attr('height', chart._height); // TODO allow margins to be passed in
      this.innerChart = this.svg.append('g')
            .classed("bar-chart",true)
            .attr("transform", "translate(" + this.margin.left + "," + 0 + ")");

      //Call the chart-specific setup function for continued setup
      if (typeof chart._setup === "function"){ chart._setup(chartOptions); }

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
    },
    width: function(_){
        if (!arguments.length) return this._width;
        this._width = _;
        return this;
    },
    height: function(_){
        if (!arguments.length) return this._height;
        this._height = _;
        return this;
    }
};











/*
*********************************************************************************************************



This approach is deprecated! Instead, use the ChartProto object that does not have a callback in it
Maintained here until refactoring is completed


*********************************************************************************************************
*/

var ChartProtoCallback = function(chartOptions) {    //chartOptions is an object, was DATA_FILE, el, field, sortField, asc, readableField                                                              
    
    this.initialize(chartOptions); 
};

ChartProtoCallback.prototype = {
    
    initialize: function(chartOptions) {
      chartOptions.dataRequest.callback = chartCallback;  

      var chart = this; 
      this.field = chartOptions.field;
      chart.width = chartOptions.width;
      chart.height = chartOptions.height;
      this.margin = chartOptions.margin || {top:10,right:10,bottom:10,left:10};
      this.svg = d3.select(chartOptions.container)
        .append("svg")
        .attr('width', chart.width)
        .attr('height', this.height); // TODO allow margins to be passed in
      this.label = chart.svg.append('text')
        .attr('y', chart._height - 5 ) // TODO 
        .attr('x', chart._width / 2)
        .attr('class','pie_text')
        .attr('text-anchor','middle'); 
    
      controller.getData(chartOptions.dataRequest); // dataRequest is an object {name:<String>, url: <String>[,callback:<Function>]]}
      function chartCallback(data){
        console.log('chartProto callback',chart);
        chart.data = data.items;
        if (chartOptions.sort !== undefined ) {
          chart.data.sort(function(a, b) { 
            if (chartOptions.sort.direction === 'asc') return a[chartOptions.sort.field] - b[chartOptions.sort.field];
            return b[chartOptions.sort.field] - a[chartOptions.sort.field]; 
          });            
        }
        chart.minValue = d3.min(chart.data, function(d) { 
              if (chartOptions.field) return d[chartOptions.field];
                return null;
        });
        chart.maxValue = d3.max(chart.data, function(d) { 
              if (chartOptions.field) return d[chartOptions.field];
              return null;
        });
        console.log(chart.setupType);
        // The below 'if' block is necessary because SubsidyTimlineChart cannot access its own setupType function during the necessary ChartProto.call() call.
        if (typeof chart.setupType === "function"){ console.log('calling setupType'); chart.setupType(chartOptions); }
      }

    },                       
    extendPrototype: function(destinationPrototype, obj){ 
      for(var i in obj){
          destinationPrototype[i] = obj[i];
      } 
    } 
};