"use strict";

var buildingView = {
    addCurrentBuildingToMap: function(map, source){
      map.addSource(
        'currentBuilding', {
          'type': 'geojson',
          'data': getState()['selectedBuilding'][0]
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
    },
    addRoutes: function(id,data){
        var ul = d3.select(id);
        var lis = ul.selectAll('li')
                    .data(data);

        lis.enter().append('li')
                .attr("class","route_list")
                .merge(lis)
                .html(function(d) {
                    var output = "<strong>" + d.values[0]['shortest_dist'] + " miles</strong>: ";
                    output = output + d.values[0]['routes'].join(", ");
                    return output
                });
    },
    getRelevantData: function(){
        var dataRequestCount = 0;
        var dataRequests = [

            {
                name: "raw_metro_stations",
                url: "http://opendata.dc.gov/datasets/54018b7f06b943f2af278bbe415df1de_52.geojson",
                callback: dataBatchCallback
            },
            {
                name: "transit_stats",
                url: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/wmata/" + getState()['selectedBuilding']['Nlihc_id'],
                callback: dataBatchCallback
            },
            {
                name: "nearby_projects",
                url: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/projects/0.5?latitude=" + getState()['selectedBuilding'][0]['properties']['latitude'] + "&longitude=" + getState()['selectedBuilding'][0]['properties']['longitude'],
                callback: dataBatchCallback
            },
            {
                name: "raw_bus_stops",
                url: "https://opendata.arcgis.com/datasets/e85b5321a5a84ff9af56fd614dab81b3_53.geojson",
                callback: dataBatchCallback
            }
        ]
        for(var i = 0; i < dataRequests.length; i++){
            controller.getData(dataRequests[i]);
        }
        function dataBatchCallback(){
            dataRequestCount++;
            console.log("dataRequestCount", dataRequestCount);
            if(dataRequestCount === dataRequests.length){
                new Accordion();
                buildingView.prepareHeader();
                buildingView.prepareMapsAndCharts();
                buildingView.prepareSidebar();
            }
        }
    },
    el:'building-view',
    init: function(){    
        
        var partialRequest = {
            partial: this.el,
            container: null, // will default to '#body-wrapper'
            transition: true,
            callback: appendCallback
        };
        
        controller.appendPartial(partialRequest, this);
        
        function appendCallback() {
            buildingView.getRelevantData();
        }
    },
    onReturn: function(){
        var wrapperElement = document.getElementById(this.el);
        wrapperElement.parentElement.removeChild(wrapperElement);
        this.init();
    },
    prepareHeader: function(){
        var d = getState()['selectedBuilding'][0]['properties'];
        document.getElementById('building-name').innerText = d.proj_name;
        document.getElementById('building-street').innerText = d.proj_addre;
        document.getElementById('building-ward').innerText = d.ward;
        document.getElementById('building-cluster').innerText = d.neighborhood_cluster;
        document.getElementById('owner-name').innerText = d.hud_own_name == 0 ? 'not in data file' : d.hud_own_name;
    },
    prepareMapsAndCharts: function(){
          
        var affordableHousingMap = new mapboxgl.Map({
            container: 'affordable-housing-map',
            style: 'mapbox://styles/mapbox/light-v9',
            center: [getState()['selectedBuilding'][0]['properties']['longitude'],getState()['selectedBuilding'][0]['properties']['latitude']],
            zoom: 15
        });

            
        affordableHousingMap.on('load', function(){
            affordableHousingMap.addSource(
                'project1', {
                    "type": "geojson",
                    'data': controller.convertToGeoJSON(model.dataCollection['raw_project'])
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

            buildingView.addCurrentBuildingToMap(affordableHousingMap);

        });
        
        var metroStationsMap = new mapboxgl.Map({
            container: 'metro-stations-map',
            style: 'mapbox://styles/mapbox/light-v9',
            center: [getState()['selectedBuilding'][0]['properties']['longitude'], getState()['selectedBuilding'][0]['properties']['latitude']],
            zoom: 15
        });
        
        metroStationsMap.on('load', function(){
        
            ///////////////////////
            //Metro stops
            ///////////////////////
            metroStationsMap.addSource(
                'metros', {
                    'type': 'geojson',
                    'data': model.dataCollection['raw_metro_stations']
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
                'data': model.dataCollection['raw_bus_stops']
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

            buildingView.addCurrentBuildingToMap(metroStationsMap,'targetBuilding2');
            
        });

        var currentNlihc = getState()['selectedBuilding'][0]['properties']['nlihc_id'];

        new SubsidyTimelineChart({
            dataRequest: {
                name: currentNlihc + '_subsidy',
                url: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/project/" + currentNlihc + "/subsidies"
            },
            container: '#subsidy-timeline-chart',
            width: 1000,
            height: 300
        });  
     },
     prepareSidebar: function(){
    
        ///////////////////
        //Transit sidebar
        ///////////////////
        var numBusRoutes = Object.keys(model.dataCollection['transit_stats']['bus_routes']).length;
        var numRailRoutes = Object.keys(model.dataCollection['transit_stats']['rail_routes']).length;
        d3.select("#num_bus_routes").html(numBusRoutes);
        d3.select("#num_rail_routes").html(numRailRoutes);


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
            .attr('style',"fill: white; stroke: green; stroke-width: 3");

        var brgSorted = d3.nest()
                .key(function(d) { return d.shortest_dist })
                .sortKeys(d3.ascending)
                .entries(model.dataCollection['transit_stats']['bus_routes_grouped']);
        var rrgSorted = d3.nest()
                .key(function(d) { return d.shortest_dist })
                .sortKeys(d3.ascending)
                .entries(model.dataCollection['transit_stats']['rail_routes_grouped']);
        buildingView.addRoutes('#bus_routes_by_dist', brgSorted);
        buildingView.addRoutes('#rail_routes_by_dist', rrgSorted);

        ///////////////
        //Nearby Housing sidebar
        ///////////////
        d3.select("#tot_buildings").html(model.dataCollection['nearby_projects']['tot_buildings']);
        d3.select("#tot_units").html(model.dataCollection['nearby_projects']['tot_units']);
        d3.select("#nearby_housing_distance").html(model.dataCollection['nearby_projects']['distance'])
     }


}