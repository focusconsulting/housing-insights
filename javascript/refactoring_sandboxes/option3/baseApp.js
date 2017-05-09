

//This provides similar functionality to the housing-insights.js

var app = {
    dataCollection: {},

    //This is like Chart from old one
    baseChart: function(data,el,field,sortField,asc){
        //this.initialize(data,el,field,sortField,asc);
    },

    genericCharts: {} //placeholder to add more charts
}

var baseChart = function(data,el,field,sortField,asc){
        this.initialize(data,el,field,sortField,asc);
    };

baseChart.prototype = {
    data: [], //updated momentarily by initialize
    initialize: function(data,el,field,sortField,asc){
        this.data = data
    },

    extendPrototype: function(destinationPrototype, obj){
       for(var i in obj){
          destinationPrototype[i] = obj[i];
      }; 
    } 
};