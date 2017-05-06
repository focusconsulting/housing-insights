// Here are some global variables.
// As we refactor the app, let's think about a more appropriate place to put them.  
var map;
var mapMenuData;
var toggleableLayerIds = [ 'ward', 'tract','neighborhood','zip','zillow' ];
var dataSourceIds = ['building_permits', 'crime'];
// End global variables

(function getMenuData(){
  var xhr = new XMLHttpRequest();
  // Currently assumes a server running in the project root directory.
  xhr.open('GET','/javascript/tool/data/datasets_for_browse.json');
  xhr.send();
  xhr.onreadystatechange = function(){
    if(xhr.readyState === 4){
      console.log(xhr.responseText);
      mapMenuData = JSON.parse(xhr.responseText);
      specifyMap();
      populateMenus();
      // prepareMaps();
    }
  }
})();

function specifyMap(){
  mapboxgl.accessToken = 'pk.eyJ1Ijoicm1jYXJkZXIiLCJhIjoiY2lqM2lwdHdzMDA2MHRwa25sdm44NmU5MyJ9.nQY5yF8l0eYk2jhQ1koy9g';

  var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/rmcarder/cizru0urw00252ro740x73cea',
    zoom: 11,
    center: [-76.92, 38.9072],
    minZoom: 3,
    preserveDrawingBuffer: true
  });
}

function populateMenus(){
  for (var i = 0; i < toggleableLayerIds.length; i++) {
    var id = toggleableLayerIds[i];

    var link = document.createElement('a');
    link.href = '#';
    link.textContent = id.toTitle();
    link.dataset.id = id;

    link.onclick = function (e) {
      map.clickedLayer = this.dataset.id;
      e.preventDefault();
      e.stopPropagation();
      showLayer(this); // call reusable function with current `this` (element) as context -JO
      setHeader();
      changeZoneType(); // defined in pie.js
      updateDataSourceMenu();
    };

    var layers = document.getElementById('menu');
    layers.appendChild(link);
  }

  for (var i = 0, datasets = Object.keys(mapMenuData.optional_datasets); i < datasets.length; i++) {
    var id = datasets[i];
    var link = document.createElement('a');
    link.href = '#';
    link.className = 'inactive';
    link.textContent = id.toTitle();
    link.dataset.id = id;

    link.onclick = function (e) {
      var id = this.dataset.id;
      e.preventDefault();
      e.stopPropagation();
      showDataLayer.call(this, id); // call reusable function with current `this` (element) as context -JO
    };
    var data_sources = document.getElementById('data-menu');
    data_sources.appendChild(link);
  }
}



function prepareMaps(){

  app.dataCollection.neighborhood_data_polygons = addDataToPolygons(
    app.dataCollection.neighborhood_polygons.json,
    app.dataCollection.crime_neighborhood.json,
    function(aggregateEl, feature){
      return aggregateEl.group == feature.properties["NAME"];
    } 
  );

  app.dataCollection.neighborhood_data_polygons = addDataToPolygons(
    app.dataCollection.neighborhood_polygons.json,
    app.dataCollection.building_permits_neighborhood.json,
    function(aggregateEl, feature){
      return aggregateEl.group == feature.properties["NAME"];
    } 
  );

  app.dataCollection.ward_data_polygons = addDataToPolygons(
    app.dataCollection.ward_polygons.json,
    app.dataCollection.crime_ward.json,
    function(aggregateEl, feature){
      return aggregateEl.group == feature.properties["NAME"];
    } 
  );

  app.dataCollection.ward_data_polygons = addDataToPolygons(
    app.dataCollection.ward_polygons.json,
    app.dataCollection.building_permits_ward.json,
    function(aggregateEl, feature){
      return aggregateEl.group == feature.properties["NAME"];
    } 
  );

  if (map.loaded()) {
    mapLoadedCallback();
  }
  else {
    map.on('load', mapLoadedCallback);
  }

  function mapLoadedCallback() {

    map.addSource("neighborhood_data",{
      "type": "geojson",
      "data": app.dataCollection.neighborhood_data_polygons
    });

    map.addLayer({
      "id": "crime_neighborhood", 
      "type": "fill",
      "source": "neighborhood_data",
      "layout": {
        "visibility": "none"
      },
      "paint": {
        "fill-color": {
          "property": 'crime',
      // So far the stops are defined arbitrarily. We may want to define them using d3.
          "stops": [[0, '#fff'], [2000, '#ec3d18']]
        },
        "fill-opacity": .5
      }
    });

    map.addLayer({
      "id": "building_permits_neighborhood", 
      "type": "fill",
      "source": "neighborhood_data",
      "layout": {
        "visibility": "none"
      },
      "paint": {
        "fill-color": {
          "property": 'building_permits',
      // So far the stops are defined arbitrarily. We may want to define them using d3.
          "stops": [[0, '#fff'], [4000, '#1e5cdf']]
        },
        "fill-opacity": .5
      }
    });

    map.addSource("ward_data",{
      "type": "geojson",
      "data": app.dataCollection.ward_data_polygons
    });

    map.addLayer({
      "id": "crime_ward", 
      "type": "fill",
      "source": "ward_data",
      "layout": {
        "visibility": "none"
      },
      "paint": {
        "fill-color": {
          "property": 'crime',
      // So far the stops are defined arbitrarily. We may want to define them using d3.
          "stops": [[0, '#fff'], [6000, '#ec3d18']]
        },
        "fill-opacity": .5
      }
    });

    map.addLayer({
      "id": "building_permits_ward", 
      "type": "fill",
      "source": "ward_data",
      "layout": {
        "visibility": "none"
      },
      "paint": {
        "fill-color": {
          "property": 'building_permits',
      // So far the stops are defined arbitrarily. We may want to define them using d3.
          "stops": [[0, '#fff'], [11000, '#1e5cdf']]
        },
        "fill-opacity": .5
      }
    });
    
    map.addSource("zip", {
      "type": "geojson",
      "data": app.dataCollection.zip_polygons.json
    });

    map.addLayer({
      "id": "zip",
      "type": "line",
      "source": "zip",
      layout: {
        visibility: 'none'
      },
      paint: {
        "line-color": "#0D7B8A",
        "line-width": 1
      }
    });

    map.addSource("tract", {
      "type": "geojson",
      "data": app.dataCollection.tract_polygons.json
    });

    map.addLayer({
      "id": "tract",
      "type": "line",
      "source": "tract",
        layout: {
          visibility: 'none'
        },
        paint: {
          "line-color": "#8DE2B8",
          "line-width": 1
        }
    });
  
    map.addSource("neighborhood", {
      "type": "geojson",
      "data": app.dataCollection.neighborhood_polygons.json
    });

    map.addLayer({
      "id": "neighborhood",
      "type": "line",
      "source": "neighborhood",
      layout: {
        visibility: 'none'
      },
      paint: {
        "line-color": "#0D5C7D",
        "line-width": 1
      }
    });

    map.addSource("ward", {
      "type": "geojson",
      "data": app.dataCollection.ward_polygons.json
    });

    map.addLayer({
      "id": "ward",
      "type": "line",
      "source": "ward",
      layout: {
        visibility: 'none'
      },
      paint: {
        "line-color": "#002D61",
        "line-width": 1
      }
    });

    map.addSource("zillow", {
      "type": "geojson",
      "data": app.dataCollection.zillow_polygons.json
    });

    map.addLayer({
      "id": "zillow",
      "type": "line",
      "source": "zillow",
      layout: {
        visibility: 'none'
      },
      paint: {
        "line-color": "#57CABD",
        "line-width": 1
      }
    });
    //zillow color 57CABD
      
    map.addSource("project", {
      "type": "geojson",
      "data": app.dataCollection.project.toGeoJSON('proj_lon', 'proj_lat')
    });
    
    map.addLayer({
      'id': 'project',
      'type': 'circle',
      'source': 'project',
      'paint': {
        // make circles larger as the user zoom. [[smallzoom,px],[bigzoom,px]]
        'circle-radius': {
                'base': 1.75,
                'stops': [[10, 3], [18, 32]]
            },
        // color circles by ethnicity, using data-driven styles
        'circle-color': {
          property: 'category_code',
          type: 'categorical',
          stops: [
            ['1 - At-Risk or Flagged for Follow-up', '#f03b20'],
            ['2 - Expiring Subsidy', '#8B4225'],
            ['3 - Recent Failing REAC Score', '#bd0026'],
            ['4 - More Info Needed', '#A9A9A9'],
            ['5 - Other Subsidized Property', ' #fd8d3c'],
            ['6 - Lost Rental', '#A9A9A9']
          ]
        }
      }
    });
  
    map.addLayer({
      'id': 'projecttext',
      'source': 'project',
      'type': 'symbol',
      'minzoom': 14,
      layout: {
        'text-field': "{proj_name}",
        'text-anchor': "bottom-left"
      },
    });
  
    var categoryLegendEl = document.getElementById('category-legend');
    categoryLegendEl.style.display = 'block';
	
    map.clickedLayer = toggleableLayerIds[0];
    map.previousLayer; // keeping track of previously selected layer so it can be turned off

    map.selectedDataLayer = null;

    function showLayer(selector) { // JO putting this bit in a reusable function

      var visibility = map.getLayoutProperty(map.clickedLayer, 'visibility');

      if (map.previousLayer !== undefined) {
        map.setLayoutProperty(map.previousLayer, 'visibility', 'none');
      }
      document.querySelectorAll('nav#menu a').forEach(function(item){
        item.className = '';
      });
      selector.className = 'active';
      map.setLayoutProperty(map.clickedLayer, 'visibility', 'visible');
    
      map.previousLayer = map.clickedLayer;
      updateDataSourceMenu();
    };

    function showDataLayer(dataSourceId){
      hideDataLayers();
      map.selectedDataLayer = dataSourceId + '_' + map.clickedLayer;
      map.setLayoutProperty(map.selectedDataLayer, 'visibility', 'visible');
      this.className = 'active';
    }

    function hideDataLayers(){
      document.querySelectorAll('#data-menu a').forEach(function(item){
        item.className = '';
      });
      if (map.selectedDataLayer !== null) {
        map.setLayoutProperty(map.selectedDataLayer, 'visibility', 'none');
        map.selectedDataLayer = null;
      }
    }

    function updateDataSourceMenu() {
      hideDataLayers();
      var availableDataSources = map.clickedLayer in Object.keys(mapMenuData['optional_datasets']) ?
        mapMenuData['optional_datasets'][map.clickedLayer]:
        [];
      document.querySelectorAll('#data-menu a').forEach(function(item){
        if (!(item.dataset.id in availableDataSources)){
          // disable link
        }
        else {
          // enable link
        }
      });
    }

    showLayer(document.querySelector('nav#menu a:first-of-type')); // this call happens once on load, sets up initial
                                                                     // condition of having first option active.

    map.on('click', function (e) {
      var building = (map.queryRenderedFeatures(e.point, { layers: ['project'] }))[0];
      var buildingId = building['properties']['nlihc_id'];
      var projectName = building['properties']['proj_name'];
      var queryString = '?building=' + encodeURIComponent(buildingId);
    
      document.getElementById('selected-building-info').innerHTML = "<h3><strong>" +
                   building.properties.proj_addre +"</strong><br>"
                   +building.properties.proj_name + "<br><br>" 
                   + "</h3><p>" + "Owner: " + building.properties.hud_own_name +"<br>"
                   +"Cluster Name: "+ building.properties.cluster_tr2000_name+"<br>"
                   +"HUD Owner Name: " + building.properties.hud_own_name+"<br>"
                   +"HUD Owner Type: " + building.properties.hud_own_type +"<br>"
                   +"HUD Manager Name: " + building.properties.hud_mgr_name+"<br>"
                   +"HUD Manager Type: " + building.properties.hud_mgr_type 
                   +"<br><br><strong>"+"At Risk: "+"</strong>"+ building.properties.cat_at_risk+"<br>"
                   +building.properties.category_Code +"</p>";
        

      var popup = new mapboxgl.Popup({ 'anchor': 'top-right' })
        .setLngLat(e.lngLat)
        .setHTML("<a href = '/tool/building.html" + queryString + "' >See more about " + projectName + "</a>" )
        .addTo(map);
    });

    map.getCanvas().style.cursor = 'default';

    setHeader();

                                                        // putting maps here so they are not called until
                                                        // the map renders, so that the zone (ward, neighborhood) can
                                                        // be selected programmatically 
                                                        
    // putting pie charts in an array property of map so we can access them later, for updating
    map.pieCharts = [
      new PieChart(DATA_FILE,'#pie', 'Subsidized',75,75), 
      new PieChart(DATA_FILE,'#pie-1','Cat_Expiring',75,75), 
      new PieChart(DATA_FILE,'#pie-2','Cat_Failing_Insp',75,75), 
      new PieChart(DATA_FILE,'#pie-3','Cat_At_Risk',75,75),
    //  new PieChart(DATA_FILE,'#pie-4','PBCA',75,75)
    ];
  }
}

function setHeader(){ // sets the text in the sidebar header according to the selected mapLayer
  if (currentZoneType !== map.clickedLayer) {

    //document.querySelector('#zone-details-heading').innerText = map.clickedLayer.capitalizeFirstLetter() + ' Details';
    document.querySelector('#zone-drilldown-instructions').innerText = 'Choose a ' + map.clickedLayer ;
    document.getElementById('zone-selector').onchange = changeZone;

  }
}


