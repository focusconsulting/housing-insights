"use strict";

var router = {
    isInitialized: false,
    stateObj: {},
    init: function(msg,data){
        if ( router.isInitialized ) return;
        setSubs([
            ['filterValues', router.routeFilter]
        ]);
        router.isInitialized = true;
    },
    routeFilter: function(msg, data){
        // handle sidebar and preview routers here with if against the msg if necessary
        router.stateObj[msg] = data;
        if (data.length === 0) {
            delete router.stateObj[msg];
        }
        window.history.replaceState(router.stateObj, 'newState', '#/' + router.paramify());
    },
    routeSidebar: function(msg, data) {
        // handle above?
    },
    routePreview: function(msg, data) {
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
                // handle endoding for date type filter here
            }
        }
     //   console.log(paramsArray.join('&'));
        return paramsArray.join('&').replace(/ /g,'_');
    }

};