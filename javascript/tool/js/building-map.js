(function prepareBuildingMaps(){
  'use strict'
   
  var datasets,
      prepareSource,
      prepareMaps,
      thisBuildingSource,
      ProtoLayer,
      mapboxSource,
      buildingForPage,      

      datasets = {
        projects: {
          url: '/javascript/tool/data/project.geojson'
        },
        metroStations: {
          url: "http://opendata.dc.gov/datasets/54018b7f06b943f2af278bbe415df1de_52.geojson"
        }    
      }
  
  // So far the style url and access token come from Paul's Mapbox account.
  // FOR ACTION - find an accessToken that works for everyone.
  mapboxgl.accessToken = 'pk.eyJ1IjoicGF1bGdvdHRzY2hsaW5nIiwiYSI6ImNpejF1Y2U3MzA1ZmQzMnA4c3N4a3FkczgifQ.6W04v2jEJFkZvVhOI-yL6A'

  
  prepareMaps = function(){
    
    buildingForPage = (datasets['projects']['data']['features'].filter(function(element){
      return element['properties']['Proj_address_id'] == buildingID;
    }))[0];
      
    var affordableHousingMap = new mapboxgl.Map({
      container: 'affordable-housing-map',
      style: 'mapbox://styles/mapbox/streets-v9',
      center: buildingForPage['geometry']['coordinates'],
      zoom: 16
    });
        
    affordableHousingMap.on('load', function(){
      affordableHousingMap.addSource(
        'project1', {
          "type": "geojson",
          'data': datasets['projects']['data']
        }
      );
      
      affordableHousingMap.addSource(
        'targetBuilding1', {
          'type': 'geojson',
          'data': buildingForPage
        }
      );
      
      affordableHousingMap.addLayer({
				'id': "buildingLocations",
				'source': 'project1',
				'type': "circle",
				'minzoom': 11,
				'paint': {
					'circle-color': 'rgb(120,150,255)',
					'circle-stroke-width': 3,
					'circle-stroke-color': 'rgb(150,150,150)',
					'circle-radius': 10
				}
      });
      
      affordableHousingMap.addLayer({
        'id': "buildingTitles",
        'source': 'project1',
        'type': "symbol",
        'minzoom': 11,
        'layout': {
          'text-field': "{Proj_Name}",
          'text-anchor': "bottom-left"
        }
      });
      
      affordableHousingMap.addLayer({
				'id': "thisBuildingLocation",
				'source': 'targetBuilding1',
				'type': 'circle',
				'minzoom': 11,
				'paint': {
					'circle-color': 'red',
					'circle-stroke-width': 3,
					'circle-stroke-color': 'red',
					'circle-radius': 10
				}
		  });
			
			affordableHousingMap.addLayer({
		    'id': "thisBuildingTitle",
        'source': 'targetBuilding1',
        'type': "symbol",
        'minzoom': 11,
        'layout': {
          'text-field': "{Proj_Name}",
          'text-anchor': "bottom-left"
        }
			});
    });
    
    var metroStationsMap = new mapboxgl.Map({
      container: 'metro-stations-map',
      style: 'mapbox://styles/mapbox/streets-v9',
      center: buildingForPage['geometry']['coordinates'],
      zoom: 16
    });
    
    metroStationsMap.on('load', function(){
      metroStationsMap.addSource(
        'metros', {
          'type': 'geojson',
          'data': datasets['metroStations']['data']
        }
      );
      
      metroStationsMap.addSource(
        'targetBuilding2', {
          'type': 'geojson',
          'data': buildingForPage
        }
      );
      
      metroStationsMap.addLayer({
        'id': "metroStationDots",
			  'source': 'metros',
			  'type': "circle",
  			'minzoom': 11,
	  		'paint': {
          'circle-color': 'white',
          'circle-stroke-width': 3,
          'circle-stroke-color': 'green',
          'circle-radius': 5
  			}
      });
      
      metroStationsMap.addLayer({
        'id': "metroStationLabels",
        'source': 'metros',
        'type': "symbol",
        'minzoom': 11,
        'layout': {
          'text-field': "{NAME}",
          'text-anchor': "bottom-left"
        }
      });     
      
            
      metroStationsMap.addLayer({
				'id': "thisBuildingLocation",
				'source': 'targetBuilding2',
				'type': 'circle',
				'minzoom': 11,
				'paint': {
					'circle-color': 'red',
					'circle-stroke-width': 3,
					'circle-stroke-color': 'red',
					'circle-radius': 10
				}
			});
			
			metroStationsMap.addLayer({
		    'id': "thisBuildingTitle",
        'source': 'targetBuilding2',
        'type': "symbol",
        'minzoom': 11,
        'layout': {
          'text-field': "{Proj_Name}",
          'text-anchor': "bottom-left"
        }
			}); 
			
			console.log(app);
      
    });
          
            
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
