'use strict';

/*

************ NOTE *************
*******************************

This file  is here to keep building.html functioning as it was before the javascript refactor.
It will be deprecated once the building view is rebuilt according to the refactor. 


*/

String.prototype.hashCode = function() {
  var hash = 0, i, chr, len;
  if (this.length === 0) return hash;
  for (i = 0, len = this.length; i < len; i++) {
    chr   = this.charCodeAt(i);
    hash  = ((hash << 5) - hash) + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return 'd' + hash;
};

String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};
// This constructor stores json data fetched from AWS so that we can do various things with it,
// like convert it to geoJSON or grab its display name and other information 
// (regardless of the data source) using conventions from meta.json.
// This assumes that 'json' is an array of objects.
function APIDataObj(json){
  this.json = json;
  
  // this.geoJSON assumes that we'll be producing a FeatureCollection with Features
  // that are points. For shapes, we may want to add an argument and code that responds to it.
  // Currently this method requires us to specify the latitude and longitude fields
  // of the data within the json. If we standardize the json to always call its geospatial
  // fields 'longitude' and 'latitude', this may not be necessary.
  this.toGeoJSON = function(longitudeField, latitudeField){
    var features = json.items.map(function(element){
      return {
        'type': 'Feature',
        'geometry': {
          'type': 'Point',
          'coordinates': [+element[longitudeField], +element[latitudeField]]
        },
        'properties': element        
      }
    });
    console.log('json', json);
    return {
      'type': 'FeatureCollection',
      'features': features
    }
  }
  
}

// geoJSONPolygons = a geoJSON FeatureCollection where the Features have a 'geometry'
// object of type 'Polygon'.
// aggregateData = a json object resulting from a query for aggregate data from the 
// project's Flask API.
// zoneNamesMatch = a callback with two arguments: (a) an element within the array of 
// objects returned from an API call. and (b) a geoJSON polygon feature. The callback
// returns true if the zone name within (a) matches the zone name within (b). 
function addDataToPolygons(geoJSONPolygons, aggregateData, zoneNamesMatch){
  var modifiedPolygons = geoJSONPolygons;
  for(var i = 0; i < modifiedPolygons.features.length;i++){
    var matchingAggregateZone = (aggregateData['items'].filter(function(el){
      return zoneNamesMatch(el,modifiedPolygons.features[i]);
    }))[0];

    modifiedPolygons.features[i].properties[aggregateData.table] = (aggregateData.items.filter(function(el){
      return el.group == matchingAggregateZone.group;
    }))[0].count;
  }
  return modifiedPolygons;
}


var app = {
    dataCollection: {}, // empty object to house potentially shared data called by specific charts, see above
    
    // getInitialData exists to fetch data that we need to use as soon as possible after the DOM loads.
    
    // 'urlsObjArray' is an array of object literals, each with two keys: 'dataName' is a string that we
    // will later use as a key within app.dataCollection; and 'dataURL' is where we fetch the data
    // from. 'doAfter' is a callback where we can specify all the specific constructors to call with the 
    // data
    getInitialData: function(urlsObjArray, doAfter){
      var MAX_INTERVALS = 60,
          ajaxRequests = {},
          currentInterval = 0,
          checkRequestsInterval,
          REQUEST_TIME = 500,
          _this = this; // To resolve scoping issues
                
       function checkRequests(){
         var completedRequests = Object.keys(ajaxRequests).filter(function(key){
           return ajaxRequests[key].readyState == 4;
         });
            
         if(completedRequests.length == Object.keys(ajaxRequests).length){
         
           clearInterval(checkRequestsInterval);
        
           for(var tableName in ajaxRequests){
             var response = ajaxRequests[tableName].responseText;
             _this.dataCollection[tableName] = new APIDataObj(JSON.parse(response));
           }
           doAfter();
         }
         if(MAX_INTERVALS == currentInterval){
           clearInterval(checkRequestsInterval);
         }
         currentInterval++;
       }
       
       for(var i = 0; i < urlsObjArray.length; i++){
         ajaxRequests[urlsObjArray[i].dataName] = new XMLHttpRequest();
         ajaxRequests[urlsObjArray[i].dataName].open('GET', urlsObjArray[i].dataURL);
         ajaxRequests[urlsObjArray[i].dataName].send();
       }
       checkRequestsInterval = setInterval(checkRequests, REQUEST_TIME);

    },
    
    getData: function(DATA_FILE, el, field, sortField, asc, readableField, chart){
        d3.csv(DATA_FILE, function(json) {
            json.forEach(function(obj) { 
                for (var key in obj) {   
                    if (obj.hasOwnProperty(key)) {  // hasOwnProperty limits to own, nonprototypical properties.
                                                    
                        obj[key] = isNaN(+obj[key]) ? obj[key] : +obj[key]; // + operator converts to number unless result would be NaN
                    }
                }
            });
            var dataName = DATA_FILE.hashCode();
            app.dataCollection[dataName] = json; // adds result of fetching data to the dataCollection
            chart.initialSetup(DATA_FILE, el, field, sortField, asc, readableField);
        });
    },

    /* function to get parameter value from query string in url */

    getParameterByName: function(name, url) { // HT http://stackoverflow.com/a/901144/5701184
      if (!url) {
        url = window.location.href;
      }
      name = name.replace(/[\[\]]/g, "\\$&");
      var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
          results = regex.exec(url);
      if (!results) return null;
      if (!results[2]) return '';
      return decodeURIComponent(results[2].replace(/\+/g, " "));
  }

};
              
var Chart = function(DATA_FILE, el, field, sortField, asc, readableField) { // Chart is called by specific chart constructors
                                                                                // in other files through Chart.call(...) method
    this.initialize(DATA_FILE, el, field, sortField, asc, readableField); 
};
// calling a new Constructor creates an object with the properties defined in the <object>.prototype such as 

// the one defined below and runs the function literally defined in the constructor. for more info see, among other sources,

// the section on constructors in https://github.com/getify/You-Dont-Know-JS/blob/master/this%20%26%20object%20prototypes/ch4.md
Chart.prototype = {
    data: [],
    
    initialize: function(DATA_FILE, el, field, sortField, asc, readableField) { // parameters will be passed by the call to
                                                                                    // the specific chart type         
        
        var chart = this; // so that `this` can be passed as parameter to app.getData
        if (!app.dataCollection[DATA_FILE.hashCode()]) { // if dataCollection object assoc. with the data file
                                                        // does not exist  fetch new data
                                                        // and assign it to the app.dataCollection 
            app.getData(DATA_FILE, el, field, sortField, asc, readableField, chart);
        } else {  
            this.initialSetup(DATA_FILE, el, field, sortField, asc, readableField);
        }
    },
    initialSetup: function(DATA_FILE,el,field,sortField,asc, readableField){
       this.data = app.dataCollection[DATA_FILE.hashCode()]; 
       var data = this.data;
       
       data.sort(function(a, b) { // sorting data array with JS prototype sort function
            if (asc) return a[sortField] - b[sortField];
            return b[sortField] - a[sortField]; 
          });  
       this.minValue = d3.min(data, function(d) { 
            return d[field]
        });

       this.maxValue = d3.max(data, function(d) { 
            return d[field]
        });
       this.setup(el, field, sortField, asc, readableField); 
    },
                      
    extendPrototype: function(destinationPrototype, obj){ // using this function for inheritance. 
                                                          // extend a constructor's prototype with the keys/values in obj.
                                                          // specific chart constructors call this method 

       for(var i in obj){
          destinationPrototype[i] = obj[i];
      } 
    } 
}; 