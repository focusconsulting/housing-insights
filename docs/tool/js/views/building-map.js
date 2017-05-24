var prepareBuildingMaps = function(buildingLat,buildingLon){
  'use strict'
  
  //TODO this should be shared by building-header.js instead of copied over
  var buildingID = app.getParameterByName('building');

  
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

      datasets = {
        projects: {
          url: '/tool/data/project.geojson'
        },
        metroStations: {
          url: "http://opendata.dc.gov/datasets/54018b7f06b943f2af278bbe415df1de_52.geojson"
        },
        busStops: {
          url: "https://opendata.arcgis.com/datasets/e85b5321a5a84ff9af56fd614dab81b3_53.geojson"
        },
        transitStats: {
          url: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/wmata/" + buildingID
          //url: "http://127.0.0.1:5000/api/wmata/" + buildingID
        },
        nearbyHousing: {
          url: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/projects/0.5?latitude=" + buildingLat + "&longitude=" + buildingLon
        }
      }
  
  // So far the style url and access token come from Paul's Mapbox account.
  // FOR ACTION - find an accessToken that works for everyone.
  mapboxgl.accessToken = 'pk.eyJ1IjoicGF1bGdvdHRzY2hsaW5nIiwiYSI6ImNpejF1Y2U3MzA1ZmQzMnA4c3N4a3FkczgifQ.6W04v2jEJFkZvVhOI-yL6A'

  
  prepareMaps = function(){
    
    buildingForPage = (datasets['projects']['data']['features'].filter(function(element){
      return element['properties']['Nlihc_id'] == buildingID;
    }))[0];
      
    var affordableHousingMap = new mapboxgl.Map({
      container: 'affordable-housing-map',
      style: 'mapbox://styles/mapbox/light-v9',
      center: buildingForPage['geometry']['coordinates'],
      zoom: 15
    });
        
    affordableHousingMap.on('load', function(){
      affordableHousingMap.addSource(
        'project1', {
          "type": "geojson",
          'data': datasets['projects']['data']
        }
      );

      affordableHousingMap.addLayer({
				'id': "buildingLocations",
				'source': 'project1',
				'type': "circle",
				'minzoom': 9,
				'paint': {
					'circle-color': 'rgb(120,150,255)',
					'circle-stroke-width': 3,
					'circle-stroke-color': 'rgb(150,150,150)',
					'circle-radius': {
                'base': 1.75,
                'stops': [[10, 2], [18, 20]] //2px at zoom 10, 20px at zoom 18
            }
				}
      });
      
      affordableHousingMap.addLayer({
        'id': "buildingTitles",
        'source': 'project1',
        'type': "symbol",
        'minzoom': 11,
        'layout': {
          //'text-field': "{Proj_Name}",  //TODO need to hide the one under the current building
          'text-anchor': "bottom-left"
        }
      });

      addCurrentBuilding(affordableHousingMap);

    });
    
    var metroStationsMap = new mapboxgl.Map({
      container: 'metro-stations-map',
      style: 'mapbox://styles/mapbox/light-v9',
      center: buildingForPage['geometry']['coordinates'],
      zoom: 15
    });
    
    metroStationsMap.on('load', function(){
      
      ///////////////////////
      //Metro stops
      ///////////////////////
      metroStationsMap.addSource(
        'metros', {
          'type': 'geojson',
          'data': datasets['metroStations']['data']
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
          'circle-radius': 7
        }
      });
      
      metroStationsMap.addLayer({
        'id': "metroStationLabels",
        'source': 'metros',
        'type': "symbol",
        'minzoom': 11,
        'layout': {
          'text-field': "{NAME}",
          'text-anchor': "left",
          'text-offset':[1,0],
          'text-size': {
                'base': 1.75,
                'stops': [[10, 10], [18, 20]] 
            }
        },
        'paint': {
          'text-color':"#006400"
        }
      });     
      
      ///////////////////////
      //Bus Stops
      ///////////////////////
      metroStationsMap.addSource(
        'busStops', {
          'type': 'geojson',
          'data': datasets['busStops']['data']
        }
      );
      metroStationsMap.addLayer({
        'id': "busStopDots",
        'source': 'busStops',
        'type': 'symbol',
        'minzoom': 11,
        'layout': {
          'icon-image':'bus-15',
          //'text-field': "{BSTP_MSG_TEXT}", //too busy
          'text-anchor': "left",
          'text-offset':[1,0],
          'text-size':12,
          'text-optional':true
        }
      });
      //No titles for now, as the geojson from OpenData does not include routes (what we want)

      addCurrentBuilding(metroStationsMap,'targetBuilding2');

			
			console.log(app);
      
    });
          
            
  };

//Adds single building icon and label. Encourages consistent formatting of the selected building
addCurrentBuilding = function(map,source){

      map.addSource(
        'currentBuilding', {
          'type': 'geojson',
          'data': buildingForPage
        }
      );

      //For future reference, this is how to do custom icons, requires effort:https://github.com/mapbox/mapbox-gl-js/issues/822
      map.addLayer({
        'id': "thisBuildingLocation",
        'source': 'currentBuilding',
        'type': 'circle',
        'minzoom': 6,
        'paint':{
          'circle-color': 'red',
          'circle-stroke-width': 3,
          'circle-stroke-color': 'red',
          'circle-radius': {
                'base': 1.75,
                'stops': [[10, 2], [18, 20]]
            }
        }
      });

      map.addLayer({
        'id': "thisBuildingTitle",
        'source': 'currentBuilding',
        'type': "symbol",
        'minzoom': 11,
        'paint': {
          'text-color': "red"
        },
        'layout': {
          'text-field': "{Proj_Name}",
          'text-justify': 'left',
          'text-offset':[1,0],
          'text-anchor': "left",
          'text-size':14
        }
      });  
}
  prepareSidebar = function(){
    
    ///////////////////
    //Transit sidebar
    ///////////////////
    var numBusRoutes = Object.keys(datasets['transitStats']['data']['bus_routes']).length
    var numRailRoutes = Object.keys(datasets['transitStats']['data']['rail_routes']).length
    d3.select("#num_bus_routes").html(numBusRoutes)
    d3.select("#num_rail_routes").html(numRailRoutes)


    //TODO this is a pretty hacky way to do this but it lets us use the same specs as above
    //TODO should make this approach to a legend a reusable method if desired, and then
    //link the values here to the relevant attributes in the addLayer method.
    var rail_icon = d3.select('#rail_icon')
          .append('svg')
          .style("width", 24)
          .style("height", 18)
          .append('circle')
          .attr('cx','9')
          .attr('cy','9')
          .attr('r','7')
          .attr('style',"fill: white; stroke: green; stroke-width: 3")

    var brgSorted = d3.nest()
            .key(function(d) {return d.shortest_dist})
            .sortKeys(d3.ascending)
            .entries(datasets['transitStats']['data']['bus_routes_grouped']);
    var rrgSorted = d3.nest()
            .key(function(d) {return d.shortest_dist})
            .sortKeys(d3.ascending)
            .entries(datasets['transitStats']['data']['rail_routes_grouped']);
    addRoutes('#bus_routes_by_dist',brgSorted);
    addRoutes('#rail_routes_by_dist',rrgSorted);

    ///////////////
    //Nearby Housing sidebar
    ///////////////
    d3.select("#tot_buildings").html(datasets['nearbyHousing']['data']['tot_buildings'])
    d3.select("#tot_units").html(datasets['nearbyHousing']['data']['tot_units'])
    d3.select("#nearby_housing_distance").html(datasets['nearbyHousing']['data']['distance'])
  };

  addRoutes = function(id,data){
    var ul = d3.select(id)
    var lis = ul.selectAll('li')
                  .data(data)

        lis.enter().append('li')
              .attr("class","route_list")
              .merge(lis)
                .html(function(d) {
                    var output = "<strong>" + d.values[0]['shortest_dist'] + " miles</strong>: "
                    output = output + d.values[0]['routes'].join(", ")
                    return output
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

        prepareSidebar();
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

};
