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
        affordableHousing: {
          url: "http://opendata.dc.gov/datasets/34ae3d3c9752434a8c03aca5deb550eb_62.geojson",
          data: {}
        },
        metroStations: {
          url: "http://opendata.dc.gov/datasets/54018b7f06b943f2af278bbe415df1de_52.geojson",
          data: {}
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
  
  // The MapboxPortal constructor inserts a Mapbox map into element with elementID.
  // It always adds certain layers (the dot and label for the building-of-interest).
  // For additional layers, name a function in onloadCAllback. The function will
  // take the Mapbox map as an argument. 
  MapboxPortal = function (elementID, layersArray){
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
      for(var i = 0; i < layersArray.length; i++){
        map.addLayer(layersArray[i]);
      }
    });          
  }
  
  prepareMaps = function(){
    
    var sources = {
      publicHousingSource: prepareSource(datasets['affordableHousing']['data'], true),
      thisBuildingSource: prepareSource(buildingForPage, false),
      metroStations: prepareSource(datasets['metroStations']['data'], false)
    };
    
    var targetBuildingDot = {
      'id': "thisBuildingLocation",
      'source': sources['thisBuildingSource'],
      'type': 'circle',
      'minzoom': 11,
      'paint': {
        'circle-color': 'red',
        'circle-stroke-width': 3,
        'circle-stroke-color': 'red',
        'circle-radius': 10
      }
    };
    
    var targetBuildingLabel = {
      'id': "thisBuildingTitle",
      'source': sources['thisBuildingSource'],
      'type': "symbol",
      'minzoom': 11,
      'layout': {
        'text-field': "{PROJECT_NAME}",
        'text-anchor': "bottom-left"
      }
    };
    
    var affordableHousingDots = {
			'id': "buildingLocation",
			'source': sources['publicHousingSource'],
			'type': "circle",
			'minzoom': 11,
			'paint': {
				'circle-color': 'rgb(120,150,255)',
				'circle-stroke-width': 3,
				'circle-stroke-color': 'rgb(150,150,150)',
				'circle-radius': 10
			}
    };
    
    var affordableHousingLabels = {
      'id': "buildingTitle",
      'source': sources['publicHousingSource'],
      'type': "symbol",
      'minzoom': 11,
      'layout': {
        'text-field': "{PROJECT_NAME}",
        'text-anchor': "bottom-left"
      }
    };
    
    var metroStationDots = {
			'id': "metroStationDots",
			'source': sources['metroStations'],
			'type': "circle",
			'minzoom': 11,
			'paint': {
				'circle-color': 'rgb(120,150,255)',
				'circle-stroke-width': 3,
				'circle-stroke-color': 'green',
				'circle-radius': 5
			}
    };
    
    var metroStationLabels = {
      'id': "metroStationLabels",
      'source': sources['metroStations'],
      'type': "symbol",
      'minzoom': 11,
      'layout': {
        'text-field': "{NAME}",
        'text-anchor': "bottom-left"
      }
    };

    new MapboxPortal('affordable-housing-map', [targetBuildingDot, targetBuildingLabel, affordableHousingDots, affordableHousingLabels]);
    new MapboxPortal('metro-stations-map', [targetBuildingDot, targetBuildingLabel, metroStationDots, metroStationLabels]);
  };
  
  (function grabData(){
   // There are weird issues with asynchronicity here, and my old approach didn't work. This was
   // assigning an event listener to readystatechange for each request, calling prepareMaps()
   // if a responseCount variable equaled the number of keys in datasets.
   
   // The next approach: try setInterval! The interval waits to see if all requests are met.
    var ajaxRequests = {};
    console.log('Object.keys(datasets)', Object.keys(datasets));
    for(var i in datasets){
      ajaxRequests[i] = new XMLHttpRequest();
      ajaxRequests[i].open('GET', datasets[i]['url']);
      ajaxRequests[i].send();
      ajaxRequests[i].onreadystatechange = function(){
        if(ajaxRequests[i].readyState == 4){
          responseCount++;
          console.log(responseCount);
          datasets[i]['data'] = JSON.parse(ajaxRequests[i].responseText);
          if(responseCount == Object.keys(datasets).length){
            return prepareMaps();
          }
        }
      }
      console.log(ajaxRequests);
    }

  })();

})();