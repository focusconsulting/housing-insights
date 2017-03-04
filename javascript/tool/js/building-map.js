(function prepareBuildingMaps(){
  'use strict'
  
  // WHERE THE DATA CURRENTLY COME FROM:
  // District of Columbia Open Data, which is here: 
  //   http://opendata.dc.gov, the public housing dataset.
  // This dataset is for development purposes only.
  
  var MapboxPortal,
      DATASET_URL = "http://opendata.dc.gov/datasets/34ae3d3c9752434a8c03aca5deb550eb_62.geojson",
      // dataset will likely be temporary, given that we will use other datasets!
      dataset,
      prepareSource,
      prepareMaps,
      thisBuildingSource,
      mapboxSource,
  // NOTE: Until we have a backend that identifies the building a user has chosen to look at
  // (or accomplish this with AJAX), buildingForPage specifies the building that the page is
  // based around this object literal, which is taken from the first geoJSON feature
  // in the Public Housing dataset from Open Data DC. Currently using an object literal because
  // This information will be available before any AJAX requests to an external data 
  // source/our own database.
      buildingForPage = { 
        "type": "Feature",
        "properties": { 
          "OBJECTID":2,
          "MAR_WARD": "WARD 6",
          "ADDRESS": "1115 H ST NE, WASHINGTON, DISTRICT OF COLUMBIA 20002",
          "PROJECT_NAME":"1115 H STREET NE (WOOLWORTH CONDO)",
          "STATUS_PUBLIC":"COMPLETED 2015 TO DATE",
          "AGENCY_CALCULATED":"DMPED DHCD",
          "REPORT_UNITS_AFFORDABLE":"4",
          "LATITUDE":38.89995096, 
          "LONGITUDE":-76.99087487,
          "ADDRESS_ID":311081,
          "XCOORD":400791.55,
          "YCOORD":136899.86000000002,
          "FULLADDRESS":"1115 H STREET NE",
          "GIS_LAST_MOD_DTTM":
          "2017-02-27T04:00:37.000Z"
        },
        "geometry": {
          "type": "Point",
          "coordinates":[-76.99087714595296,38.89995841328189]
        }
      };
  
  
  // The below function turns a geoJSON object into a source object for Mapbox maps.
  // The second argument determines whether to exclude the building page's target
  // building from the data.
  // FOR REVIEW - prepareSource seems to want to be a constructor.
  //                     geoJSON object    boolean
  prepareSource = function(dat, excludeThisBuilding){
    var dat = dat;
        
    if(excludeThisBuilding && dat['type'] == 'FeatureCollection'){ 
      dat['features'] = dat['features'].filter(function(element){
      // The assumption here is that a given feature will be identical to the target building
      // if it has the exact same coordinates.
        return (
          element['geometry']['coordinates'][0] != buildingForPage['geometry']['coordinates'][0] &&
          element['geometry']['coordinates'][1] != buildingForPage['geometry']['coordinates'][1]
        )
      });
    }
    return {
      type: 'geojson',
      data: dat
    }
  }
  
  prepareMaps = function(ajaxResponseText){
    console.log("prepareMaps has been called!");

    // FOR ACTION - we will need to change this assignment Of dataset once we start using other datasets.
    dataset = JSON.parse(ajaxResponseText);
    
    console.log(dataset['features'][0]);
    mapboxSource = prepareSource(dataset, true);
    thisBuildingSource = prepareSource(buildingForPage, false);

    
    new MapboxPortal('test-map', function(map){
          
      map.addLayer({
        'id': "buildingLocation",
        'source': mapboxSource,
        'type': "circle",
        'minzoom': 11,
        'paint': {
          'circle-color': 'rgb(120,150,255)',
          'circle-stroke-width': 3,
          'circle-stroke-color': 'rgb(150,150,150)',
          'circle-radius': 10
        }
      });
      map.addLayer({
        'id': "buildingTitle",
        'source': mapboxSource,
        'type': "symbol",
        'minzoom': 11,
        'layout': {
          'text-field': "{PROJECT_NAME}",
          'text-anchor': "bottom-left"
        }
      });
    });
  }

  // The MapboxPortal constructor inserts a Mapbox map into element with elementID.
  // It always adds certain layers (the dot and label for the building-of-interest).
  // For additional layers, name a function in onloadCAllback. The function will
  // take the Mapbox map as an argument. 
  MapboxPortal = function (elementID, onloadCallback){
    console.log("There's a new MapboxPortal");
    console.log("buildingForPage", buildingForPage);
  // So far the style url and access token come from Paul's Mapbox account.
  // FOR ACTION - find an accessToken that works for everyone.
    mapboxgl.accessToken = 'pk.eyJ1IjoicGF1bGdvdHRzY2hsaW5nIiwiYSI6ImNpejF1Y2U3MzA1ZmQzMnA4c3N4a3FkczgifQ.6W04v2jEJFkZvVhOI-yL6A'
    var map = new mapboxgl.Map({
      container: elementID,
      style: 'mapbox://styles/mapbox/streets-v9',
      center: buildingForPage['geometry']['coordinates'],
      zoom: 16
    });
    
    // Guidance on adding layers is here: https://www.mapbox.com/mapbox-gl-js/style-spec/#layers
    // The 'on()' function below appears to be a method of a Mapbox map, though there's no entry
    // for 'on()' in the Mapbox JS GL API.
    // Information on styling layers is here:
    // https://www.mapbox.com/mapbox-gl-js/style-spec/#layer-paint
    map.on('load', function(){
      
      map.addLayer({
        'id': "thisBuildingLocation",
        'source': thisBuildingSource,
        'type': 'circle',
        'minzoom': 11,
        'paint': {
          'circle-color': 'red',
          'circle-stroke-width': 3,
          'circle-stroke-color': 'red',
          'circle-radius': 10
        }
      });
      
      map.addLayer({
        'id': "thisBuildingTitle",
        'source': thisBuildingSource,
        'type': "symbol",
        'minzoom': 11,
        'layout': {
          'text-field': "{PROJECT_NAME}",
          'text-anchor': "bottom-left"
        }
      });
      
      if(onloadCallback){ onloadCallback(map); }
      
    });
        
  }
    
   // it looks like grabData isn't being called! 
   // This might have to do with the mapbox error I'm getting: 't.classList is undefined'
  (function grabData(callback){
    var req = new XMLHttpRequest();
    console.log(callback);
    console.log("grabData is being called!");
    req.open('GET', DATASET_URL);
    req.send();
    req.onreadystatechange = function(){
      if(req.readyState == 4){
        return callback(req.responseText);
      }
    }
  })(prepareMaps);
})();