// Here are some global variables.
// As we refactor the app, let's think about a more appropriate place to put them.  
var map,
    mapMenuData,
    dataMenu,
    layerOptions = [];

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
      prepareInitialMapData();
    }
  }
})();

function OverlayMenuItem(idString){
  var _this = this;
  this.link = document.createElement('a');
  this.link.href = '#';
  this.link.className = 'inactive';
  this.link.textContent = idString.toTitle();
  this.link.dataset.id = idString;
  this.link.addEventListener('click', function(e){
    e.preventDefault();
    e.stopPropagation();
    for(var i = 0, kids = this.parentElement.children; i < kids.length; i++){
      if(kids[i].classList.contains('active')){ kids[i].classList.remove('active');}
      if(!kids[i].classList.contains('inactive')){ kids[i].classList.add('inactive');}
    }
    _this.link.classList.add('active');
    _this.link.classList.remove('inactive');
  });
  
}

function DatasetItem(dataset){
  OverlayMenuItem.call(this, dataset);
  this.link.addEventListener('click', function(e){
    hideAllOptionalLayers();
    dataMenu.emptyZoneOptions();
    dataMenu.makeZoneOptions(dataset);
  })
  this.toDOM = function(){
    document.getElementById('data-menu').appendChild(this.link);
  }
}
DatasetItem.prototype = Object.create(OverlayMenuItem.prototype);

function ZoneItem(zone, dataset){
  OverlayMenuItem.call(this, zone);
  
  this.link.addEventListener('click', function(e){
    var existingLayerOption = layerOptions.find(function(opt){
      return opt.layerName == zone && opt.dataName == dataset;
    });

    hideAllOptionalLayers();

    var selectedLayerOption = existingLayerOption || new LayerOption(dataset, zone, map);

    map.setHeader();
    changeZoneType(); // defined in pie.js

  })
  this.toDOM = function(){
    document.getElementById('menu').appendChild(this.link);
  }

}
ZoneItem.prototype = Object.create(OverlayMenuItem.prototype);

function DataMenu(){
  this.toDOM = function(){
    for (var i = 0, datasets = Object.keys(mapMenuData.optional_datasets); i < datasets.length; i++) {
      (new DatasetItem(datasets[i])).toDOM();
    }
  }

  this.makeZoneOptions = function(tableName){
    var eligibleZoneIds = mapMenuData['optional_datasets'][tableName];
    for (var i = 0; i < eligibleZoneIds.length; i++) {
      (new ZoneItem(eligibleZoneIds[i], tableName)).toDOM();
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

// LayerOption includes the third 'map' argument to avoid a scoping/closure issue
// that caused 'map' to be undefined. Let's find a more elegant way to make 
// map available to LayerOption, so we don't have to use an argument for something
// that should be kind of global.
function LayerOption(dataName, zoneName, map){
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
        _this.sourceData = json;
        queryShape();
      }  
    }
  })();

  // This function exists to grab a geoJSON polygon object from the server. We won't need this if we
  // put them in an API endpoint.
  function queryShape(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/javascript/tool/data/' + _this.zoneName + ".geojson");
      xhr.send();
      xhr.onreadystatechange = function(){
        if(xhr.readyState === 4){
          var json = JSON.parse(xhr.responseText);
          _this.sourceShapes = json;
          _this.addMapboxSource();
          _this.addMapboxLayer();
        }  
      }

  }

  this.addMapboxSource = function(){
    // Check whether the source already exists
    if(map.getSource(this.sourceName)){
      return;
    }
    var sourcePlusShapes = addDataToPolygons(this.sourceShapes, this.sourceData);

    map.addSource(this.sourceName, {
      "type": "geojson",
      "data": sourcePlusShapes
    });

  }

  this.addMapboxLayer = function(){
    // Check whether the layer already exists
    if(map.getLayer(this.layerName)){
      this.show();
      return;
    }

    // for determining upper bound of the data
    var counts = this.sourceData.items.map(function(item){
      return item.count;
    })

    // assigns a random color
    var RGB_RANGE = 200;

    // if we need random colors elsewhere in this app, we could extract a RandomColor constructor and
    // turn 'makeRGB' into a method. For now it's a quick and diryt function.
    function makeRGB(colorValsArray){
      return "rgb(" + colorValsArray.join(",") + ")";
    }

    var highestColorVals = [0,0,0].map(function(el){
      return Math.floor(Math.random() * (255 - RGB_RANGE));
    });

    var lowestColorVals = highestColorVals.map(function(el){
      return el + RGB_RANGE;
    });

    map.addLayer({
      "id": this.layerName,
      "type": "fill",
      "source": this.sourceName,
      "layout": {
        "visibility": "visible"
      },
      "paint": {
        "fill-color": {
          "property": this.dataName,
          "stops": [[0, makeRGB(lowestColorVals)], [Math.max.apply(null, counts), makeRGB(highestColorVals)]]
        },
        "fill-opacity": .5
      }
    });
  }

  this.show = function() {
    map.clickedZone = this.zoneName;
    var selector = document.querySelectorAll('[data-id=' + this.dataName + ']')[0];
    map.setLayoutProperty(this.layerName, 'visibility', 'visible');
  
  };

  this.hide = function(){
    map.setLayoutProperty(this.layerName, 'visibility', 'none');
  }

}

function prepareInitialMapData(){

  mapboxgl.accessToken = 'pk.eyJ1Ijoicm1jYXJkZXIiLCJhIjoiY2lqM2lwdHdzMDA2MHRwa25sdm44NmU5MyJ9.nQY5yF8l0eYk2jhQ1koy9g';

  map = new mapboxgl.Map({
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

  // There might be a better place to put this.
  map.setHeader = function(){ // sets the text in the sidebar header according to the selected mapLayer
    if (currentZoneType !== this.clickedZone) {

      document.querySelector('#zone-drilldown-instructions').innerText = 'Choose a ' + this.clickedZone;
      document.getElementById('zone-selector').onchange = changeZone;

    }
  }

  function mapLoadedCallback() { 
    dataMenu = new DataMenu;
    dataMenu.toDOM();

    // TO DO - there's a bit of ugly callback nesting in the code below, which loads the initial
    // 'project' data into the map. Let's make this neater!
    var projectXHR = new XMLHttpRequest();
    projectXHR.open('GET', 'http://hiapidemo.us-east-1.elasticbeanstalk.com/api/raw/project');
    projectXHR.send();
    projectXHR.onreadystatechange = function(){
      if(projectXHR.readyState === 4){
        app.dataCollection.project = new APIDataObj(JSON.parse(projectXHR.responseText));
        addProjectToMap();
      }
    }

    function addProjectToMap(){
      
      map.addSource("project", {
        "type": "geojson",
        "data": app.dataCollection.project.toGeoJSON('longitude', 'latitude')
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

    // HERE'S WHERE THE PAGE LOADS THE DATA MENU AND MAKES IT POSSIBLE TO LOAD OPTIONAL DATA SOURCES.

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

    map.setHeader();                                             
                                                        
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






