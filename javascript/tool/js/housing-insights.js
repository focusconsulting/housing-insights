'use strict';

// I'm not using ES6 syntax (e.g. const, let). Happy to do so if we determine it has enough browser support for the project.

var app = {
    dataCollection: {},
    getData: function(DATA_FILE,dataName,el,field,sortField,asc,chart,readableField){
        d3.csv(DATA_FILE, function(json) {
            json.forEach(function(obj) { // iterate over each object of the data array
                for (var key in obj) {   // iterate over each property of the object
                    if (obj.hasOwnProperty(key)) {  // forEach iterates over protypical property.
                                                    // hasOwnProperty limits to own, nonprototypical properties.
                        obj[key] = isNaN(+obj[key]) ? obj[key] : +obj[key]; // + operator converts to number unless result would be NaN
                    }
                }
            });
            app.dataCollection[dataName] = json;
            console.log(app.dataCollection);
            // publish a topic asyncronously (module allows for asynch publishing which may be faster but can cause problems)
            PubSub.publish( dataName + '/load', '' ); // using the publish/subscribe module provided in local PubSubs.js
                                                          // source: https://github.com/mroderick/PubSubJS
                                                          // param1 = topic; param 2 = message
                                                          // using here to publish that data has been loaded so that 
                                                          // other Charts using the same data can be initiated  
            chart.initialSetup(dataName,el,field,sortField,asc,readableField);
        });
    }
};
    
var Chart = function(DATA_FILE,dataName,el,field,sortField,asc,readableField) {
    this.initialize(DATA_FILE,dataName,el,field,sortField,asc,readableField); 
};

Chart.prototype = {
    data: [],
    initialize: function(DATA_FILE,dataName,el,field,sortField,asc,readableField) { // parameters will be passed by the call to the specific chart type         
        
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
            if (asc) return a[sortField] - b[sortField]; // if asc parameter in Chart constructor call is true
            return b[sortField] - a[sortField]; // if not
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

       for(var i in obj){
          destinationPrototype[i] = obj[i];
      } 
    } // end extendPrototype
}; // end Chart.prototype
