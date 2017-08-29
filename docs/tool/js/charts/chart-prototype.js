"use strict";

var ChartProto = function(container) {    //chartOptions is an object, was DATA_FILE, el, field, sortField, asc, readableField                                                              
    this.setup(container); 
    return this;
};

ChartProto.prototype = {
    create: function(){
      /*
      This method is called to trigger drawing of the chart once all initial properties have been 
      set using method chaining. Example:

      myChart = new ChartProto('.myContainerSelector')
                .width(500)
                .height(200)
                .create()
      */
      var chart = this
      //resize performs all the stuff needed to draw the chart the first time
      chart.resize()

      //Allows variable assignment with a method chain that conclues in create()
      return chart

    },
    setup: function(container) {
      /*
      setup initializes all the default parameters, and create the container objects that are only created once. 
      This method is run automatically when a new object is created

      Any chart that inherits from this prototype should have a _setup method, which is called at the end of this function
      */

      var chart = this; 

      //Setup defaults
      chart._data = []
      chart._field = null;
      chart._label = null //"field" will be returned as placeholder by getter if _label is null
      chart._width = 400;
      chart._height = 300;
      chart._margin = {top:10,right:10,bottom:10,left:10};
      chart._container = container

      chart._delay = 200
      chart._duration = 1000

      //Create graph objects needed
      chart.svg = d3.select(chart.container())
        .append("svg")
        .attr('width', chart.width())
        .attr('height', chart.height());

      chart.innerChart = this.svg.append('g')
            .classed("chart",true)

      //Call the chart-specific setup function for continued setup
      if (typeof chart._setup === "function"){ chart._setup(); }

    },
    resize: function(){
      /*
      Anything that needs to be changed on resize should go in here. 
      Note, this function also sets up the initial sizes of these elements because
      it is run the first time the graph is created as well. 

      Note, resize also calls update(), because anything that needs to change in update
      also needs to be changed in resize. 

      Inherited charts should have a _resize function that is called at the end of this public method
      */

      var chart = this;
      chart.svg
        .attr('width', chart._width)
        .attr('height', chart._height)
        .transition()
        .delay(chart.delay())
        .duration(chart.duration())

      chart.innerChart.attr("transform", "translate(" + this.margin().left + "," + this.margin().top + ")");

      if (typeof chart._resize === "function"){ chart._resize(); };
      
      //Make the resize happen instantaneously - necessary when update uses transitions for normal updates
      var old_duration = chart.duration()
      var old_delay = chart.delay()
      chart.duration(0)
      chart.delay(0)
      
      chart.update();

      //Reset the transition settings
      chart.duration(old_duration)
      chart.delay(old_delay)

    }, 
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

        chart.data(data);

        //Calculated fields as necessary
        //TODO maybe move this into the data getter/setter?
        this.minValue = d3.min(chart.data(), function(d) { 
              if (chart.field()) return d[chart.field()];
              return null;
        });
        this.maxValue = d3.max(chart.data(), function(d) { 
              if (chart.field()) return d[chart.field()];
              return null;
        });

      };

      this._update();
    },      

    extendPrototype: function(destinationPrototype, obj){ 
      /*
      Convenience function for merging prototypes

      Example usage:
      var BarChart = function(container) { //
          this.extendPrototype(BarChart.prototype, BarExtension);
          ChartProto.call(this, container); 
      }
      */

      for(var i in obj){
          destinationPrototype[i] = obj[i];
      } 
    },

    //TODO not used currently
    sort: function(field, direction) {
        chart.data.sort(function(a, b) { 
          if (direction === 'asc') return a[chartOptions.sort.field] - b[chartOptions.sort.field];
          return b[chartOptions.sort.field] - a[chartOptions.sort.field]; 
        });             
    },

    //Calculated attributes accessible from all functions
    innerHeight: function(_){
        if (!arguments.length) {
            var innerHeight = (this._height - this.margin().top - this.margin().bottom)
            return innerHeight;
        }
        console.log("can't set inner height, it's calculated")
        return this;
    },
    //Calculated attributes accessible from all functions
    innerWidth: function(_){
        if (!arguments.length) {
            var innerWidth = (this._width - this.margin().left - this.margin().right)   
            return innerWidth;
        }
        console.log("can't set inner height, it's calculated")
        return this;
    },


    /*
    Custom getter/setters for chart proto properties
    */
    data: function(_){
        if (!arguments.length) return this._data;
        this._data = _;
        return this;
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
    },

    //Name of the key in the data object to be used for the primary numeric data, e.g. "value" with data of shape [{'id':'point 1', 'value': 100 }]
    field: function(_){
        if (!arguments.length) return this._field;
        this._field = _;
        return this;
    },
    //Name of the key in the data object to be used for the displayed name of a data point, e.g. "id" with data of shape [{'id':'point 1', 'value': 100 }]
    label: function(_){
        if (!arguments.length) {
            //Return a default label if none exists yet
            if (this._label == null) return this._field;
            return this._label
        };
        this._label = _;
        return this;
    },
    margin: function(_){
        if (!arguments.length) return this._margin;
          for (var key in _ ) {
            this._margin[key] = _[key]
          }
        return this;
    },
    container: function(_){
        if (!arguments.length) return this._container;
        this._container = _;
        return this;
    },
    delay: function(_){
        if (!arguments.length) return this._delay;
        this._delay = _;
        return this;
    },
    duration: function(_){
        if (!arguments.length) return this._duration;
        this._duration = _;
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
        .attr('y', chart.height - 5 ) // TODO 
        .attr('x', chart.width / 2)
        .attr('class','pie_text')
        .attr('text-anchor','middle'); 

      controller.getData(chartOptions.dataRequest); // dataRequest is an object {name:<String>, url: <String>[,callback:<Function>]]}

      function chartCallback(data){
        console.log('chartProto callback',chart);
        chart.data = data.objects;
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