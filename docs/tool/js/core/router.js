"use strict";

var router = {
    isFilterInitialized: false,
    stateObj: {},
    initFilters: function(msg,data){
        if ( router.isFilterInitialized ) return;
        setSubs([
            ['filterValues', router.pushFilter]
        ]);        
        router.isFilterInitialized = true;
        if ( router.hasInitialFilterState ) router.decodeState();
    },
    initBuilding: function() {
        router.initialView = 'building';
        router.buildingID = window.location.hash.match(/building=([\w\d-]+)/)[1];
    },
    pushFilter: function(msg, data){
        console.log(msg,data);
        // TO DO: add handling for sidebar and preview pusher
        if (data.length === 0) {
            delete router.stateObj[msg];
        } else {
            router.stateObj[msg] = data;
            console.log(router.stateObj);
        }
        if ( Object.keys(router.stateObj).length === 0 ) {
            window.history.replaceState(router.stateObj, 'newState', '#');
        } else {
            window.history.replaceState(router.stateObj, 'newState', '#/HI/' + router.paramifyFilter());        
        }
    },
    pushViewChange: function(msg, data){
        if (data.el === 'building-view'){
            var buildingID = getState().selectedBuilding[0].properties.nlihc_id;
            window.history.pushState(router.stateObj, 'newState', '#/HI/building=' + buildingID);
        }
    },
    paramifyFilter: function(){
        var paramsArray = [];
        for (var key in router.stateObj) {
            if (!router.stateObj.hasOwnProperty(key)) continue;
            var dataChoice = dataChoices.find(function(obj){
                return key.split('.')[1] === obj.source;
            });
            
            if ( dataChoice.component_type === 'continuous' ) {
                var separator = router.stateObj[key] && router.stateObj[key][2] ? '-' : '_';
                paramsArray.push(dataChoice.short_name + '=' + Math.round(router.stateObj[key][0]) + separator + Math.round(router.stateObj[key][1])); 
            }
            if ( dataChoice.component_type === 'categorical' || dataChoice.component_type === 'location'  ){
                paramsArray.push( dataChoice.short_name + '=' + router.stateObj[key].join('+'));
            }
            if ( dataChoice.component_type === 'date' ){
                var separator = router.stateObj[key] && router.stateObj[key][2] ? '-' : '_';
                var dateStrings = [];
                for ( var i = 0; i < 2; i++ ){ // i < 2 bc index 2 is true/false of nullsShown
                    var date = router.stateObj[key][i].getDate();
                    var month = router.stateObj[key][i].getMonth() + 1;
                    var year = router.stateObj[key][i].getFullYear();
                    dateStrings[i] = 'd' + date.toString() + 'm' + month.toString() + 'y' + year.toString(); 
                }
                paramsArray.push(dataChoice.short_name + '=' + dateStrings[0] + separator + dateStrings[1]);
            }
        }
     //   console.log(paramsArray.join('&'));
        return paramsArray.join('&').replace(/ /g,'_');
    },
    screenLoad: function(){
        document.getElementById('loading-state-screen').style.display = 'block';
    },
    decodeState: function(){
        console.log("decoding state from URL");
        var stateArray = window.location.hash.replace('#/HI/','').split('&');
        stateArray.forEach(function(each){
            var eachArray = each.split('=');
            var dataChoice = dataChoices.find(function(obj){
                return obj.short_name === eachArray[0];
            });
            console.log('datachoice', dataChoice);
            var filterControlObj = filterView.filterControlsDict[dataChoice.short_name]
            console.log('filterControlObj', filterControlObj);
            if ( dataChoice.component_type === 'continuous' ) {
                var separator = eachArray[1].indexOf('-') !== -1 ? '-' : '_';
                var values = eachArray[1].split(separator);
                var min = +values[0]
                var max = +values[1]
                var nullsShown = separator === '_' ? false : true;
                
                filterControlObj.set(min,max,nullsShown);
                
            }
            if ( dataChoice.component_type === 'categorical' || dataChoice.component_type === 'location' ){
                console.log('categorical or location');
                var values = eachArray[1].replace(/_/g,' ').split('+');
                console.log(values);
                if ( dataChoice.component_type === 'location' ) {
                    /* below is very hard-coded to match the options of the location drodown with the association mapLayer */
                    var expectedLayer = values[0].indexOf('Ward') !== -1 ? 'ward' : values[0].indexOf('Cluster') !== -1 ? 'neighborhood_cluster' : 'census_tract';
                    if ( expectedLayer !== getState().mapLayer ) {
                        setState('mapLayer',expectedLayer);
                    }
                }
                setTimeout(function(){
                    $('.ui.dropdown.'+'dropdown-' + dataChoice.source).dropdown('set selected', values);
                }); // decoding location won't without the setTimeout trick, which asyncs the function, to be fired
                    // in the next open slot in the queue. especially true if the mapLaye needs to be changed first, because then
                    // probably a lot of async stuff is triggered but the setState call above. 
            }   
            if ( dataChoice.component_type === 'date' ){
                // handle decoding for date type filter here
                var separator = eachArray[1].indexOf('-') !== -1 ? '-' : '_';
                var nullsShown = separator === '_' ? false : true;
                var values = eachArray[1].split(separator);

                //Set the values on the input boxes
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
                document.querySelector('[name="showNulls-' + dataChoice.source + '"]').checked = nullsShown;
                
                //Commit the values using callback(), which will update slider to match. 
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
        controller.goBack();
    },

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