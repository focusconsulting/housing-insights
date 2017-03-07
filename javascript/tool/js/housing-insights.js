'use strict';

/*
 *  This file contains the methods and variables common to all d3 charts for housing insights. Specific charts
 *  are built in separate files with constructors that prototypically inherit from the Chart constructor. If prototypical
 *  inheritance is new to you, check out https://github.com/getify/You-Dont-Know-JS/blob/master/this%20%26%20object%20prototypes/ch5.md.
 *  (among other sources). The Chart constructor is not called directly. Only specific chart constructors, like MovingBlockChart 
 *  (in moving-blocks.js) are called.
 *
 *  Contributors can refer to moving-block.js for an example of how to inherit from Chart in this file and call specific
 *  charts to be rendered.
 *
 *  Pages loading this script will have available an `app` object which itself has a `dataCollection` object. When a chart
 *  is constructed from a data file, the json object resulting from loading that data is added to the `dataCollection` object.
 *  This way, any subsequent charts that use the same data can refer to the existing data object by setting the DATA_FILE parameter
 *  of the specific chart's constructor to NULL and the dataName parameter to the existing object in the dataCollection. The second
 *  MovingBlockChart constructor in moving-block.js is an exampe of this. It uses the same data object as the first.
 *
 *  Other things to note:
 *
 *  1. The PubSub (publish/subscribe) module simplifies how we can connect events and the actions we want to occur as a result
 *  of that action. The module is provided by PubSub.js (MIT licence: https://github.com/mroderick/PubSubJS). Any function can
 *  publish an event (aka topic, aka msg), and any other function can be subscribed to that event. The app.getData method below,
 *  for instance, publishes an event when a data object is loaded (when the d3.csv function in complete). Any function subscribed
 *  to that event will then fire. In moving-blocks.js, the second MovingBlockChart constructor is in a function subscribed to the
 *  that event and so only fires after the data object it needs exists.
 *
 *  2. The extendPrototype method of the Chart constructor is basically a helper function that allows us to easily and cleanly add
 *  methods to specfic chart types in addition to the shared prototype from Chart. It's defined here in the shared Chart "class"
 *  but called in the specific constructors.
 */

// I'm not using ES6 syntax (e.g. const, let). Happy to do so if we determine it has enough browser support for the project.

var app = {
    dataCollection: {}, // empty object to house potentially shared data called by specific charts, see above
    getData: function(DATA_FILE,dataName,el,field,sortField,asc,chart,readableField){
        d3.csv(DATA_FILE, function(json) {
            json.forEach(function(obj) { 
                for (var key in obj) {   
                    if (obj.hasOwnProperty(key)) {  // forEach iterates over protypical property.
                                                    // hasOwnProperty limits to own, nonprototypical properties.
                        obj[key] = isNaN(+obj[key]) ? obj[key] : +obj[key]; // + operator converts to number unless result would be NaN
                    }
                }
            });
            app.dataCollection[dataName] = json; // adds result of fetching data to the dataCollection
            console.log(app.dataCollection);
           
            PubSub.publish( dataName + '/load', '' ); // using the publish/subscribe module provided in local PubSubs.js
                                                          // param1 = topic; param 2 = message
                                                          // using here to publish that data has been loaded so that 
                                                          // other Charts using the same data can be initiated  
            chart.initialSetup(dataName,el,field,sortField,asc,readableField);
        });
    }
};
              
var Chart = function(DATA_FILE,dataName,el,field,sortField,asc,readableField) { // Chart is called by specific chart constructors
                                                                                // in other files through Chart.call(...) method
    this.initialize(DATA_FILE,dataName,el,field,sortField,asc,readableField); 
};
// calling a new Constructor creates an object with the properties defined in the <object>.prototype such as 
// the one defined below and runs the function literally defined in the constructor. For more info see, among other sources,
// the section on constructors in https://github.com/getify/You-Dont-Know-JS/blob/master/this%20%26%20object%20prototypes/ch4.md
Chart.prototype = {
    data: [],
    initialize: function(DATA_FILE,dataName,el,field,sortField,asc,readableField) { // parameters will be passed by the call to
                                                                                    // the specific chart type         
        
        var chart = this; // so that `this` can be passed as parameter to app.getData
        if (DATA_FILE) { // if DATA_FILE param is not null, fetch new data
                         // and assign it to the app.dataCollection under name dataName
            app.getData(DATA_FILE,dataName,el,field,sortField,asc,chart,readableField);
        } else {         // if DATA_FILE is null proceed to intialSetup where data is defined as existing array
                         // with name dataName in the app.dataCollection object
            this.initialSetup(dataName,el,field,sortField,asc,readableField);
        }
    },
    initialSetup: function(dataName,el,field,sortField,asc,readableField){
       console.log(app.dataCollection[dataName]);
       this.data = app.dataCollection[dataName]; 
       var data = this.data;
       
       data.sort(function(a, b) { // sorting data array with JS prototype sort function
            if (asc) return a[sortField] - b[sortField];
            return b[sortField] - a[sortField]; 
          });  
       this.minValue = d3.min(data, function(d) { // d3.min iterates through datums (d) and return the smallest
            return d[field]
        });

       this.maxValue = d3.max(data, function(d) { // d3.max iterates through datums (d) and return the largest
            return d[field]
        });
       this.setup(el, field, sortField, asc, readableField); 
console.log(this.minValue);
console.log(this.maxValue);
    },
                      // ex: MovingBlockChart.prototype (param[0])
    extendPrototype: function(destinationPrototype, obj){ // using this function for inheritance. 
                                                          // extend a constructor's prototype with the keys/values in obj.
                                                          // specific chart constructors call this method 

       for(var i in obj){
          destinationPrototype[i] = obj[i];
      } 
    } // end extendPrototype
}; // end Chart.prototype
