"use strict";
/* 
 * MODEL **********************************
 */

var model = {
    dataCollection: {
  
    },
    manifest: { // for purpose of example, this is hard coded in but could instead reference actual data manifest
        patterns: [
            {
                path: 'http://hiapidemo.us-east-1.elasticbeanstalk.com/api/',
                members: ['raw','crime','building_permits'],
                extension: null,
                type:'json'
            },
            {
                path: 'data/',
                members: ['ward','tract','neighborhood','zip', 'zillow'],
                extension: '.geojson',
                type:'json'
            }
        ]
    },
    state: {
        mapLayer: null
    }
};


/*
 * CONTROLLER ******************************
 */

var controller = {
    init: function(){
        this.setInitialSubscriptions(); // set initital PubSub subscriptions
        mapView.init();
        //sibeBar.init()  to come
    },
                                        //p3 [optional] = callback function
    getData: function(dataName, params, fn){
        var paramsUnderscore = params ? '_' + params.join('_') : '';
        if (model.dataCollection[dataName + paramsUnderscore] === undefined) { // if data not in collection
            var meta = this.dataMeta(dataName, params);
            console.log(meta);
            var paramsSlash = params ? '/' + params.join('/') : '';
            var extension = meta.extension || '';
            console.log(meta.path + dataName + paramsSlash + extension );
            d3.json(meta.path + dataName + paramsSlash + extension, function(error, data){
                if ( error ) { console.log(error); }
                model.dataCollection[dataName + paramsUnderscore] = data;
                // TODO publish that data is available
                if ( fn !== undefined) { // if callback has been passed in 
                    fn(data);
                }                               
            });
               
        } else {
            // TODO publish that data is available
            if ( fn !== undefined) { // if callback has been passed in 
                fn(model.dataCollection[dataName + paramsUnderscore]);
            }              
        }
    },
    dataMeta: function(dataName) {
        var patternMatch = model.manifest.patterns.find(function(pattern){
            return pattern.members.indexOf(dataName) !== -1;
        });
        return {
            path: patternMatch.path,
            type: patternMatch.type,
            extension: patternMatch.extension
        };
    },
    subscriptions: {},
    setInitialSubscriptions: function() {
        this.subscriptions.mapLoaded = PubSub.subscribe( 'mapBox', mapView.addInitialLayers );
    },
    appendPartial: function(partial, elemID){
        d3.html('partials/' + partial + '.html', function(fragment){
            document.getElementById(elemID).appendChild(fragment);
        });
    }
};

/* 
 * Views **********************************
 */



var mapView = {
    init: function() {        
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
        controller.subscriptions.layerMenu = PubSub.subscribe( 'layer-menu', mapView.showLayer);
        this.map.on('load', function(){
            PubSub.publish( 'mapBox', 'style_loaded' ); // announce style loaded when map is ready. addInitialLayers subscribes
                                                        // to this announcement, so will only fire when the announcement is made
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
            visibility: 'none'
    
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
    addInitialLayers: function(){
        controller.appendPartial('layer-menu','main-view');
        mapView.initialLayers.forEach(function(layer){  // refers to mapView instead of this bc being called form PubSub
                                                        //  context. `this` causes error
            mapView.addLayer(layer);
        });
    },
    addLayer: function(layer){
        if ( layer.visibility === 'visible' ) {
            model.state.mapLayer = layer.source;
        }
        var name = layer.source + 'Layer';
        controller.getData(layer.source, null, function (data) {
            console.log(data);
            if ( mapView.map.getSource( name ) === undefined ) {
                mapView.map.addSource(layer.source + 'Layer', {
                    type:'geojson',
                    data: data
                });
            }
            mapView.map.addLayer({
              'id': name,
              'type': 'line',
              'source': name,
              'paint': {
                'line-color': layer.color,
                'line-width': 1
              },
              'layout': {
                'visibility': layer.visibility
              }
            });
            mapView.addToLayerMenu(layer);
        });               
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

                PubSub.publish( 'layer-menu', layer.source);
            });
    },
    showLayer: function(msg,data) {
        if ( data === model.state.mapLayer ) {
            return
        }
        mapView.map.setLayoutProperty(model.state.mapLayer + 'Layer', 'visibility', 'none');
        mapView.map.setLayoutProperty(data + 'Layer', 'visibility', 'visible');
        model.state.mapLayer = data;
        d3.selectAll('#layer-menu a')
            .attr('class','');
        d3.select('#' + data + '-menu-item')
            .attr('class','active');

    }
};

var sideBar = {
    init: function() {
        //TODO
    }
    // rest of sidebar view here, including pies
};

var detailView = {
    init: function() {
        //TODO
    }
    //rest of detailView here
}

controller.init(); 