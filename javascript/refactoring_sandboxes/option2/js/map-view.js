"use strict";

var mapView = {
    
    init: function() {  

        setSubs([
            ['mapLoaded', mapView.addInitialLayers],
            ['mapLayer', mapView.showLayer],
            ['mapLoaded', sideBar.init],
            ['mapLoaded', mapView.overlayMenu],
            ['overlay', mapView.addOverlayData],
            ['joinedToGeo', mapView.addOverlayLayer],
            ['dataLoaded.raw_project', mapView.placeProjects],
            ['previewBuilding', mapView.showPreview]
        ]);
        
        mapboxgl.accessToken = 'pk.eyJ1Ijoicm1jYXJkZXIiLCJhIjoiY2lqM2lwdHdzMDA2MHRwa25sdm44NmU5MyJ9.nQY5yF8l0eYk2jhQ1koy9g';
        this.map = new mapboxgl.Map({
          container: 'map', // container id
          style: 'mapbox://styles/rmcarder/cizru0urw00252ro740x73cea',
          zoom: 11,
          center: [-76.92, 38.9072],
          minZoom: 3,
          preserveDrawingBuffer: true
        });
        
        this.map.addControl(new mapboxgl.NavigationControl());
        
        
        this.map.on('load', function(){
            setState('mapLoaded',true);
        });        
    },
    overlayMenu: function(){        
        mapView.initialOverlays.forEach(function(overlay){
            var link = document.createElement('a');
            link.href = '#';
            link.id = overlay + '-overlay-item';
            link.innerHTML = overlay.toUpperCase().replace('_',' ');
            link.onclick = function(e){
                e.preventDefault();
                var existingOverlayType = getState().overlay !== undefined ? getState().overlay[0].overlay : null;
                if ( existingOverlayType !== overlay ) {
                    setState('overlay', {overlay: overlay, activeLayer: getState().mapLayer[0]});                     
                } else {
                    mapView.clearOverlay();
                }
            };
            document.getElementById('overlay-menu').appendChild(link);
        });

    },
    initialOverlays: ['crime','building_permits'],
    overlayMapping: {
        neighborhood: {
            group:'neighborhood_cluster', // including key-values here if the overlay grouping name is not the same
                                             // as the name of the mapLayer
            
        }
    },
    clearOverlay: function(layer){
        var i = layer === 'previous' ? 1 : 0;
        console.log(i);
        var layerObj = getState().overlay !== undefined ? getState().overlay[i] : undefined;
        if ( layerObj !== undefined) {
            mapView.map.setLayoutProperty(layerObj.activeLayer + '_' + layerObj.overlay, 'visibility', 'none');
            mapView.toggleActive('#' + layerObj.overlay + '-overlay-item');
            console.log('toggleActive ' + layerObj.overlay + '-overlay-item');
        }
        if ( i === 0 ) { // i.e. clearing the existing current overlay, with result that none will be visible         
          clearState('overlay');
        }
    },   
    addOverlayData: function(msg,data){ // data e.g. { overlay: 'building_permits', activeLayer: 'ward'}]
        if ( data == null) { // ie if the overlays have been cleared
            return;
        }
        var grouping = mapView.overlayMapping[data.activeLayer] !== undefined ? mapView.overlayMapping[data.activeLayer].group || data.activeLayer : data.activeLayer;
        if ( getState()['joinedToGeo.' + data.overlay + '-' + data.activeLayer] === undefined ) {
            function dataCallback() {           
                controller.joinToGeoJSON(data.overlay,grouping,data.activeLayer); // joins the overlay data to the geoJSON *in the dataCollections* not in the mapBox instance
            }
            console.log(data.grouping);
            var dataRequest = {
                name: data.overlay, //e.g. crime
                params: ['all',grouping], // TODO: if first parameter will / could ever be anything other than 'all', will have to set programmaticaly
                callback: dataCallback
            };
            controller.getData(dataRequest);
        } else {
            mapView.showOverlayLayer(data.overlay, data.activeLayer);
        }
    },
    addOverlayLayer: function(msg,data){ // e.g. data = {overlay:'crime',grouping:'neighborhood_cluster',activeLayer:'neighborhood'}
        console.log(mapView.map.getLayer(data.activeLayer + '_' + data.overlay));
        if (mapView.map.getLayer( data.activeLayer + '_' + data.overlay ) === undefined) {
        
            mapView.map.getSource(data.activeLayer + 'Layer').setData(model.dataCollection[data.activeLayer]); // necessary to update the map layer's data
                                                                                                     // it is not dynamically connected to the
                                                                                                     // dataCollection           

            var minValue = d3.min(model.dataCollection[data.overlay + '_all_' + data.grouping].items, function(d){
                return d.count;
            });
            var maxValue = d3.max(model.dataCollection[data.overlay + '_all_' + data.grouping].items, function(d){
                return d.count;
            });
            mapView.map.addLayer({
              'id': data.activeLayer + '_' + data.overlay, //e.g. neighboorhood_crime
              'type': 'fill',
              'source': data.activeLayer + 'Layer',
              'layout': {
                'visibility': 'none'
              },
              'paint': {
                'fill-color': {
                  'property': data.overlay,          
                  'stops': [[minValue, "#fff"], [maxValue, "#1e5cdf"]]
                },
                'fill-opacity': .5
              }
            });      
        }
        mapView.showOverlayLayer(data.overlay,data.activeLayer);

    },
    showOverlayLayer: function(overlay, activeLayer){
      mapView.clearOverlay('previous');
      mapView.map.setLayoutProperty(activeLayer + '_' + overlay, 'visibility', 'visible');
      mapView.toggleActive('#' + overlay + '-overlay-item')               
    },
    toggleActive: function(selector){
        d3.select(selector)
        .attr('class', function(){
            if ( d3.select(this).attr('class') === 'active' ){
                return '';
            }
            return 'active';
        });
    },
    initialLayers: [
        {
            source: 'ward', 
            color: "#002D61",
            visibility: 'visible'            
        },
        {
            source: 'neighborhood',
            color: '#0D5C7D',
            visibility: 'none',
            grouping: 'neighborhood_cluster' // ie the corresponding grouping name in the overlay data, such as crime or building_permits
    
        },
        {
            source: 'tract',
            color: '#8DE2B8',
            visibility: 'none'            
        },
        {
            source: 'zip',
            color: '#0D7B8A',
            visibility: 'none'            
        },
        {
            source: 'zillow',
            color: '#57CABD',
            visibility: 'none'            
        }

    ],
    addInitialLayers: function(msg,data){
        if ( data === true ) {
            //controller.appendPartial('layer-menu','main-view');
            mapView.initialLayers.forEach(function(layer){  // refers to mapView instead of this bc being called form PubSub
                                                            //  context. `this` causes error
                mapView.addLayer(layer);
            });            
        } 
    },
    addLayer: function(layer){
        if ( layer.visibility === 'visible' ) {
            setState('mapLayer', layer.source);
        }
        var layerName = layer.source + 'Layer'; // e.g. 'wardLayer'
        var dataRequest = {
            name: layer.source,  // e.g. ward
            params: null,
            callback: addLayerCallback
        };
        controller.getData(dataRequest);

        function addLayerCallback(data) {            
            if ( mapView.map.getSource( layerName ) === undefined ) {
                mapView.map.addSource( layerName, {
                    type:'geojson',
                    data: data
                });
            }
            mapView.map.addLayer({
              'id': layerName,
              'type': 'line',
              'source': layerName,
              'paint': {
                'line-color': layer.color,
                'line-width': 1
                
              },
              'layout': {
                'visibility': layer.visibility
              }
            });
            mapView.addToLayerMenu(layer);
        }               
    },
    
    addToLayerMenu: function(layer) {
        d3.select('#layer-menu')
            .append('a')
            .attr('href','#')
            .attr('id',function(){
                return layer.source + '-menu-item';
            })
            .attr('class',function(){
                if ( layer.visibility === 'visible' ){
                    return 'active';
                }
                return '';
            })
            .text(layer.source.toUpperCase())
            .on('click', function(){
                d3.event.preventDefault();
                setState('mapLayer',layer.source);                
            });
    },
    showLayer: function(msg,data) {
        var previousLayer = getState().mapLayer[1];
        if (previousLayer !== undefined ) {
            mapView.clearOverlay();
            mapView.map.setLayoutProperty(previousLayer + 'Layer', 'visibility', 'none');            
        }
        mapView.map.setLayoutProperty(data + 'Layer', 'visibility', 'visible');
        d3.selectAll('#layer-menu a')
            .attr('class','');
        d3.select('#' + data + '-menu-item')
            .attr('class','active');

    },
    placeProjects: function(){
        mapView.map.addSource('project', {
          'type': 'geojson',
          'data': controller.convertToGeoJSON(model.dataCollection.raw_project)
        });
        mapView.map.addLayer({
            'id': 'project',
            'type': 'circle',
            'source': 'project',
            'paint': {
                'circle-radius': { // make circles larger as the user zoom. [[smallzoom,px],[bigzoom,px]]
                    'base': 1.75,
                    'stops': [[10, 3], [18, 32]]
                },            
                'circle-color': {
                      property: 'category_code', // the field on which to base the color. this is probably not the category we want for v1
                      type: 'categorical',
                      stops: [ // hard-code for now. should be set programmatically
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
        mapView.map.on('mousemove', function(e) {
             //get the province feature underneath the mouse
             var features = mapView.map.queryRenderedFeatures(e.point, {
                 layers: ['project']
             });
             //if there's a point under our mouse, then do the following.
             if (features.length > 0) {
                 //use the following code to change the 
                 //cursor to a pointer ('pointer') instead of the default ('')
                 mapView.map.getCanvas().style.cursor = (features[0].properties.proj_addre != null) ? 'pointer' : '';
             }
             //if there are no points under our mouse, 
             //then change the cursor back to the default
             else {
                 mapView.map.getCanvas().style.cursor = '';
             }
        });
        mapView.map.on('click', function (e) {
            var building = (mapView.map.queryRenderedFeatures(e.point, { layers: ['project'] }))[0];
            if ( building === undefined ) return;
            setState('previewBuilding',{
                proj_addre: building.properties.proj_addre,
                proj_name: building.properties.proj_name,
                hud_own_name: building.properties.hud_own_name
            });               
        });
    },
    showPreview: function(msg,data){
        document.getElementById('preview-address').innerHTML = data.proj_addre;
        document.getElementById('preview-name').innerHTML = data.proj_name;
        document.getElementById('preview-owner').innerHTML = data.hud_own_name ? 'Owner: ' + data.hud_own_name : '';

    }
};