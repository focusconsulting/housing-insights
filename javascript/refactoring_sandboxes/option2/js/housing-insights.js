"use strict";

/* 
 * MODEL **********************************
 */

var model = {  // TODO (?) change to a module similar to State and Subscribe so that dataCollection can only be accessed
               // through functions that the module returns to the handlers
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
    }
    
};

/* STATE ********************************
 *
 * State module keeps the state object private; only access is through module-scoped functions with closure over state. We have access
 * to those functions, and thus to state, by returning them to controller.controlState.
 */

function StateModule() {
        
    var state = {};

    function logState(){
        console.log(state);
    }

    function getState(){
        return state;
    }

    function setState(key,value) { // making all state properties arrays so that previous value is held on to
                                   // current state to be accessed as state[key][0].
        if ( state[key] === undefined ) {
            state[key] = [value];
            PubSub.publish(key, value);
            console.log('STATE CHANGE', key, value);
        } else if ( state[key][0] !== value ) {
            state[key].unshift(value);
            PubSub.publish(key, value);
            console.log('STATE CHANGE', key, value);
            if ( state[key].length > 2 ) {
                state[key].length = 2;
            }
        }
        
    }
    return {
        logState: logState,
        getState: getState,
        setState: setState
    }
}

/*
 * Subscriptions module for setting, canceling, and logging all PubSub subscriptions. Automatically creates token for each unique
 * plus function (string) combination so that we don't have to remember them and so that duplicate topic-function pairs
 * cannot be made.
 */

 function SubscribeModule() {
    var subscriptions = {};

    function logSubs() {
        console.log(subscriptions);
    }

    function createToken(topic, fnRef){
        var functionHash = 'f' + fnRef.toString().hashCode();
        var str = topic + fnRef;
        var token = 'sub' + str.hashCode();
        return {
            token: token,
            fn: functionHash
        }
    }

    function setSubs(subsArray) { // subsArray is array of topic/function pair arrays
        subsArray.forEach(function(pair){
            var topic = pair[0],
                fnRef = pair[1],
                tokenObj = createToken(topic,fnRef);
            
            if ( subscriptions[tokenObj.fn] === undefined ) {
                subscriptions[tokenObj.fn] = {};
            }
            if ( subscriptions[tokenObj['fn']][topic] === undefined ) {
                subscriptions[tokenObj['fn']][topic] = PubSub.subscribe(topic,fnRef);  
            } else {
                throw 'Subscription token is already in use.';
            }
        });
    }

    function cancelSub(topic,fnRef) { // for canceling single subscription
        var tokenObj = createToken(topic,fnRef);
        if ( subscriptions[tokenObj.fn] !== undefined && subscriptions[tokenObj['fn']][topic] !== undefined ) {
            PubSub.unsubscribe( subscriptions[tokenObj['fn']][topic] );
            delete subscriptions[tokenObj['fn']][topic];
            if ( Object.keys(subscriptions[tokenObj['fn']]).length === 0 ) {
                delete subscriptions[tokenObj['fn']];
            }
        } else {
            throw 'Subscription does not exist.';
        }
    }

    function cancelFunction(fnRef) {
        var tokenObj = createToken('',fnRef);
        PubSub.unsubscribe(fnRef);
        delete subscriptions[tokenObj['fn']];
    }

    return {
        logSubs:logSubs,
        setSubs:setSubs,
        cancelSub:cancelSub,
        cancelFunction: cancelFunction
    };

 }

 
/*
 * CONTROLLER ******************************
 */

var controller = {
    controlState: StateModule(),
    controlSubs: SubscribeModule(),
    init: function(){        
        mapView.init();        
    },                                  
    getData: function(dataRequest){
        var paramsUnderscore = dataRequest.params ? '_' + dataRequest.params.join('_') : '';
        if (model.dataCollection[dataRequest.name + paramsUnderscore] === undefined) { // if data not in collection
            var meta = this.dataMeta(dataRequest.name);
            var paramsSlash = dataRequest.params ? '/' + dataRequest.params.join('/') : '';
            var extension = meta.extension || '';
            d3.json(meta.path + dataRequest.name + paramsSlash + extension, function(error, data){
                if ( error ) { console.log(error); }
                model.dataCollection[dataRequest.name + paramsUnderscore] = data;
                setState('dataLoaded.' + dataRequest.name + paramsUnderscore, true );
                if ( dataRequest.callback !== undefined) { // if callback has been passed in 
                    dataRequest.callback(data);
                }                               
            });
               
        } else {
            // TODO publish that data is available
            if ( fn !== undefined) { // if callback has been passed in 
                fn(model.dataCollection[dataRequest.name + paramsUnderscore]);
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

        setSubs([
            ['mapLoaded',mapView.addInitialLayers],
            ['mapLayer', mapView.showLayer],
            ['mapLoaded', sideBar.init],
            ['mapLoaded',mapView.addInitialOverlays]
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
    initialOverlays: ['crime','building_permits'],
    addInitialOverlays: function(){
        mapView.initialOverlays.forEach(function(overlay){
            mapView.addOverlay(overlay);
        });      
    },
    addOverlay: function(overlay){
        var grouping = getState().mapLayer[0];
        var dataRequest = {
            name:overlay,
            params: ['all',grouping]
        };
        controller.getData(dataRequest);
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
    addInitialLayers: function(msg,data){
        if ( data === true ) {
            controller.appendPartial('layer-menu','main-view');
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
                setState('mapLayer',layer.source);                
            });
    },
    showLayer: function(msg,data) {
        var previousLayer = getState().mapLayer[1];
        if (previousLayer !== undefined ) {
            mapView.map.setLayoutProperty(previousLayer + 'Layer', 'visibility', 'none');            
        }
        mapView.map.setLayoutProperty(data + 'Layer', 'visibility', 'visible');
        d3.selectAll('#layer-menu a')
            .attr('class','');
        d3.select('#' + data + '-menu-item')
            .attr('class','active');

    }
};

var sideBar = {
    init: function() {
        setSubs([
            ['firstPieReady', sideBar.setDropdownOptions],
            ['mapLayer',sideBar.changeZoneType],
            ['pieZone', sideBar.changeZoneType]
        ]);
        sideBar.charts = [];
        var instances = ['subsidized','cat_expiring','cat_failing_insp','cat_at_risk'];
        instances.forEach(function(instance, i){
            sideBar.charts[i] = new DonutChart({
                dataRequest: {
                    name: 'raw',
                    params: ['project']
                },
                field: instance,
                container: '#pie-' + i,
                width: 95,
                height: 115,
                zoneType: 'ward',
                zoneName: 'All',
                index: i,
                margin: {
                    top:0,
                    right:0,
                    bottom:20,
                    left:0
                }
            })
        });
    },
    zoneMapping: { // object to map mapLayer names (the keys) to the field in the data
                  // later code adds an array of all the values for each type to the objects
                  // for populating the dropdown list
        ward: {
          name: 'ward'
          
        },
        tract: {
          name: 'census_tract'
          
        },
        zip: {
          name: 'zip'
        },
        neighborhood: {
          name: 'neighborhood_cluster_desc'
        }
    },
    setDropdownOptions: function() {
               
            var activeLayer = getState().mapLayer[0];            
            if ( sideBar.zoneMapping[activeLayer].values === undefined ) { // i.e. the  zones withing the zoneType have not been 
                                                                       // enumerated yet
                sideBar.zoneMapping[activeLayer].values = [];
                sideBar.charts[0].nested.forEach(function(obj) {
                    sideBar.zoneMapping[activeLayer].values.push(obj.key)
                });                                    
            }
            var selector = document.getElementById('zone-selector');
            selector.onchange = function(e){
                setState('pieZone', e.target.selectedOptions[0].value);                 
            };
            selector.innerHTML = '';
            sideBar.zoneMapping[activeLayer].values.forEach(function(zone,i){
                var option = document.createElement('option');
                if ( i === 0 ) { option.setAttribute('selected','selected'); }
                option.setAttribute('class',activeLayer);
                option.setAttribute('value',zone);
                option.id = zone.toLowerCase().replace(/ /g,'-');
                option.innerHTML = zone;
                selector.appendChild(option);
            });
        
    },
    changeZoneType: function(msg){
        var zoneType = getState().mapLayer[0];
        document.getElementById('zone-drilldown-instructions').innerHTML = 'Choose a ' + zoneType;
        if (getState().firstPieReady) { 
            if (msg === 'mapLayer') {
                setState('pieZone', 'All');
            }
            var zoneName = getState().pieZone[0];                
            sideBar.charts.forEach(function(chart){
                chart.pieVariable = chart.returnPieVariable(chart.field,zoneType,zoneName);
                chart.update();
            });
            if ( msg === 'mapLayer' ) { // if fn was called by changing mapLayer state. if not, leave dropdown
                                        // menu alone
                sideBar.setDropdownOptions();
            }
        } else { // if this function was called suring initial setup, before pies were ready
            setState('pieZone', 'All');
        }
    }

};

var detailView = {
    init: function() {
        setSubs([

        ]);
        //TODO
    }
    //rest of detailView here
}

/* Aliases */

var setState = controller.controlState.setState,
    getState = controller.controlState.getState,
    logState = controller.controlState.logState;

var setSubs = controller.controlSubs.setSubs,
    logSubs = controller.controlSubs.logSubs,
    cancelSub = controller.controlSubs.cancelSub,
    cancelFunction = controller.controlSubs.cancelFunction;

/*
 * POLYFILLS AND HELPERS ***********************
 */

 // HELPER array.move()

 Array.prototype.move = function (old_index, new_index) { // HT http://stackoverflow.com/questions/5306680/move-an-array-element-from-one-array-position-to-another
                                                          // native JS for moving around array items
                                                          // used e.g. in pie-chart.js to always move the all-zone option to the top 
    while (old_index < 0) {
        old_index += this.length;
    }
    while (new_index < 0) {
        new_index += this.length;
    }
    if (new_index >= this.length) {
        var k = new_index - this.length;
        while ((k--) + 1) {
            this.push(undefined);
        }
    }
    this.splice(new_index, 0, this.splice(old_index, 1)[0]);
    return this; // for testing purposes
};

// HELPER String.hashCode()

String.prototype.hashCode = function() {
  var hash = 0, i, chr, len;
  if (this.length === 0) return hash;
  for (i = 0, len = this.length; i < len; i++) {
    chr   = this.charCodeAt(i);
    hash  = ((hash << 5) - hash) + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};

// HELPER String.cleanString()

String.prototype.cleanString = function() { // lowercase and remove punctuation and replace spaces with hyphens; delete punctuation
    return this.replace(/[ \\\/]/g,'-').replace(/['"”’“‘,\.!\?;\(\)&]/g,'').toLowerCase();
};

// Polyfill for Array.findIndex()

// https://tc39.github.io/ecma262/#sec-array.prototype.findIndex
if (!Array.prototype.findIndex) {
  Object.defineProperty(Array.prototype, 'findIndex', {
    value: function(predicate) {
     // 1. Let O be ? ToObject(this value).
      if (this == null) {
        throw new TypeError('"this" is null or not defined');
      }

      var o = Object(this);

      // 2. Let len be ? ToLength(? Get(O, "length")).
      var len = o.length >>> 0;

      // 3. If IsCallable(predicate) is false, throw a TypeError exception.
      if (typeof predicate !== 'function') {
        throw new TypeError('predicate must be a function');
      }

      // 4. If thisArg was supplied, let T be thisArg; else let T be undefined.
      var thisArg = arguments[1];

      // 5. Let k be 0.
      var k = 0;

      // 6. Repeat, while k < len
      while (k < len) {
        // a. Let Pk be ! ToString(k).
        // b. Let kValue be ? Get(O, Pk).
        // c. Let testResult be ToBoolean(? Call(predicate, T, « kValue, k, O »)).
        // d. If testResult is true, return k.
        var kValue = o[k];
        if (predicate.call(thisArg, kValue, k, o)) {
          return k;
        }
        // e. Increase k by 1.
        k++;
      }

      // 7. Return -1.
      return -1;
    }
  });
}



/* Go! */

controller.init(); 