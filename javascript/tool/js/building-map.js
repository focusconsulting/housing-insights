(function prepareBuildingMaps(){
  'use strict'
  
  // WHERE THE DATA CURRENTLY COME FROM:
  // District of Columbia Open Data, which is here: 
  //   http://opendata.dc.gov, the public housing dataset.
  // This dataset is for development purposes only.
  
  var MapboxPortal,
      datasets,
      prepareSource,
      prepareMaps,
      thisBuildingSource,
      ProtoLayer,
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
      
      // incorporate this with the 'app' object later. This will likely involve a different approach.
      datasets = {
        metroStations: {
          url: "http://opendata.dc.gov/datasets/54018b7f06b943f2af278bbe415df1de_52.geojson"
        },
        affordableHousing: {
          url: "http://opendata.dc.gov/datasets/34ae3d3c9752434a8c03aca5deb550eb_62.geojson"
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
  };
  
  // You call MapboxPortal with a ProtoLayer to ensure that source IDs are unique and that
  // sources can be called with MapboxPortal after they load.
  // This is because a Mapbox layer's 'source' property refers to an ID, rather than the source
  // itself. Binding the source itself to the same object as the layer helps keep things
  // orderly for calling MapboxPortal.
  // layerObj is an object literal that you'd use to assign properties to a Mapbox layer.
  // source is an object literal that you'd use to assign properties to any Mapbox source.
  ProtoLayer = function(layerObj, source){
    this.obj = layerObj;
    this.source = source;
  }
  
  //   The id of an html element        an array of ProtoLayer objects, which bundle 
  //                        |           an object literal for a layer with an object literal
  //                        |           for a source.
  //                        |                    |
  //                        V                    V 
  MapboxPortal = function (elementID, protoLayersArray){
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
      for(var i = 0; i < protoLayersArray.length; i++){
        // Name a new source after the layer object's 'source' property within ProtoLayer
        if(!map.getSource(protoLayersArray[i]['obj']['source'])){
          map.addSource(protoLayersArray[i]['obj']['source'], protoLayersArray[i]['source']);
        }
        // Add the layer, which now refers to a source that's been loaded into map.
        map.addLayer(protoLayersArray[i]['obj']);
      }
    });
    
  }
  
  prepareMaps = function(){
    
    var sources = {
      publicHousingSource: prepareSource(datasets['affordableHousing']['data'], true),
      thisBuildingSource: prepareSource(buildingForPage, false),
      metroStations: prepareSource(datasets['metroStations']['data'], false)
    };
        
    var targetBuildingDot = new ProtoLayer({
      'id': "thisBuildingLocation",
      'source': 'thisBuildingSource',
      'type': 'circle',
      'minzoom': 11,
      'paint': {
        'circle-color': 'red',
        'circle-stroke-width': 3,
        'circle-stroke-color': 'red',
        'circle-radius': 10
      }
    }, sources['thisBuildingSource']);
    
    var targetBuildingLabel = new ProtoLayer({
      'id': "thisBuildingTitle",
      'source': 'thisBuildingSource',
      'type': "symbol",
      'minzoom': 11,
      'layout': {
        'text-field': "{PROJECT_NAME}",
        'text-anchor': "bottom-left"
      }
    }, sources['thisBuildingSource']);
    
    var affordableHousingDots = new ProtoLayer({
			'id': "buildingLocation",
			'source': 'publicHousingSource',
			'type': "circle",
			'minzoom': 11,
			'paint': {
				'circle-color': 'rgb(120,150,255)',
				'circle-stroke-width': 3,
				'circle-stroke-color': 'rgb(150,150,150)',
				'circle-radius': 10
			}
    }, sources['publicHousingSource']);
        
    var affordableHousingLabels = new ProtoLayer({
      'id': "buildingTitle",
      'source': 'publicHousingSource',
      'type': "symbol",
      'minzoom': 11,
      'layout': {
        'text-field': "{PROJECT_NAME}",
        'text-anchor': "bottom-left"
      }
    }, sources['publicHousingSource']);
    
    var metroStationDots = new ProtoLayer({
			'id': "metroStationDots",
			'source': 'metroStations',
			'type': "circle",
			'minzoom': 11,
			'paint': {
				'circle-color': 'white',
				'circle-stroke-width': 3,
				'circle-stroke-color': 'green',
				'circle-radius': 5
			}
    }, sources['metroStations']);
    
    var metroStationLabels = new ProtoLayer({
      'id': "metroStationLabels",
      'source': 'metroStations',
      'type': "symbol",
      'minzoom': 11,
      'layout': {
        'text-field': "{NAME}",
        'text-anchor': "bottom-left"
      }
    }, sources['metroStations']);

    new MapboxPortal('affordable-housing-map', [targetBuildingDot, affordableHousingDots, affordableHousingLabels, targetBuildingLabel]);
    
    new MapboxPortal('metro-stations-map', [targetBuildingDot, metroStationDots, targetBuildingLabel, metroStationLabels]);
  };
  
  (function grabData(){
    var ajaxRequests = {};
    var maxIntervals = 10;
    var currentInterval = 0;
    var checkRequestsInterval;
    
    function checkRequests(){
      var completedRequests = Object.keys(ajaxRequests).filter(function(key){
        return ajaxRequests[key].readyState == 4;
      });
            
      if(completedRequests.length == Object.keys(ajaxRequests).length){
        clearInterval(checkRequestsInterval);
        
        for(var i in ajaxRequests){
          var response = ajaxRequests[i].responseText;
          datasets[i].data = JSON.parse(response);
        }
        prepareMaps();
      }
      currentInterval = 0;
      if(maxIntervals == currentInterval){
        clearInterval(checkRequestsInterval);
      }
    }
    for(var i in datasets){
      ajaxRequests[i] = new XMLHttpRequest();
      ajaxRequests[i].open('GET', datasets[i]['url']);
      ajaxRequests[i].send();
    }
    checkRequestsInterval = setInterval(checkRequests, 500);

  })();

})();