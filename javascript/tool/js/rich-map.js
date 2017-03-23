mapboxgl.accessToken = 'pk.eyJ1Ijoicm1jYXJkZXIiLCJhIjoiY2lqM2lwdHdzMDA2MHRwa25sdm44NmU5MyJ9.nQY5yF8l0eYk2jhQ1koy9g';

var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/rmcarder/cizru0urw00252ro740x73cea',
	zoom: 11,
	center: [-76.92, 38.9072],
	minZoom: 3,
	preserveDrawingBuffer: true});

map.on('load', function() {

map.addSource("zip", {
"type": "geojson",
"data": "data/zip.geojson"
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
"data": "data/tract.geojson"
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
"data": "data/neighborhood.geojson"
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
"data": "data/ward.geojson"
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
"data": "data/zillow.geojson"
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
"data": "data/project.geojson"
});

 map.addLayer({
        'id': 'project',
        'type': 'circle',
        'source': 'project',
        'paint': {
            // make circles larger as the user zooms from z12 to z22
            'circle-radius': {
                'base': 1.75,
                'stops': [[12, 3], [22, 180]]
            },
            // color circles by ethnicity, using data-driven styles
            'circle-color': {
                property: 'Category_Code',
                type: 'categorical',
                stops: [
                    ['1 - At-Risk or Flagged for Follow-up', '#f03b20'],
                    ['2 - Expiring Subsidy', '#fecc5c'],
                    ['3 - Recent Failing REAC Score', '#fd8d3c'],
                    ['4 - More Info Needed', '#A9A9A9'],
                    ['5 - Other Subsidized Property', '#A9A9A9'],
                    ['6 - Lost Rental', '#bd0026']]
            }
        }
    });
 map.addLayer({
        'id': 'projecttext',
        'source': 'project',
        'type': 'symbol',
        'minzoom': 14,
        layout: {
          'text-field': "{Proj_Name}",
          'text-anchor': "bottom-left"
        },
      });

var toggleableLayerIds = [ 'ward', 'tract','neighborhood','zip','zillow' ];

for (var i = 0; i < toggleableLayerIds.length; i++) {
    var id = toggleableLayerIds[i];

    var link = document.createElement('a');
    link.href = '#';
    link.className = 'disabled';
    link.textContent = id;

    link.onclick = function (e) {
        var clickedLayer = this.textContent;
        e.preventDefault();
        e.stopPropagation();

        var visibility = map.getLayoutProperty(clickedLayer, 'visibility');

        if (visibility === 'visible') {
            map.setLayoutProperty(clickedLayer, 'visibility', 'none');
            this.className = '';
        } else {
            this.className = 'active';
            map.setLayoutProperty(clickedLayer, 'visibility', 'visible');
        }
    };

    var layers = document.getElementById('menu');
    layers.appendChild(link);
}


map.on('click', function (e) {
	  var building = map.queryRenderedFeatures(e.point, {
	 
	  });
	      document.getElementById('pd').innerHTML = "<h3><strong>" + building[0].properties.Proj_Addre +"</strong><br>"+building[0].properties.Proj_Name + "<br><br>" + "</h3><p>" + "Owner: " + building[0].properties.Hud_Own_Name +"<br>"+"Cluster Name: "+ building[0].properties.Cluster_tr2000_name+"<br>"+"HUD Owner Name: " + building[0].properties.Hud_Own_Name+"<br>"+"HUD Owner Type: " + building[0].properties.Hud_Own_Type +"<br>"+"HUD Manager Name: " + building[0].properties.Hud_Mgr_Name+"<br>"+"HUD Manager Type: " + building[0].properties.Hud_Mgr_Type +"<br><br><strong>"+"At Risk: "+"</strong>"+ building[0].properties.Cat_At_Risk+"<br>"+building[0].properties.Category_Code +"</p>";

	});

	map.getCanvas().style.cursor = 'default';


});