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
        console.log(router.stateObj);
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
                console.log('date');
                var dateStrings = [];
                router.stateObj[key].forEach(function(dateObj,index){
                    var date = dateObj.getDate();
                    var month = dateObj.getMonth() + 1;
                    var year = dateObj.getFullYear();
                    dateStrings[index] = 'd' + date.toString() + 'm' + month.toString() + 'y' + year.toString(); 
                });
                paramsArray.push(dataChoice.short_name + '=' + dateStrings[0] + '-' + dateStrings[1]);
            }
        }
     //   console.log(paramsArray.join('&'));
        return paramsArray.join('&').replace(/ /g,'_');
    },
    screenLoad: function(){
        document.getElementById('loading-state-screen').style.display = 'block';
    },
    decodeState: function(){
        console.log('decodeState');
        var stateArray = window.location.hash.replace('#/HI/','').split('&');
        stateArray.forEach(function(each){
            var eachArray = each.split('=');
            console.log(eachArray);
            var dataChoice = dataChoices.find(function(obj){
                return obj.short_name === eachArray[0];
            });
            if ( dataChoice.component_type === 'continuous' ) {
                var values = eachArray[1].split('-');
                // set the values of the corresponding textInput
                filterView.textInputs[dataChoice.short_name].setValues([['min', +values[0]]],[['max', +values[1]]]);
                // call the corresponding textInput's callback
                filterView.textInputs[dataChoice.short_name].callback();
            }
            if ( dataChoice.component_type === 'categorical' ){
                console.log('decoding categorical');
                var values = eachArray[1].replace('_',' ').split('+');
                console.log(values);
                $('.ui.dropdown.'+'dropdown-' + dataChoice.source).dropdown('set selected', values);
            }   
            if ( dataChoice.component_type === 'date' ){
                // handle decoding for date type filter here
                var values = eachArray[1].split('-');
                filterView.dateInputs[dataChoice.short_name].setValues(
                    [
                        [ 'year',  values[0].match(/\d{4}/)[0] ],
                        [ 'month', values[0].match(/m(\d+)/)[1] ],
                        [ 'day',   values[0].match(/d(\d+)/)[1]]
                    ],
                    [
                        [ 'year',  values[1].match(/\d{4}/)[0] ],
                        [ 'month', values[1].match(/m(\d+)/)[1] ],
                        [ 'day',   values[1].match(/d(\d+)/)[1]]
                    ]
                );
                filterView.dateInputs[dataChoice.short_name].callback();
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