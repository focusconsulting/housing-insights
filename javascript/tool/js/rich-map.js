mapboxgl.accessToken = 'pk.eyJ1Ijoicm1jYXJkZXIiLCJhIjoiY2lqM2lwdHdzMDA2MHRwa25sdm44NmU5MyJ9.nQY5yF8l0eYk2jhQ1koy9g';

var map = new mapboxgl.Map({
  container: 'map', // container id
  style: 'mapbox://styles/rmcarder/cizru0urw00252ro740x73cea',
  zoom: 11,
  center: [-76.92, 38.9072],
  minZoom: 3,
  preserveDrawingBuffer: true
});

function prepareMaps(){

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
    
    console.log('app in rich-map.js', app);
    console.log('app.dataCollection.project.geoJSON()', app.dataCollection.project.geoJSON());
    
    map.addSource("project", {
      "type": "geojson",
      "data": app.dataCollection.project.geoJSON('proj_lon', 'proj_lat')
    });
    
    console.log(map.getSource('project'));

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
          property: 'category_code',
          type: 'categorical',
          stops: [
            ['1 - At-Risk or Flagged for Follow-up', '#f03b20'],
            ['2 - Expiring Subsidy', '#fecc5c'],
            ['3 - Recent Failing REAC Score', '#fd8d3c'],
            ['4 - More Info Needed', '#A9A9A9'],
            ['5 - Other Subsidized Property', '#A9A9A9'],
            ['6 - Lost Rental', '#bd0026']
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
      var building = (map.queryRenderedFeatures(e.point, { layers: ['project'] }))[0];
      var projAddressId = building['properties']['proj_address_id'];
      var projectName = building['properties']['proj_name'];
      var queryString = '?building=' + encodeURIComponent(projAddressId);
    
      document.getElementById('pd').innerHTML = "<h3><strong>" + building.properties.proj_addre +"</strong><br>"+building.properties.proj_name + "<br><br>" + "</h3><p>" + "Owner: " + building.properties.hud_own_name +"<br>"+"Cluster Name: "+ building.properties.cluster_tr2000_name+"<br>"+"HUD Owner Name: " + building.properties.hud_own_name+"<br>"+"HUD Owner Type: " + building.properties.hud_own_type +"<br>"+"HUD Manager Name: " + building.properties.hud_mgr_name+"<br>"+"HUD Manager Type: " + building.properties.hud_mgr_type +"<br><br><strong>"+"At Risk: "+"</strong>"+ building.properties.cat_at_risk+"<br>"+building.properties.category_Code +"</p>";
        
      var popup = new mapboxgl.Popup({ 'anchor': 'top-right' })
        .setLngLat(e.lngLat)
        .setHTML("<a href = '/javascript/tool/building.html" + queryString + "' >See more about " + projectName + "</a>" )
        .addTo(map);

    });

    map.getCanvas().style.cursor = 'default';

  });

}

app.getAPIData(['project'], prepareMaps);