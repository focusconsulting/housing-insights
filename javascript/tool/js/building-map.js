(function(){
  'use strict'
  
  // FOR ACTION - determine how to bind building data to a building page. 
  // Will it be in the JS when the user selects a building to display (i.e. via AJAX)? 
  // Or when producing the document from a template on the server?
  
  var thisBuildingLayer,
      MapboxPortal;
      
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
  // FOR ACTION, ERROR TO FIX - currently receiving error message, 'Error: Style is not 
  // done loading' from mapbox-gl.js:127.
    map.addLayer({
      id: "buildingLocation",
      source: thisBuildingLayer,
      type: "circle",
      minzoom: 11,
    });
  
  }
  
  window.addEventListener('load', function(){
    console.log("The document has loaded!");
    new MapboxPortal('test-map');
  });
  
})();