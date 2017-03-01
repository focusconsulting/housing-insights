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
      grabData,
      prepareSource,
      prepareMaps,
      thisBuildingSource,
      mapboxSource,
  // NOTE: Until we have a backend that identifies the building a user has chosen to look at
  // (or accomplish this with AJAX), buildingForPage specifies the building that the page is
  // based around and points to dataset['features'][0];
      buildingForPage;
  
  grabData = function(callback){
    var req = new XMLHttpRequest();
    req.open('GET', DATASET_URL);
    req.send();
    req.onreadystatechange = function(){
      if(req.readyState == 4){
        return callback(req.responseText);
      }
    }
  }
  
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

    // FOR ACTION - we will need to change this assignment Of dataset once we start using other datasets.
    dataset = JSON.parse(ajaxResponseText);
    
    // FOR ACTION - we will need another way to specify the building that is the subject of the building page.
    buildingForPage = dataset['features'][0];
    
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
    
  grabData(prepareMaps);
  
})();