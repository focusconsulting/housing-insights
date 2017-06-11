    "use strict";

var mapView = {
    el: 'map-view',

    init: function() { // as single page app, view init() functions should include only what should happen the first time
                       // the view is loaded. things that need to happen every time the view is made active should be in 
                       // the onReturn methods. nothing needs to be there so far for mapView, but buildingView for instance 
                       // should load the specific building info every time it's made active.
        console.log(this);
        var partialRequest = {
            partial: this.el,
            container: null, // will default to '#body-wrapper'
            transition: false,
            callback: appendCallback
        };
        controller.appendPartial(partialRequest, this);
        function appendCallback() {
            console.log(this);
            setSubs([
                ['mapLayer', mapView.showLayer],
                ['mapLoaded', model.loadMetaData],
                ['dataLoaded.metaData', mapView.addInitialLayers], //adds zone borders to geojson
                ['dataLoaded.metaData', resultsView.init],
                ['dataLoaded.metaData', mapView.placeProjects],
                ['dataLoaded.metaData', mapView.overlayMenu],
                ['dataLoaded.raw_project', filterView.init],
                ['overlayRequest', mapView.addOverlayData],
                ['joinedToGeo', mapView.addOverlayLayer],
                ['previewBuilding', mapView.showPopup],
                ['filteredData', mapView.filterMap],
                ['hoverBuildingList', mapView.highlightBuilding]
              
                
            ]);
            

            this.originalZoom = 11;
            this.originalCenter = [-77, 38.9072];
            //Add the map
            mapboxgl.accessToken = 'pk.eyJ1Ijoicm1jYXJkZXIiLCJhIjoiY2lqM2lwdHdzMDA2MHRwa25sdm44NmU5MyJ9.nQY5yF8l0eYk2jhQ1koy9g';
            this.map = new mapboxgl.Map({
              container: 'map', // container id
              style: 'mapbox://styles/rmcarder/cizru0urw00252ro740x73cea',
              zoom: mapView.originalZoom,
              center: mapView.originalCenter,
              minZoom: 3,
              preserveDrawingBuffer: true
            });
            
            this.map.addControl(new mapboxgl.NavigationControl(), 'bottom-left');
            
            this.map.on('load', function(){
                setState('mapLoaded',true);
            });

            this.map.on('zoomend', function(){
                
                d3.select('#reset-zoom')
                    .style('display',function(){
                        if ( Math.abs(mapView.map.getZoom() - mapView.originalZoom) < 0.001
                             && Math.abs(mapView.map.getCenter().lng - mapView.originalCenter[0]) < 0.001
                             && Math.abs(mapView.map.getCenter().lat - mapView.originalCenter[1]) < 0.001 ) {
                                return 'none';
                        } else { 
                            return 'block';
                        }
                    })
                    .on('click', function(){
                        
                        mapView.map.flyTo({
                            center: mapView.originalCenter,
                            zoom: mapView.originalZoom
                        });
                        
                    });

            });

        }

    },


    initialOverlays: [],

    findOverlayConfig: function(key,value){
        return mapView.initialOverlays.filter(function(v) {
            return v[key] === value;
        })[0];
    },
    buildOverlayOptions: function(){

        //TODO we want to move this config data into it's own file or to the api
        mapView.initialOverlays = [
            {   name:"crime",
                display_name: "Crime",
                display_text: "Number of crime incidents reported in the past 3 months.",
                zones: ["ward","neighborhood_cluster"],
                aggregate_endpoint_base: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/crime/all/",
                available_aggregates: ["ward", "neighborhood_cluster"],
                default_layer: "ward"
            },
            {   name:"building_permits",
                display_name: "Building Permits",
                display_text: "Number of building permits issued in the zone during 2016.",
                zones: ["ward","neighborhood_cluster"],
                aggregate_endpoint_base: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/building_permits/all/",
                available_aggregates: ["ward", "neighborhood_cluster"],
                default_layer: "neighborhood_cluster"
            },
            {   name:"more_building_permits_1",
                display_name: "More Building Permits 1",
                display_text: "This is duplicated just as a demo, because we haven't added more api endpoints yet.",
                zones: ["ward","neighborhood_cluster"],
                aggregate_endpoint_base: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/building_permits/all/",
                available_aggregates: ["ward", "neighborhood_cluster"],
                default_layer: "neighborhood_cluster"
            },
            {   name:"more_building_permits_2",
                display_name: "More Building Permits 2",
                display_text: "This is duplicated just as a demo, because we haven't added more api endpoints yet.",
                zones: ["ward","neighborhood_cluster"],
                aggregate_endpoint_base: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/building_permits/all/",
                available_aggregates: ["ward", "neighborhood_cluster"],
                default_layer: "neighborhood_cluster"
            },
            {   name:"more_building_permits_3",
                display_name: "More Building Permits 3",
                display_text: "This is duplicated just as a demo, because we haven't added more api endpoints yet.",
                zones: ["ward","neighborhood_cluster"],
                aggregate_endpoint_base: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/building_permits/all/",
                available_aggregates: ["ward", "neighborhood_cluster"],
                default_layer: "neighborhood_cluster"
            }
        ];
    },

    overlayMenu: function(msg, data){    

        if ( data === true ) {
            mapView.buildOverlayOptions();    
            mapView.initialOverlays.forEach(function(overlay){
                new mapView.overlayMenuOption(overlay);
            });
        } else {
            console.log("ERROR data loaded === false")
        }
    },
    overlayMenuOption: function(overlay){
        

        var parent = d3.select('#overlay-menu')
                .classed("ui styled fluid accordion",true)  //semantic UI styling
            
        var title = parent.append("div")
                      .classed("title overlay-title",true);
            title.append("i")
                .classed("dropdown icon",true);
            title.append("span")
                .classed("title-text",true)
                .text(overlay.display_name)
            title.attr("id", "overlay-"+overlay.name); //TODO need to change this to different variable after changing meta logic structure

        var content = parent.append("div")
              .classed("content",true)
              .text(overlay.display_text)

        $('.ui.accordion').accordion(); //alternately allow multiple to be open: .accordion({'exclusive':false})
        
        //Set it up to trigger the layer when title is clicked
        document.getElementById("overlay-"+overlay.name).addEventListener("click", clickCallback);
        function clickCallback(){
            console.log("you clicked on the overlay title for " + overlay.name);
            var existingOverlayType = getState().overlaySet !== undefined ? getState().overlaySet[0].overlay : null;
            console.log("changing from " + existingOverlayType + " to " + overlay.name);

            if ( existingOverlayType !== overlay.name ) {
                    setState('overlayRequest', {overlay: overlay.name, activeLayer: getState().mapLayer[0]});                     
                } else {
                    mapView.clearOverlay();
                };

            //probably not currently working - disabling of layers
            mapView.layerMenuOptions.forEach(function(opt){
                if(thisOption.availableLayerNames.indexOf(opt.name) === -1){
                    opt.makeUnavailable();
                }
                else{
                    opt.makeAvailable();
                }
            });

        }; //end clickCallback
    },



    
    onReturn: function(){
        console.log('nothing to do');
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

        var grouping = data.activeLayer

        if ( getState()['joinedToGeo.' + data.overlay + '_' + data.activeLayer] === undefined ) {
            function dataCallback(d) {
                if (d.items === null){
                    //If the data returned is null that aggregation is not available. Use default aggregation instead
                    //var default_layer = 'ward'; //TODO should make this a config param for each layer so that it can vary
                    var config = mapView.findOverlayConfig('name',data.overlay)
                    var default_layer = config.default_layer
                    setState('mapLayer',default_layer);
                    setState('overlayRequest', {overlay: data.overlay, activeLayer: default_layer});
                } else {      
                    controller.joinToGeoJSON(data.overlay,grouping,data.activeLayer); // joins the overlay data to the geoJSON *in the dataCollection* not in the mapBox instance
                };
            }

            var overlayConfig = mapView.findOverlayConfig('name',data.overlay)
            var url = overlayConfig.aggregate_endpoint_base + data.activeLayer;
            var dataRequest = {
                name: data.overlay + "_" + data.activeLayer, //e.g. crime
                url: url, 
                callback: dataCallback
            };

            controller.getData(dataRequest);
        } else {
            mapView.showOverlayLayer(data.overlay, data.activeLayer);
        }
    },

    addOverlayLayer: function(msg,data){ // e.g. data = {overlay:'crime',grouping:'neighborhood_cluster',activeLayer:'neighborhood_cluster'}
        //Called after the data join from addOverlayData's callback

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

        setState('mapLayer', activeLayer);

        //Toggle the overlay colors themselves
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
        }
    ],
    addInitialLayers: function(msg,data){

        //This function adds the zone layers, i.e. ward, zip, etc.
        if ( data === true ) {
            //controller.appendPartial('layer-menu','main-view');
            mapView.initialLayers.forEach(function(layer){  // refers to mapView instead of this bc being called form PubSub
                                                            //  context. `this` causes error
                mapView.addLayer(layer);
            });            
        } else {
            console.log("ERROR data loaded === false")
        };
    },
    addLayer: function(layer){
        //Adds an individual zone (ward, zip, etc.) to the geoJSON

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


    layerMenuOptions: [],


    showLayer: function(msg,data) {
        //'data' is the name of the zone type (layer) to show

        //first clear all existing layers
        var layerChoices = mapView.initialLayers.map(function(i) {
            return i['source']
        })


        for (var i = 0; i < layerChoices.length; i++) {
            mapView.map.setLayoutProperty(layerChoices[i] + 'Layer', 'visibility', 'none');
        }

        var previousOverlayState = getState().overlaySet
        var existingOverlayType = getState().overlaySet !== undefined ? getState().overlaySet[0].overlay : null;
        if (previousOverlayState !== undefined ) {
            var previousLayer = previousOverlayState[0].activeLayer
            mapView.clearOverlay();
        }
        
        //Toggle boundaries ('layer')
        mapView.map.setLayoutProperty(data + 'Layer', 'visibility', 'visible');

        //Make sure the menu reflects the current choice
        d3.selectAll('#layer-menu a')
            .attr('class','');
        d3.select('#' + data + '-menu-item')
            .attr('class','active');

        //Keep the currently selected overlay data choice with the new zone type
        if (existingOverlayType !== null){
            setState('overlayRequest', {overlay: existingOverlayType, activeLayer: data});
        };


    },

    placeProjects: function(msg,data){ // some repetition here with the addLayer function used for zone layers. could be DRYer if combined
                                       // or if used constructor with prototypical inheritance
        if ( data === true ) {
            //msg and data are from the pubsub module that this init is subscribed to. 
            //when called from dataLoaded.metaData, 'data' is boolean of whether data load was successful
            console.log(msg,data);
            var dataURLInfo = model.dataCollection.metaData.project.api;
            var dataURL = dataURLInfo.raw_endpoint;
            var dataRequest = {
                    name: 'raw_project',
                    url: dataURL, 
                    callback: dataCallback
                };
            controller.getData(dataRequest);

            function dataCallback() {   
                console.log('in callback');     
                mapView.convertedProjects = controller.convertToGeoJSON(model.dataCollection.raw_project);
                mapView.convertedProjects.features.forEach(function(feature){
                    feature.properties.matches_filters = true;
                });
                mapView.listBuildings();
                mapView.map.addSource('project', {
                  'type': 'geojson',
                  'data': mapView.convertedProjects
                });
                mapView.circleStrokeWidth =  1;
                mapView.circleStrokeOpacity =  1;
                mapView.map.addLayer({
                    'id': 'project',
                    'type': 'circle',
                    'source': 'project',
                    'paint': {
                        'circle-radius': {
                            'base': 1.75,
                            'stops': [[12, 3], [15, 32]]
                        }, 
                        'circle-opacity': 0.3,      
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
                        },
                    'circle-stroke-width': mapView.circleStrokeWidth,
                    'circle-stroke-opacity': mapView.circleStrokeOpacity,
                    
                    'circle-stroke-color': {
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
                    console.log(e);
                    var building = (mapView.map.queryRenderedFeatures(e.point, { layers: ['project'] }))[0];
                    console.log(building);
                    if ( building === undefined ) return;
                    setState('previewBuilding', building);
                   });               
            } // end dataCallback
        } else {
             console.log("ERROR data loaded === false");
        }

    },

    showPopup: function(msg,data){
            console.log(data);

            if ( document.querySelector('.mapboxgl-popup') ){                
                d3.select('.mapboxgl-popup')
                    .remove();
            }
                
            var lngLat = {
                lng: data.properties.longitude,
                lat: data.properties.latitude,
            }
            var popup = new mapboxgl.Popup({ 'anchor': 'top-right' }) 
                .setLngLat(lngLat)        
                .setHTML('<a href="#">See more about ' + data.properties.proj_name + '</a>' )
                .addTo(mapView.map);

            popup._container.querySelector('a').onclick = function(e){
                e.preventDefault();
                setState('selectedBuilding', data);
                setState('switchView', buildingView);
            };

    },
    filterMap: function(msg, data){
        
        mapView.convertedProjects.features.forEach(function(feature){
            if ( data.indexOf(feature.properties.nlihc_id) !== -1 ){
                feature.properties.matches_filters = true;
            } else {
                feature.properties.matches_filters = false;
            }
        });
        mapView.map.getSource('project').setData(mapView.convertedProjects);
        mapView.map.setFilter('project',['==','matches_filters', true]);
        mapView.listBuildings();
        setTimeout(function(){
            mapView.growShrinkId = requestAnimationFrame(mapView.animateSize);
        },20);
        /*
        console.log(data.toString().replace(/([^,]+)/g,"'$1'"));    
        var idStr = data.toString().replace(/([^,]+)/g,"'$1'")
        var str = "NL000001";
        mapView.map.setFilter('project',['in','nlihc_id', data]);*/
    },
    animateSize: function(timestamp){
        setTimeout(function(){
            mapView.shrinkGrow = mapView.shrinkGrow || 'grow';
            mapView.circleStrokeWidth = mapView.shrinkGrow === 'grow' ? mapView.circleStrokeWidth * 2 : mapView.circleStrokeWidth / 2;// ( 20 - mapView.circleStrokeWidth ) / ( 1000 / ( timestamp - mapView.lastTimestamp ));
            mapView.circleStrokeOpacity = mapView.shrinkGrow === 'grow' ? mapView.circleStrokeOpacity / 1.2 : mapView.circleStrokeOpacity * 1.2;
            mapView.map.setPaintProperty('project','circle-stroke-width',mapView.circleStrokeWidth);
            mapView.map.setPaintProperty('project','circle-stroke-opacity',mapView.circleStrokeOpacity);
            if (mapView.shrinkGrow === 'grow' && mapView.circleStrokeWidth >= 32){
                
                mapView.shrinkGrow = 'shrink';
            } 
            if (mapView.shrinkGrow === 'shrink' && mapView.circleStrokeWidth <= 1){
                mapView.shrinkGrow = 'grow';
                cancelAnimationFrame(mapView.growShrinkId);
            } else {
                
                mapView.growShrinkId = requestAnimationFrame(mapView.animateSize);            
            }
        }, (1000 / 20) );
    },
    listBuildings: function(){

        
        
            var data = mapView.convertedProjects.features.filter(function(feature){
                return feature.properties.matches_filters === true;
            });

            d3.select('#matching-count')
             .text('(' + data.length + ')');

            var t = d3.transition()
              .duration(750);
            var preview = d3.select('#buildings-list')
              
            var listItems = preview.selectAll('div')
            .data(data, function(d){ return d.properties.nlihc_id; });

            listItems.attr('class','update');

            listItems.enter().append('div')
            //.attr('class','enter')
            .merge(listItems)
            .html(function(d){
                return  '<p>' + d.properties.proj_name + '<br />' + 
                        d.properties.proj_addre + '<br />' +
                        'Owner: ' + d.properties.hud_own_name + '</p>';
            })
            .on('mouseenter',function(d){
                mapView['highlight-timer-' + d.properties.nlihc_id] = setTimeout(function(){
                    setState('hoverBuildingList', d.properties.nlihc_id);
                },500);  // timeout minimizes inadvertent highlighting and gives more assurance that quick user actions
                         // won't trip up all the createLayers and remove layers.               
            })
            .on('mouseleave', function(d){
                clearTimeout(mapView['highlight-timer-' + d.properties.nlihc_id]);
                setState('hoverBuildingList', false);
                if ( mapView.map.getLayer('project-highlight-' + d.properties.nlihc_id) ) {
                    mapView.map.setFilter('project-highlight-' + d.properties.nlihc_id, ['==','nlihc_id', '']);
                    mapView.map.removeLayer('project-highlight-' + d.properties.nlihc_id);     
                }
            })
            .on('click', function(d){

                mapView.map.flyTo({
                    center: [d.properties.longitude, d.properties.latitude],
                    zoom: 15
                });
                setState('previewBuilding', d);
            })
            
            .attr('tabIndex',0)
            .transition().duration(100)
            .attr('class','enter');

            listItems.exit()
            .attr('class', 'exit')
            .transition(t)
            .remove();
        
    },
    highlightBuilding(msg, data){
        if (data){
            mapView.map.addLayer({
                'id': 'project-highlight-' + data,
                'type': 'circle',
                'source': 'project',
                'paint': {
                    'circle-blur': 0.2,
                    'circle-color':'transparent',
                    'circle-radius': {
                        'base': 1.75,
                        'stops': [[12, 10], [15, 40]]
                    },
                    'circle-stroke-width': 4,
                    'circle-stroke-opacity': 1,                
                    'circle-stroke-color': '#4D90FE'
                },
                'filter': ['==','nlihc_id', data]
            });            
        }
    }
};

