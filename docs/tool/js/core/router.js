"use strict";

var router = {
    isInitialized: false,
    stateObj: {},
    init: function(msg,data){
        if ( router.isInitialized ) return;
        setSubs([
            ['filterValues', router.pushFilter]
        ]);        
        router.isInitialized = true;
        if ( router.hasInitialState ) router.decodeState();
    },
    pushFilter: function(msg, data){
        // TO DO: add handling for sidebar and preview pusher
        router.stateObj[msg] = data;
        if (data.length === 0) {
            delete router.stateObj[msg];
        }
        window.history.replaceState(router.stateObj, 'newState', '#/HI/' + router.paramify());
    },
    pushSidebar: function(msg, data) {
        // handle above?
    },
    pushPreview: function(msg, data) {
        // handle above?
    },
    paramify: function(){
        var paramsArray = [];
        for (var key in router.stateObj) {
            if (!router.stateObj.hasOwnProperty(key)) continue;
            var dataChoice = dataChoices.find(function(obj){
                return key.replace('filterValues.','') === obj.source;
            });
            console.log(dataChoice);
            
            if ( dataChoice.component_type === 'continuous' ) {
                console.log('continuous'); 
                paramsArray.push(dataChoice.short_name + '=' + Math.round(router.stateObj[key][0]) + '-' + Math.round(router.stateObj[key][1])); 
            }
            if ( dataChoice.component_type === 'categorical' ){
                console.log('categorical');
                paramsArray.push( dataChoice.short_name + '=' + router.stateObj[key].join('+'));
            }
            if ( dataChoice.component_type === 'date' ){
                // handle encoding for date type filter here
            }
        }
     //   console.log(paramsArray.join('&'));
        return paramsArray.join('&').replace(/ /g,'_');
    },
    screenLoad: function(){
        document.getElementById('loading-state-screen').style.display = 'block';
    },
    decodeState: function(){
        var stateArray = window.location.hash.replace('#/HI/','').split('&');
        stateArray.forEach(function(each){
            var eachArray = each.split('=');
            console.log(eachArray);
            var dataChoice = dataChoices.find(function(obj){
                return obj.short_name === eachArray[0];
            });
            if ( dataChoice.component_type === 'continuous' ) {
                var values = eachArray[1].split('-');
                setState('filterValues.' + dataChoice.source , [+values[0], +values[1]]  );
            }
            if ( dataChoice.component_type === 'categorical' ){
                var values = eachArray[1].replace('_',' ').split('+');
                setState('filterValues.' + dataChoice.source , values );
            }   
            if ( dataChoice.component_type === 'date' ){
                // handle decoding for date type filter here
            }

        });

        document.getElementById('loading-state-screen').style.display = 'none';
    }

};

if ( window.location.hash.indexOf('#/HI/') !== -1 ) {
    router.hasInitialState = true;
    router.screenLoad();
} else {
    router.hasInitialState = false;
}