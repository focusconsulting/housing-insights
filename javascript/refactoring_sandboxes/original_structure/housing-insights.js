'use strict';

String.prototype.hashCode = function(){};

String.prototype.capitalizeFirstLetter = function(){};
function APIDataObj(json){
  this.json = json;
  this.toGeoJSON = function(longitudeField, latitudeField){
    var features;
  }
}

function addDataToPolygons(geoJSONPolygons, aggregateData, zoneNamesMatch){};

var app = {
  dataCollection: {}, 
  getInitialData: function(urlsObjArray, doAfter){
    var MAX_INTERVALS,
        ajaxRequests,
        currentInterval,
        checkRequestsInterval,
        REQUEST_TIME,
        _this;
              
    function checkRequests(){
      var completedRequests;
    }
  },
  
  getData: function(DATA_FILE, el, field, sortField, asc, readableField, chart){
    var dataName;
  },

  getParameterByName: function(name, url){}
};
              
var Chart = function(DATA_FILE, el, field, sortField, asc, readableField) {};

Chart.prototype = {
  data: [],
    
  initialize: function(DATA_FILE, el, field, sortField, asc, readableField) {},
  initialSetup: function(DATA_FILE,el,field,sortField,asc, readableField){
    this.data; 
    this.minValue;
    this.maxValue;
  },
                      
  extendPrototype: function(destinationPrototype, obj){ } 
}; 
