//A comment here helps keep Jekyll from getting confused about rendering

"use strict";

var projectView = {

  // 'el', 'init' and 'onReturn' conform projectView to the structure expected in the code for
  // changing partials.
  el:'project-view',
  init: function(nlihcID){ // nlihcID is passed in only when the initial view is building    
  
    // TODO: Change this and use the one from secrets.json.
    mapboxgl.accessToken = 'pk.eyJ1Ijoicm1jYXJkZXIiLCJhIjoiY2lqM2lwdHdzMDA2MHRwa25sdm44NmU5MyJ9.nQY5yF8l0eYk2jhQ1koy9g';      

    var transition = nlihcID !== undefined ? true : false;
    var partialRequest = {
        partial: this.el,
        container: null, // will default to '#body-wrapper'
        transition: transition,
        callback: appendCallback
    };
      
    controller.appendPartial(partialRequest, this);

    function appendCallback() {
      if ( getState().activeView.length > 1 ){
          document.getElementById('button-back').innerHTML = '&lt; Back to Map View';
      }
      projectView.getRelevantData(nlihcID); // nlihcID is passed in only when the initial view is building    
    }                 
  },
  renderSegments: function(){
    var nlihc_id = getState()['selectedBuilding'][0]['properties']['nlihc_id']
    var full_project_data = model.dataCollection['full_project_data_' + nlihc_id]['objects'][0]
    for(var segmentName in this.layout){
      this.wrapAndAppendSegment(this.layout[segmentName], full_project_data);
    }
  },
  onReturn: function(){
    var wrapperElement = document.getElementById(this.el);
    wrapperElement.parentElement.removeChild(wrapperElement);
    this.init();
  },
  getRelevantData: function(nlihcID){ // nlihcID is passed in only when the initial view is building    
    if ( nlihcID !== undefined ) {
        var dataURL = model.URLS.project;
        var dataRequest = {
                name: 'raw_project',
                url: dataURL,
                callback: dataCallback
            };
        controller.getData(dataRequest);

        function dataCallback() {
            
            //setting state with geojson since that is how the map view sets it
            var selectedBuildingGeoJSON = controller.convertToGeoJSON(model.dataCollection.raw_project).features.find(function(each){
                    return each.properties.nlihc_id === nlihcID;
            });
            setState('selectedBuilding', selectedBuildingGeoJSON);
            continueDataRequest();
            
        }
    } else {
        continueDataRequest();
    }

    function continueDataRequest(){
      var nlihc_id = getState()['selectedBuilding'][0]['properties']['nlihc_id']

      var dataRequestCount = 0;
      var dataRequests = [
          {   name: "full_project_data_" + nlihc_id,
              url: "http://housinginsights.us-east-1.elasticbeanstalk.com/api/project/" + nlihc_id,
              callback: dataBatchCallback
          },
          {
              name: "raw_metro_stations",
              url: "http://opendata.dc.gov/datasets/54018b7f06b943f2af278bbe415df1de_52.geojson",
              callback: dataBatchCallback
          },
          {
              name: "transit_stats",
              url: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/wmata/" + nlihc_id,
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
          if(dataRequestCount === dataRequests.length){
              projectView.renderSegments();
              projectView.navSidebar.render();
              router.clearScreen();
          }
      }
    }
  },
  wrapAndAppendSegment: function(layoutSegment, full_project_data){
    var container = document.getElementById('building-view-container')

    //Add the title
    if(!layoutSegment.hideTitle){
      d3.select('#building-view-container')
        .append('div')
        .classed('ui attached header',true)
        .text(layoutSegment.title)
    }
    
    var htmlSection = document.createElement('section');
      htmlSection.classList = 'ui attached segment'
      container.appendChild(htmlSection)

    //Save for submenu navigation later
    layoutSegment.htmlSection = htmlSection

    d3.html(layoutSegment.wrapperPartial, function(html){
      htmlSection.appendChild(html);
      layoutSegment.render(full_project_data);
    });
  },
  
  navSidebar: {
    id: 'building-view-segments',
    render: function(){
      var container = document.getElementById('building-view-segments');
      for(var segmentName in projectView.layout){
        (new projectView.NavSidebarButton(projectView.layout[segmentName])).render();
      }
    }
  },
  NavSidebarButton: function(objectWithinLayout){
    this.layoutObj =  objectWithinLayout;

    this.render = function(){
      var ths = this;
      var button = document.createElement('div');
      button.classList.add('enter');
      button.textContent = this.layoutObj.title;
      document.getElementById(projectView.navSidebar.id).appendChild(button);
      button.addEventListener('click', function(){
        var topNavBarHeight = 120;
        var destination = window.scrollY + ths.layoutObj.htmlSection.getBoundingClientRect().top - topNavBarHeight;
        window.scrollTo(0, destination);
      });
    }
  },
  // layout represents the structure of the Project View. Each top-level value
  // is an object with keys/values that govern the data requests and rendering
  // processes for each segment within the Project View. We add a layout to the 
  // Project View by calling the Segment constructor. This allows us to reuse
  // certain methods, like addRoutes.
  // Each 'render' method first grabs the partial corresponding to the 
  // segment from the given folder and adds the content to a set of standard
  // wrapper tags.
  // The value of each top-level key is an object that must have values for
  // the keys, 'title', 'wrapperPartial' and 'render'.
  // There's also an htmlSection property that's added to each object within
  // wrapAndAppendSegment(). This is used for scrolling.
  // There's also a 'hideTitle' key, indicating whether the title will
  // appear in the segment itself, or just within the navigation sidebar.
  layout: {
    header: {
      title: 'Basic information',
      hideTitle: true,
      wrapperPartial: 'partials/project-view/header.html',
      render: function(full_project_data){
        console.log("full project data", full_project_data)
        var d = full_project_data;
        document.getElementById('building-name').innerText = d.proj_name;
        document.getElementById('building-street').innerText = d.proj_addre;
        document.getElementById('building-ward').innerText = d.ward;
        document.getElementById('building-cluster').innerText = d.neighborhood_cluster;
        document.getElementById('owner-name').innerText = d.hud_own_name == 0 ? 'not in data file' : d.hud_own_name;
      },
    },
    
    example1: {
      title: 'Header section',
      wrapperPartial: 'partials/project-view/example.html',
      hideTitle:false,
      render: function(full_project_data){
        d3.select('#this-is-my-id')
      }
    },
    example2: {
      title: 'TOPA Notices',
      wrapperPartial: 'partials/project-view/example.html',
      hideTitle:true,
      render: function(full_project_data){
        d3.select('#this-is-my-id')
      }
    },

    topaNotices: {
      title: 'TOPA Notices',
      wrapperPartial: 'partials/project-view/topa-notices.html',
      hideTitle:false,
      render: function(full_project_data){


        //TODO! Refactor this into a 'buildTable' function that is callable from wherever. 
        //helpful examples:
        //https://www.vis4.net/blog/posts/making-html-tables-in-d3-doesnt-need-to-be-a-pain/
        //https://gist.github.com/jfreels/6733593
        var topaTable =  d3.select('#topa-notice-table')
        var headerTr = topaTable.append('tr')
              .classed('heading', true)
            headerTr.append('th')
              .text('') //index number, no need to annotate
            headerTr.append('th')
              .text('Notice Date')
            headerTr.append('th')
              .text('Notice Type')
            headerTr.append('th')
              .text('Sale Price')

        //Add rows for each topa notice
        var topaRows = topaTable.selectAll('tr.data')
              .data(full_project_data.topa, function(d) {return d.id})

        var trs = topaRows.enter().append('tr')
              .attr('id',function(d){return d.id})
              .classed('data',true) //to differentiate from headings
            trs.append('td')
              .classed('title',true)
              .text(function(d,i){return (i+1) + ')'})
            trs.append('td')
              .classed('value', true)
              .text(function(d){return d.notice_date})
            trs.append('td')
              .classed('value', true)
              .text(function(d){return d.notice_type})
            trs.append('td')
              .classed('value',true)
              .text(function(d){
                  if (d.sale_price == null){
                    return '-'}
                  else {
                    return d3.format('$,.0r')(d.sale_price)
                  }
                })

      }
    },

    affordableHousingMap:{
      title: 'Affordable Housing Nearby',
      wrapperPartial: 'partials/project-view/affordable-housing.html',
      render: function(full_project_data){
        var affordableHousingMap = new mapboxgl.Map({
          container: 'affordable-housing-map',
          style: 'mapbox://styles/mapbox/light-v9',
          center: [full_project_data['longitude'],full_project_data['latitude']],
          zoom: 15, 
          trackResize: true
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

          projectView.addCurrentBuildingToMap(affordableHousingMap);
        });
        ///////////////
        //Nearby Housing sidebar
        ///////////////
        
        d3.select("#tot_buildings").html(model.dataCollection['nearby_projects']['tot_buildings']);
        d3.select("#tot_units").html(model.dataCollection['nearby_projects']['tot_units']);
        d3.select("#nearby_housing_distance").html(model.dataCollection['nearby_projects']['distance'])

      }
    },
    metroStationsAndBusStops: {
      title: "Public Transit Accessibility",
      wrapperPartial: "partials/project-view/transit.html",
      render: function(full_project_data){
        var metroStationsMap = new mapboxgl.Map({
          container: 'metro-stations-map',
          style: 'mapbox://styles/mapbox/light-v9',
          center: [full_project_data['longitude'], full_project_data['latitude']],
          zoom: 15
        });
      
        metroStationsMap.on('load', function(){
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

          projectView.addCurrentBuildingToMap(metroStationsMap,'targetBuilding2');

        });
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
        projectView.addRoutes('#bus_routes_by_dist', brgSorted);
        projectView.addRoutes('#rail_routes_by_dist', rrgSorted);
      }
    },
    subsidyTimelineChart: {
      title: "Building Subsidy Status",
      wrapperPartial: "partials/project-view/subsidy.html",
      render: function(full_project_data){
        var currentNlihc = full_project_data['nlihc_id'];
        
        new SubsidyTimelineChart({
            dataRequest: {
                name: currentNlihc + '_subsidy',
                url: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/project/" + currentNlihc + "/subsidies"
            },
            container: '#subsidy-timeline-chart',
            width: 700,
            height: 300
        }); 
      }
    },
    surroundingAreaDevelopment: {
      title: "Surrounding Area Development",
      wrapperPartial: "partials/project-view/surrounding-dev.html",
      render: function(full_project_data){
        // Nothing to do yet
        return;
      }
    }
  },
  addRoutes: function(id, data){
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

  addCurrentBuildingToMap: function(map){
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
  }
}