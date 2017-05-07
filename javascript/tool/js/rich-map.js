// Here are some global variables.
// As we refactor the app, let's think about a more appropriate place to put them.  
var map;
var mapMenuData;
var toggleableLayerIds = [ 'ward', 'tract','neighborhood','zip','zillow' ];
var layerOptions = [];
var dataMenu;
// End global variables

function hideAllOptionalLayers(){
  for(var i = 0; i < layerOptions.length; i++){
    layerOptions[i].hide();
  }
}

(function getMenuData(){
  var xhr = new XMLHttpRequest();
  // Currently assumes a server running in the project root directory.
  xhr.open('GET','/javascript/tool/data/datasets_for_browse.json');
  xhr.send();
  xhr.onreadystatechange = function(){
    if(xhr.readyState === 4){
      mapMenuData = JSON.parse(xhr.responseText);
      prepareMaps();
      dataMenu = new DataMenu();
    }
  }
})();

function DataMenu(){
  var _this = this;
  for (var i = 0, datasets = Object.keys(mapMenuData.optional_datasets); i < datasets.length; i++) {
    var id = datasets[i];
    var link = document.createElement('a');
    link.href = '#';
    link.className = 'inactive';
    link.textContent = id.toTitle();
    link.dataset.id = id;

    link.onclick = function (e) {
      e.preventDefault();
      e.stopPropagation();
      _this.emptyZoneOptions();
      _this.makeZoneOptions(id);
    };
    var data_sources = document.getElementById('data-menu');
    data_sources.appendChild(link);
  }

  this.makeZoneOptions = function(tableName){
    var eligibleZoneIds = toggleableLayerIds.filter(function(zone){
      return mapMenuData.optional_datasets[tableName].indexOf(zone) != -1;
    })
    for (var i = 0; i < eligibleZoneIds.length; i++) {
      var id = eligibleZoneIds[i];

      var link = document.createElement('a');
      link.href = '#';
      link.textContent = id.toTitle();
      link.dataset.id = id;

      link.onclick = function (e) {
        e.preventDefault();
        e.stopPropagation();
        
        var possibleLayerOptions = layerOptions.filter(function(opt){
          return opt.layerName == id && opt.dataName == tableName;
        })

        var selectedLayerOption = possibleLayerOptions[0] || new LayerOption(tableName, id);

        selectedLayerOption.show();

        setHeader();
        changeZoneType(); // defined in pie.js
      };

      var layers = document.getElementById('menu');
      layers.appendChild(link);
    }
  }

  this.emptyZoneOptions = function(){
    var layers = document.getElementById('menu');
    while(layers.children.length > 0 ){
      layers.removeChild(layers.children[0]);
    }
  }
}

// LayerOption assumes that there is one zones menu and one data menu. 
// It also assumes that the id attribute for each link in the data layers menu 
// corresponds to a table name, and the id attribute for each link in the 
// zones menu corresponds to a zone layer.
function LayerOption(dataName, zoneName){
  var _this = this;
  layerOptions.push(this);
  this.dataName = dataName;
  this.zoneName = zoneName;
  this.sourceName = dataName + "_" + zoneName + "_source";
  this.layerName = dataName + "_" + zoneName + "_layer";

  this.sourceData;

  (function queryData(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', mapMenuData.zone_api_base + dataName + "/all/" + zoneName);
    xhr.send();
    xhr.onreadystatechange = function(){
      if(xhr.readyState === 4){
        var json = JSON.parse(xhr.responseText);
        this.sourceData = json;
        queryShape();
      }  
    }
  })();

  function queryShape(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/javascript/tool/data/' + this.zoneName + ".geojson");
      xhr.send();
      xhr.onreadystatechange = function(){
        if(xhr.readyState === 4){
          var json = JSON.parse(xhr.responseText);
          this.sourceShapes = json;
          this.addMapboxSource();
          this.addMapboxLayer();
        }  
      }

  }

  this.addMapboxSource = function(){
    // Check whether the source already exists and if it does, use it.
    if(map.getSource(this.sourceName)){
      this.mapboxSource = map.getSource(this.sourceName);
    }
    var sourcePlusShapes = addDataToPolygons(this.sourceShapes, this.sourceData);

    map.addSource(this.sourceName, {
      "type": "geojson",
      "data": sourcePlusShapes
    });

  }

  this.addMapboxLayer = function(){
    // Check whether the layer already exists and if it does, use it.
    if(map.getLayer(this.layerName)){
      this.mapboxLayer = map.getLayer(this.layerName);
    }

    // for determining upper bound of the data
    var counts = this.sourceData.items.map(function(item){
      return item.count;
    })

    // assigns a random color
    var RGB_RANGE = 75;
    var highestColor = 'rgb' + ([0,0,0].map(function(el){
      return Math.random() * (255 - RGB_RANGE);
    })).join("");

    var lowestColor = 'rgb' + (lowestColor.map(function(el){
      return el + RGB_RANGE;
    })).join("");

    map.addLayer({
      "id": this.layerName,
      "type": "fill",
      "source": this.sourceName,
      "layout": {
        "visibility": "none"
      },
      "paint": {
        "fill-color": {
          "property": this.dataName,
          "stops": [[0, lowestColor], [Math.max(counts), highestColor]]
        },
        "fill-opacity": .5
      }
    });
  }

  this.show = function() {
    map.clickedZone = this.zoneName;
    var selector = document.getElementById(this.dataName);
    hideAllOptionalLayers();

    document.querySelectorAll('nav#menu a').forEach(function(item){
      item.className = '';
    });
    selector.className = 'active';
    map.setLayoutProperty(this.layerName, 'visibility', 'visible');
  
  };

  this.hide = function(){
    map.setLayoutProperty(this.layerName, 'visibility', 'none');
  }

}

function prepareMaps(){

  mapboxgl.accessToken = 'pk.eyJ1Ijoicm1jYXJkZXIiLCJhIjoiY2lqM2lwdHdzMDA2MHRwa25sdm44NmU5MyJ9.nQY5yF8l0eYk2jhQ1koy9g';

  var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/rmcarder/cizru0urw00252ro740x73cea',
    zoom: 11,
    center: [-76.92, 38.9072],
    minZoom: 3,
    preserveDrawingBuffer: true
  });

  if (map.loaded()) {
    mapLoadedCallback();
  }
  else {
    map.on('load', mapLoadedCallback);
  }

  function mapLoadedCallback() {
  
    // TO DO - there's a bit of ugly callback nesting in the code below, which loads the initial
    // 'project' data into the map. Let's make this neater!
    var projectXHR = new XMLHttpRequest();
    projectXHR.open('GET', 'http://hiapidemo.us-east-1.elasticbeanstalk.com/api/raw/project');
    projectXHR.send();
    projectXHR.onreadystatechange = function(){
      if(projectXHR.readyState === 4){
        app.dataCollection.project = new APIDataObj(JSON.parse(projectXHR.responseText));
        console.log(app.dataCollection.project);
        addProjectToMap();
      }
    }

    function addProjectToMap(){
      
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
    }
  
    var categoryLegendEl = document.getElementById('category-legend');
    categoryLegendEl.style.display = 'block';

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
  
  function setHeader(){ // sets the text in the sidebar header according to the selected mapLayer
    if (currentZoneType !== map.clickedZone) {

      document.querySelector('#zone-drilldown-instructions').innerText = 'Choose a ' + map.clickedZone;
      document.getElementById('zone-selector').onchange = changeZone;

    }
  }
}




