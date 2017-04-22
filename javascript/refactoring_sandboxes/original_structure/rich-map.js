mapboxgl.accessToken;

var map;

function prepareMaps(){

  app.dataCollection.neighborhood_data_polygons;

  app.dataCollection.ward_data_polygons;

  function mapLoadedCallback() {

    // Add sources and layers
  
    var categoryLegendEl;
	
    var toggleableLayerIds;

    map.clickedLayer;
    var previousLayer;

    var dataSourceIds;
    var dataSourcesByLayer;
    var selectedDataLayer;

    function showLayer() {};

    function showDataLayer(dataSourceId){};

    function hideDataLayer(){};

    function updateDataSourceMenu() {};

    function titleString(string) {
      function capFirst(string){
      }
    }

    for (var i = 0; i < toggleableLayerIds.length; i++) {
      var id = toggleableLayerIds[i];

      var link = document.createElement('a');
      link.href = '#';
      link.textContent = titleString(id);
      link.dataset.id = id;

      link.onclick = function (e) {
        map.clickedLayer = this.dataset.id;
        e.preventDefault();
        e.stopPropagation();
        showLayer.call(this); // call reusable function with current `this` (element) as context -JO
        setHeader();
        changeZoneType(); // defined in pie.js
        updateDataSourceMenu();
      };

      var layers = document.getElementById('menu');
      layers.appendChild(link);
    }

    showLayer.call(document.querySelector('nav#menu a:first-of-type')); // this call happens once on load, sets up initial
                                                                     // condition of having first option active.

    // Produce the data sources menu

    // Set up the sidebar and header
      var popup;

    // Note: There is a lot of code here that's been deleted in this exercise, code that
    // hasn't been separated into functions/objects/variables.
                                                        
    map.pieCharts = [];
  }
}

function setHeader(){}

// The line below isn't a function/var/obj declaration, but I'm leaving it here because it contains
// a sizeable chunk of code in the arguments.
app.getInitialData();