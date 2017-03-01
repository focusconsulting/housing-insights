mapboxgl.accessToken = 'pk.eyJ1Ijoicm1jYXJkZXIiLCJhIjoiY2lqM2lwdHdzMDA2MHRwa25sdm44NmU5MyJ9.nQY5yF8l0eYk2jhQ1koy9g';

var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/rmcarder/ciym9jjva006d2smgl1nnqaru',
	zoom: 11,
	center: [-76.92, 38.9072],
	minZoom: 3,
	preserveDrawingBuffer: true});

map.on('load', function() {

map.addSource("markers", {
"type": "geojson",
"data": "data/zip.json"
});

map.addLayer({
    "id": "markers",
    "type": "line",
    "source": "markers",
        "paint": {
            "line-color": "#888",
            "line-width": 8
        }
});

map.on('click', function (e) {
	  var building = map.queryRenderedFeatures(e.point, {
	 
	  });
	      document.getElementById('pd').innerHTML = "<h3><strong>" + building[0].properties.Proj_Addre +"</strong><br>"+building[0].properties.Proj_Name + "<br><br>" + "</h3><p>" + "Owner: " + building[0].properties.Hud_Own_Name +"<br>"+"Cluster Name: "+ building[0].properties.Cluster_tr2000_name+"<br>"+"HUD Owner Name: " + building[0].properties.Hud_Own_Name+"<br>"+"HUD Owner Type: " + building[0].properties.Hud_Own_Type +"<br>"+"HUD Manager Name: " + building[0].properties.Hud_Mgr_Name+"<br>"+"HUD Manager Type: " + building[0].properties.Hud_Mgr_Type +"<br><br><strong>"+"At Risk: "+"</strong>"+ building[0].properties.Cat_At_Risk+"<br>"+building[0].properties.Category_Code +"</p>";

	});

	map.getCanvas().style.cursor = 'default';


});