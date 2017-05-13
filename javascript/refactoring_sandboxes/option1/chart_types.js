// PG: It would be nice to reduce the number of arguments to something easier to
// memorize. 
// We still have to incorporate Bostock's guidance re: reusable charts.
// We also have to work out how to integrate this with DataObject (see data_objects.js).
var Chart = function(DATA_FILE, el, field, sortField, asc, readableField) {};

Chart.prototype = {
  data: [],
    
  initialize: function(DATA_FILE, el, field, sortField, asc, readableField) {},
  initialSetup: function(DATA_FILE,el,field,sortField,asc, readableField){
    this.data; 
    this.minValue;
    this.maxValue;
  },

  legend: function(){ //returns an HTMLElement object and its children}
}; 

// Code for defining PieCharts and inheriting from Chart from pie.js.
var PieChart = function(DATA_FILE, dataName, el, field, width, height) {};

// Code for defining SubsidtyTimelineCharts and inheriting from Chart from subsidy-timeline.js.
var SubsidyTimelineChart = function(DATA_FILE, dataName, el, field, sortField, asc, readableField, width, height, building) {};
