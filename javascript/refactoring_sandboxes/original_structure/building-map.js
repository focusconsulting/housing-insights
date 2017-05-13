var prepareBuildingMaps = function(buildingLat,buildingLon){
  'use strict'
  
  var buildingID;

  var datasets,
      prepareSource,
      prepareMaps,
      addCurrentBuilding,
      addRoutes,
      prepareSidebar,
      thisBuildingSource,
      ProtoLayer,
      mapboxSource,
      buildingForPage,      

      datasets = {};
  
  mapboxgl.accessToken;

  prepareMaps = function(){      
    var affordableHousingMap;
    // add affordableHousingMap sources and layers.
    
    var metroStationsMap; 
    // add metroStationsMap sources and layers.                      
  };

  //Adds single building icon and label. Encourages consistent formatting of the selected building
  addCurrentBuilding = function(map,source){};
  
  prepareSidebar = function(){
    
    ///////////////////
    //Transit sidebar
    ///////////////////
    var numBusRoutes;
    var numRailRoutes; 

    //TODO this is a pretty hacky way to do this but it lets us use the same specs as above
    //TODO should make this approach to a legend a reusable method if desired, and then
    //link the values here to the relevant attributes in the addLayer method.
    var rail_icon;
    var brgSorted;
    var rrgSorted;

  };

  addRoutes = function(id,data){};

  (function grabData(){
    var ajaxRequests;
    var maxIntervals;
    var currentInterval;
    var checkRequestsInterval;
    
    function checkRequests(){};
  })();

};
