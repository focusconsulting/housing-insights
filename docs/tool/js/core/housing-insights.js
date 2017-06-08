"use strict";

/* 
 * MODEL **********************************
 */

var model = {  // TODO (?) change to a module similar to State and Subscribe so that dataCollection can only be accessed
               // through functions that the module returns to the handlers
    dataCollection: {
  
    },
    loadMetaData: function(){
        var metaDataRequest = {
            url: model.URLS.metaData,
            name: "metaData"
        }
        controller.getData(metaDataRequest);
    },
    // Here's where we keep hardcoded URLs. The aim is to make this as short as possible.
    //NOTE raw data sources have their urls included in the metaData
    URLS: {
      geoJSONPolygonsBase: "/tool/data/",
      metaData: "/tool/data/meta.json",
      filterData: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/filter/"
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
        } else if ( state[key][0] !== value ) { // only for when `value` is a string or number. doesn't seem
                                                // to cause an issue when value is an object, but it does duplicate
                                                // the state. i.e. key[0] and key[1] will be equivalent. avoid that
                                                // with logic before making the setState call.
            state[key].unshift(value);
            PubSub.publish(key, value);
            console.log('STATE CHANGE', key, value);
            if ( state[key].length > 2 ) {
                state[key].length = 2;
            }
        }
        
    }
    function clearState(key) {
        delete state[key];
         PubSub.publish('clearState', key);
         console.log('CLEAR STATE', key);
    }
    return {
        logState: logState,
        getState: getState,
        setState: setState,
        clearState: clearState
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
        setSubs([
            ['switchView', controller.switchView]
        ]);
        setState('activeView',mapView);        
        mapView.init();        
    },
    // dataRequest is an object with the properties 'name', 'url' and 'callback'. The 'callback' is a function
    // that takes as an argument the data returned from getData.                             
    getData: function(dataRequest){
        if (model.dataCollection[dataRequest.name] === undefined) { // if data not in collection
            d3.json(dataRequest.url, function(error, data){
                if ( error ) { console.log(error); }
                if ( data.items !== null ) {
                    model.dataCollection[dataRequest.name] = data;
                    setState('dataLoaded.' + dataRequest.name, true );
                    if ( dataRequest.callback !== undefined ) { // if callback has been passed in 
                        dataRequest.callback(data);
                    }                              
                } else {
                    //This approach suggests that either the caller (via callback) or the subscriber (via dataLoaded state change)
                    //should appropriately handle a null data return. If they don't handle it, they'll probably get errors anyways.
                    setState('dataLoaded.' + dataRequest.name, false );
                    if ( dataRequest.callback !== undefined ) { // if callback has been passed in 
                        dataRequest.callback(data);
                    }
                }
            });
               
        } else {
            // TODO publish that data is available every time it's requested or only on first load?
            if ( dataRequest.callback !== undefined ) { // if callback has been passed in 
                console.log(model.dataCollection[dataRequest.name]);
                dataRequest.callback(model.dataCollection[dataRequest.name]);
            }              
        }
    },                                         // bool
    appendPartial: function(partialRequest,context){
        partialRequest.container = partialRequest.container || 'body-wrapper'; 
        d3.html('partials/' + partialRequest.partial + '.html', function(fragment){
            if ( partialRequest.transition ) {
                fragment.querySelector('.main-view').classList.add('transition-right');
                setTimeout(function(){
                    document.querySelector('.transition-right').classList.remove('transition-right');
                }, 200);
            }
            document.getElementById(partialRequest.container).appendChild(fragment);
            if ( partialRequest.callback ) {
                partialRequest.callback.call(context); // call the callbBack with mapView as the context (the `this`) 
            }
        });
    },
    joinToGeoJSON: function(overlay,grouping,activeLayer){
        model.dataCollection[activeLayer].features.forEach(function(feature){
            var zone = feature.properties.NAME;
            var dataKey = overlay + '_' + grouping;
            feature.properties[overlay] = model.dataCollection[dataKey].items.find(function(obj){
                return obj.group === zone;
            }).count;
        });
        setState('joinedToGeo.' +  overlay + '_' + activeLayer, {overlay:overlay, grouping:grouping, activeLayer:activeLayer});
        // e.g. joinedToGeo.crime_neighborhood, {overlay:'crime',grouping:'neighborhood_cluster',activeLayer:'neighborhood_cluster'}
    },
    convertToGeoJSON: function(data){ // thanks, Rich !!! JO. takes non-geoJSON data with latititude and longitude fields
                                      // and returns geoJSON with the original data in the properties field
        var features = data.items.map(function(element){ 
          return {
            'type': 'Feature',
            'geometry': {
              'type': 'Point',
              'coordinates': [+element.longitude, +element.latitude]
            },
            'properties': element        
          }
        });
          return {
          'type': 'FeatureCollection',
          'features': features
        }
    },
    // ** NOTE re: classList: not supported in IE9; partial support in IE 10
    switchView: function(msg,data) {

        var container = document.getElementById(getState().activeView[0].el);
        container.classList.add('fade');
        console.log( data === getState().activeView[1]);
        setTimeout(function(){
            container.classList.remove('fade');
            container.classList.add('inactive');
           
            if ( data !== getState().activeView[1] ){   // if not going back             
                container.classList.add('transition-left');
                data.init();
                controller.backToggle = 0;                
            } else {
                if ( controller.backToggle === 0 ) {
                    container.classList.add('transition-right');
                } else {
                    container.classList.add('transition-left');
                }
                controller.backToggle = 1 - controller.backToggle;
                document.getElementById(data.el).classList.remove('inactive');
                document.getElementById(data.el).classList.remove('transition-left');
                document.getElementById(data.el).classList.remove('transition-right');
                
                data.onReturn();
            }
            setState('activeView',data);
        }, 500);
    },
    backToggle: 0,
    goBack: function(){
        setState('switchView', getState().activeView[1])
    }

}

/* Aliases */

var setState = controller.controlState.setState,
    getState = controller.controlState.getState,
    logState = controller.controlState.logState,
    clearState = controller.controlState.clearState;

var setSubs = controller.controlSubs.setSubs,
    logSubs = controller.controlSubs.logSubs,
    cancelSub = controller.controlSubs.cancelSub,
    cancelFunction = controller.controlSubs.cancelFunction;

/*
 * POLYFILLS AND HELPERS ***********************
 */

 // HELPER get parameter by name
 var getParameterByName = function(name, url) { // HT http://stackoverflow.com/a/901144/5701184
      if (!url) {
        url = window.location.href;
      }
      name = name.replace(/[\[\]]/g, "\\$&");
      var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
          results = regex.exec(url);
      if (!results) return null;
      if (!results[2]) return '';
      return decodeURIComponent(results[2].replace(/\+/g, " "));
  }

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