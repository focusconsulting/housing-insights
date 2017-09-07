"use strict";

var router = {
    isFilterInitialized: false,
    stateObj: {},
    initFilters: function(msg,data){
        if ( router.isFilterInitialized ) return;
        setSubs([
            ['filterValues', router.pushFilter],
            ['mapLayer', router.pushFilter],
            ['overlaySet', router.pushFilter],
            ['subNav.right', router.pushFilter],
            ['previewBuilding', router.pushFilter],
            ['clearState', router.clearOverlayURL]
        ]);        
        router.isFilterInitialized = true;
        if ( router.hasInitialFilterState ) {
            router.decodeState();
        }
    },
    initBuilding: function() {
        router.initialView = 'building';
        router.buildingID = window.location.hash.match(/building=([\w\d-]+)/)[1];
    },
    clearOverlayURL: function(msg, data){
        if ( data === 'overlaySet' ){
            delete router.stateObj[data];
            router.setHash();
        }
    },
    pushFilter: function(msg, data){
        console.log(msg,data);
        if (data.length === 0 || !data) {
            delete router.stateObj[msg];
        } else if ( msg.split('.')[0] === 'previewBuilding' ) {
            router.stateObj['previewBuilding'] = data;
        } else {
            router.stateObj[msg] = data;
        }
        router.setHash()
    },
    setHash: function () {
        if ( Object.keys(router.stateObj).length === 0 || ( Object.keys(router.stateObj).length === 1 && router.stateObj.mapLayer === mapView.initialLayers[0].source ) ) {
            // clear location has if state obj is empty  OR if it's only property is mapLayer equal to initial mapLayer (ward for now)
            window.history.replaceState(router.stateObj, 'newState', '#');
        } else {
            window.history.replaceState(router.stateObj, 'newState', '#/HI/' + router.paramifyFilter());        
        }
    },
    pushViewChange: function(msg, data){
        if (data.el === 'project-view'){
            var buildingID = getState().selectedBuilding[0].properties.nlihc_id;
            window.history.pushState(router.stateObj, 'newState', '#/HI/building=' + buildingID);
        }
    },
    paramifyFilter: function(){
        var paramsArray = [];
        for (var key in router.stateObj) {
            if (!router.stateObj.hasOwnProperty(key)) continue;
            if ( key.split('.')[0] === 'filterValues') {
                var dataChoice = dataChoices.find(function(obj){
                    return key.split('.')[1] === obj.source;
                });
                
                if ( dataChoice.component_type === 'continuous' ) {
                    var separator = router.stateObj[key] && router.stateObj[key][2] ? '-' : '_';
                    paramsArray.push(dataChoice.short_name + '=' + router.stateObj[key][0] + separator + router.stateObj[key][1]);
                }
                if ( dataChoice.component_type === 'categorical' || dataChoice.component_type === 'location' || dataChoice.component_type === 'searchbar' ){
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
            } else if ( key.split('.')[0] === 'mapLayer') {
                if ( router.stateObj[key] !== mapView.initialLayers[0].source ) { // paramify only if mapLayer does not equal
                                                                                  // initial layer. now `ward` but could be 
                                                                                  // something else
                    paramsArray.unshift('ml=' + router.stateObj[key]); // ensure mapLayer is always first
                                                                       // some other component seems to already ensure
                                                                       // this, but no harm done to do again.
                }
            } else if ( key === 'overlaySet') {
                
                var dataChoice = dataChoices.find(function(obj){
                    return router.stateObj.overlaySet.overlay === obj.source;
                });
                paramsArray.push( 'ol=' + dataChoice.short_name);
            } else if ( key === 'subNav.right' && router.stateObj['subNav.right'] === 'buildings' ) {
                paramsArray.push('sb=bdng');
            } else if ( key.split('.')[0] === 'previewBuilding' ){
                paramsArray.push('pb=' + router.stateObj['previewBuilding'].properties.nlihc_id);
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
            var dataChoice;
            var eachArray = each.split('=');
            if ( eachArray[0] === 'ml' ) { // ie if it's a mapLayer encoding
                 setState('mapLayer',eachArray[1]);
            } else if ( eachArray[0] === 'ol' ) { // ie if it's a overLay encoding
                dataChoice = dataChoices.find(function(obj){
                    return obj.short_name === eachArray[1];
                });
                router.openFilterControl(dataChoice.source); // can be replicated for non-overLay filters if
                                                             // we decide to url encode them and want them (or the
                                                             // last) opened on load
            } else if ( eachArray[0] === 'sb' ){
                setState('subNav.right', 'buildings');
            
            } else if ( eachArray[0] === 'pb' ) {
                var matchingRenderedProject = mapView.map.queryRenderedFeatures({
                    layers: ['project','project-enter','project-exit', 'project-unmatched']
                })
                .find(function(each){
                    return each.properties.nlihc_id === eachArray[1];
                });
                setState('previewBuilding', matchingRenderedProject);
            
            } else {
                dataChoice = dataChoices.find(function(obj){
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
            if ( dataChoice.component_type === 'categorical' || dataChoice.component_type === 'location' || dataChoice.component_type === 'searchbar' ){
                    var values = eachArray[1].replace(/_/g,' ').split('+');
                    setTimeout(function(){
                        var dropdown_element = $('.ui.dropdown.'+'dropdown-' + dataChoice.source)
                            dropdown_element.dropdown('set selected', values);
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
            }
        });

        this.clearScreen();
    },
    openFilterControl: function(id){
        $('#filter-' + id).click(); // programmatically "click" open the accordion. with overLays, the clicking will
                                    // lead to the setState so no need to setState directly
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