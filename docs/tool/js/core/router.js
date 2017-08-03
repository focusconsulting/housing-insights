"use strict";

var router = {
    isFilterInitialized: false,
    stateObj: {},
    initFilters: function(msg,data){
        if ( router.isFilterInitialized ) return;
        setSubs([
            ['filterValues', router.pushFilter]
    //        ['nullsShown', router.nullsHandler] // triggered when the nullsShown check is toggled. not when a filter range is adjusted
        ]);        
        router.isFilterInitialized = true;
        if ( router.hasInitialFilterState ) router.decodeState();
    },
    initBuilding: function() {
        console.log('building in hash');
        router.initialView = 'building';
        router.buildingID = window.location.hash.match(/building=([\w\d-]+)/)[1];
        console.log(router.buildingID);
    },
    pushFilter: function(msg, data){
        // TO DO: add handling for sidebar and preview pusher
        console.log(data);
        router.stateObj[msg] = data;
        if (data.length === 0) {
            delete router.stateObj[msg];
            window.history.replaceState(router.stateObj, 'newState', '#');
        } else {
            window.history.replaceState(router.stateObj, 'newState', '#/HI/' + router.paramifyFilter());        
        }
        console.log(router.stateObj);
    },
    pushViewChange: function(msg, data){
        if (data.el === 'building-view'){
            console.log('push view change');
            var buildingID = getState().selectedBuilding[0].properties.nlihc_id;
            window.history.pushState(router.stateObj, 'newState', '#/HI/building=' + buildingID);
        }
    },
    paramifyFilter: function(){
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
                for ( var i = 0; i < 2; i++ ){ // i < 2 bc index 2 is true/false of nullsShown
                    var date = router.stateObj[key][i].getDate();
                    var month = router.stateObj[key][i].getMonth() + 1;
                    var year = router.stateObj[key][i].getFullYear();
                    dateStrings[i] = 'd' + date.toString() + 'm' + month.toString() + 'y' + year.toString(); 
                }
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
                filterView.filterInputs[dataChoice.short_name].setValues([['min', +values[0]]],[['max', +values[1]]]);
                // call the corresponding textInput's callback
                filterView.filterInputs[dataChoice.short_name].callback();
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
                filterView.filterInputs[dataChoice.short_name].setValues(
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
                filterView.filterInputs[dataChoice.short_name].callback();
            }

        });

        this.clearScreen();
    },
    clearScreen: function(){
        document.getElementById('loading-state-screen').style.display = 'none';
    },
    inAppBack: function(){
        if ( getState().activeView.length > 1 ) {
            window.history.back(); // if there's a previously active view, use history.back() function. router will pick up
                                   // on the hash change
        } else { // if not, need custom handling; otherwise the in-app back button will navigate to whatever the previous page
                 // is, outside of the domain. ok for browser's back button to do that, but not the in-app back
            location.hash = ' ';
            location.reload();
        }
    },
    hashChangeHandler: function(){
        console.log('hash change');
        controller.goBack();
    },
    nullsHandler: function (msg,data) { // for handling when a nullsShown checkbox is toggled. needs to grab values of the filter
        console.log(msg, data);
        var component = msg.split('.')[1];
        var dataChoice = dataChoices.find(function(each){
            return each.source === component;
        });
        var type = dataChoice.component_type;
        var shortName = dataChoice.short_name;
        console.log(type,shortName);
        if ( type === 'categorical' ) {
            // i think this is a null set; no unknowns in categorical filters
        }
        if ( type === 'continuous' ) {

        }
        if ( type === 'date' ) {

        }
        if ( type === 'location' ) {
            // to come
        }
    }

};
window.onhashchange = function() {
 router.hashChangeHandler();
}
if ( window.location.hash.indexOf('#/HI/') !== -1 ) {
    if ( window.location.hash.indexOf('building=') !== -1 ){
        router.initBuilding();
    } else {
        router.hasInitialFilterState = true;
    }
    router.screenLoad();
} else {
    router.hasInitialFilterState = false;
}