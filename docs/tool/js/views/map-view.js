"use strict";

var mapView = {
    el: 'mapView',
    buildOverlayOptions: function(){
        var tablesWithOverlays = Object.keys(model.dataCollection.metaData).filter(function(key){
            var tableProperties = model.dataCollection.metaData[key];
            return tableProperties.api && tableProperties.api.available_aggregates.length > 0;
        });
        mapView.initialOverlays = tablesWithOverlays.map(function(tableName){
            return {
                "name": tableName,
                "zones": model.dataCollection.metaData[tableName]['available_aggregates']
            }
        });
    },
    init: function() {  

        setSubs([
            ['mapLayer', mapView.showLayer],
            ['mapLoaded', model.loadMetaData],
            ['dataLoaded.metaData', mapView.addInitialLayers],
            ['dataLoaded.metaData', sideBar.init],
            ['dataLoaded.metaData', mapView.overlayMenu],
            ['overlayRequest', mapView.addOverlayData],
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
        mapView.buildOverlayOptions();    
        mapView.initialOverlays.forEach(function(overlay){
            var link = document.createElement('a');
            link.href = '#';
            link.id = overlay.name + '-overlay-item';
            link.innerHTML = overlay.name.toUpperCase().replace('_',' ');
            link.onclick = function(e){
                e.preventDefault();
                var existingOverlayType = getState().overlaySet !== undefined ? getState().overlaySet[0].overlay : null;
                console.log(existingOverlayType, overlay.name);
                if ( existingOverlayType !== overlay.proj_name ) {
                    setState('overlayRequest', {overlay: overlay.name, activeLayer: getState().mapLayer[0]});                     
                } else {
                    mapView.clearOverlay();
                }
            };
            document.getElementById('overlay-menu').appendChild(link);
        });

    },
    initialOverlays: [],
    overlayMapping: {
        neighborhood: {
            group:'neighborhood_cluster', // including key-values here if the overlay grouping name is not the same
                                             // as the name of the mapLayer
            
        }
    },
    clearOverlay: function(layer){
        var i = layer === 'previous' ? 1 : 0;
        
        var layerObj = getState().overlaySet !== undefined ? getState().overlaySet[i] : undefined;
        
        if ( layerObj !== undefined) {
            mapView.map.setLayoutProperty(layerObj.activeLayer + '_' + layerObj.overlay, 'visibility', 'none');
            mapView.toggleActive('#' + layerObj.overlay + '-overlay-item');
            
        }
        if ( i === 0 ) { // i.e. clearing the existing current overlay, with result that none will be visible         
          clearState('overlaySet');
        }
    },   
    addOverlayData: function(msg,data){ // data e.g. { overlay: 'building_permits', activeLayer: 'ward'}]
        if ( data == null) { // ie if the overlays have been cleared
            return;
        }
        var grouping = mapView.overlayMapping[data.activeLayer] !== undefined ? mapView.overlayMapping[data.activeLayer].group || data.activeLayer : data.activeLayer;
        if ( getState()['joinedToGeo.' + data.overlay + '-' + data.activeLayer] === undefined ) {
            function dataCallback() {           
                controller.joinToGeoJSON(data.overlay,grouping,data.activeLayer); // joins the overlay data to the geoJSON *in the dataCollection* not in the mapBox instance
            }

            var dataURLInfo = model.dataCollection.metaData[data.overlay].api;

            var dataURL = dataURLInfo.aggregate_endpoint_base + data.activeLayer;
            
            var dataRequest = {
                name: data.overlay + "_" + data.activeLayer, //e.g. crime
                url: dataURL, 
                callback: dataCallback
            };
            controller.getData(dataRequest);
        } else {
            mapView.showOverlayLayer(data.overlay, data.activeLayer);
        }
    },
    addOverlayLayer: function(msg,data){ // e.g. data = {overlay:'crime',grouping:'neighborhood_cluster',activeLayer:'neighborhood'}
        
        if (mapView.map.getLayer( data.activeLayer + '_' + data.overlay ) === undefined) {
        
            mapView.map.getSource(data.activeLayer + 'Layer').setData(model.dataCollection[data.activeLayer]); // necessary to update the map layer's data
                                                                                                     // it is not dynamically connected to the
                                                                                                     // dataCollection           

            var minValue = d3.min(model.dataCollection[data.overlay + '_' + data.grouping].items, function(d){
                return d.count;
            });
            var maxValue = d3.max(model.dataCollection[data.overlay + '_' + data.grouping].items, function(d){
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
      mapView.map.setLayoutProperty(activeLayer + '_' + overlay, 'visibility', 'visible');
      mapView.toggleActive('#' + overlay + '-overlay-item')               
      setState('overlaySet', {overlay: overlay, activeLayer: activeLayer});  
      mapView.clearOverlay('previous');
      // TODO: make / show legend
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
            source: 'neighborhood_cluster',
            color: '#0D5C7D',
            visibility: 'none',
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
        }/*,
        {
            source: 'zillow',
            color: '#57CABD',
            visibility: 'none'            
        }*/

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
        var layerName = layer.source + 'Layer'; // e.g. 'wardLayer'
        var dataRequest = {
            name: layer.source,  // e.g. ward
            url: model.URLS.geoJSONPolygonsBase + layer.source + '.geojson',
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
            if ( layer.visibility === 'visible' ) {
                setState('mapLayer', layer.source);
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
            .text(function(){
                return layer.source.split('_')[0].toUpperCase();
            })
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
    placeProjects: function(){ // some repetition here with the addLayer function used for zone layers. could be DRYer if combines
                               // or if used constructor with prototypical inheritance
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
       // TODO: MAKE LEGEND
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

            var popup = new mapboxgl.Popup({ 'anchor': 'top-right' }) // the lines commented out below would handle loading
                                                                      // the building view from a partial html file
                                                                      // and appending it to the already loaded page, in a
                                                                      // single-page-app fashion. commented out here because it
                                                                      // is not ready. defering now to the old method of loading
                                                                      // a the building.html page with a query parameter for the 
                                                                      // building id. uncomment the lines to see how it would work
                .setLngLat(e.lngLat)
                .setHTML('<a href="building.html?building=' + building.properties.nlihc_id + '">See more about ' + building.properties.proj_name + '</a>' )
        //      .setHTML('<a href="#">See more about ' + building.properties.proj_name + '</a>' )
                .addTo(mapView.map);

      /*      popup._container.querySelector('a').onclick = function(e){
                e.preventDefault();
                setState('switchView', buildingView);
            };*/
           });               
        
    },
    showPreview: function(msg,data){
        document.getElementById('preview-address').innerHTML = data.proj_addre;
        document.getElementById('preview-name').innerHTML = data.proj_name;
        document.getElementById('preview-owner').innerHTML = data.hud_own_name ? 'Owner: ' + data.hud_own_name : '';

    }
};