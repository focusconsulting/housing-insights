(function prepareBuildingMaps(){
  'use strict'
  
  // FOR ACTION - determine how to bind building data to a building page. 
  // Will it be in the JS when the user selects a building to display (i.e. via AJAX)? 
  // Or when producing the document from a template on the server?
  
  var thisBuildingLayer,
      MapboxPortal,
      prepareGeoJSON; // FOR REVIEW: prepareGeoJSON (see below)
  
  
  // FOR REVIEW - prepareGeoJSON takes a single flat object, i.e. an object in which no
  // value is another object, and turns it into a geoJSON object based on the keys that
  // are specified to represent longitude and latitude.
  // So far this function only exists to work with Project.csv and app.dataCollection.
  // It may no longer be useful if the plan is to load geoJSON directly from the server.

  // SO FAR NOTHING CALLS THIS. Paul's goal was to use prepareGeoJSON to manipulate Project.csv 
  // after processing it within app.getData() and storing it in app.dataCollection.
  // Currently, app.getData() assumes that the data will be used in a Chart.
  // POSSIBLE SOLUTIONS: 
  // a- Make app.getData() work for both Charts and non-Chart objects (like Mapbox maps) that
  //    use the same data. Remove some parameters from app.getData, including Chart.
  // b- Keep MapboxPortals separate from the app/Chart relationship. MapboxPortals make their
  //    own requests for geoJSON objects.
  prepareGeoJSON = function(obj, longKey, latKey){
    // Some keys of the resulting geoJSON object are hard-coded (see below). In the future
    // we may want to extract them as parameters of prepareGeoJSON().
    // Coordinates are added later.
    var resultingObj = {
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [obj[longKey], obj[latKey]]        
      },
      properties: {}
    };
    
    // The 'select' call and 'for' loop iterate over any properties of obj that aren't
    // specified as longitude and latitude, adding them to the 'properties' property
    // of the resulting geoJSON object.
    var propertyKeys = Object.keys(obj).select(function(key){
      return key != longKey && key != latKey;
    });    
    
    for(var i = 0; i < propertyKeys.length; i++){
      resultingObj['properties'][propertyKeys[i]] = obj[propertyKeys[i]];
    }
    
    return resultingObj;      
  }
  
        
  // The geoJSON object in thisBuildingLayer['data'] comes from 
  // one row within '/scripts/small_data/PresCat_Export_20160401/Project.csv'.
  // This is for exploratory purposes only, pending a way to load the building information 
  // dynamically.
      
  // thisBuildingLayer is an object containing a layer source as per 
  // https://www.mapbox.com/mapbox-gl-js/style-spec/#layers
  
  thisBuildingLayer = {
    type: "geojson",
    data: {
      type: "Feature",
      geometry: { 
        type: "Point",
        coordinates: [-77.0511477, 38.89886317]
      },
    // These are some properties from '/scripts/small_data/PresCat_Export_20160401/Project.csv'.
    // So far they are just for illustration. 
      properties: { 
        Proj_Name: "St. Mary's Court", 
        Proj_Addre: "725 24th Street NW", 
        Proj_City: "Washington", 
        Proj_ST: "DC", 
        Proj_Zip: 20037, 
        Proj_Units_Tot: 140, 
        Proj_Units_Assist_Min: 140, 
        Proj_Units_Assist_Max: 140
      }
    }  
  }
  
  MapboxPortal = function (elementID){
  // So far the style url and access token come from Paul's Mapbox account.
  // FOR ACTION - find an accessToken that works for everyone.
    mapboxgl.accessToken = 'pk.eyJ1IjoicGF1bGdvdHRzY2hsaW5nIiwiYSI6ImNpejF1Y2U3MzA1ZmQzMnA4c3N4a3FkczgifQ.6W04v2jEJFkZvVhOI-yL6A'
    var map = new mapboxgl.Map({
      container: elementID,
      style: 'mapbox://styles/mapbox/streets-v9',
      center: thisBuildingLayer['data']['geometry']['coordinates'],
      zoom: 16
    });

    // Guidance on adding layers is here: https://www.mapbox.com/mapbox-gl-js/style-spec/#layers
    // The 'on()' function below appears to be a method of a Mapbox map, though there's no entry
    // for 'on()' in the Mapbox JS GL API.
    // Information on styling layers is here:
    // https://www.mapbox.com/mapbox-gl-js/style-spec/#layer-paint
    map.on('load', function(){
      map.addLayer({
        'id': "buildingLocation",
        'source': thisBuildingLayer,
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
        'source': thisBuildingLayer,
        'type': "symbol",
        'minzoom': 11,
        'layout': {
          'text-field': "{Proj_Name}",
          'text-anchor': "bottom-left"
        }
      });
    });
        
  }
  
  window.addEventListener('load', function(){
    console.log("The document has loaded!");
    new MapboxPortal('test-map');
  });
  
})();