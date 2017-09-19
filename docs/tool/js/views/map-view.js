---
frontmatter: isneeded
---
    //A comment here helps Jekyll not get confused

    "use strict";

    var mapView = {
        el: 'map-view',

        init: function() { // as single page app, view init() functions should include only what should happen the first time
            // the view is loaded. things that need to happen every time the view is made active should be in
            // the onReturn methods. nothing needs to be there so far for mapView, but projectView for instance
            // should load the specific building info every time it's made active.
            var partialRequest = {
                partial: this.el,
                container: null, // will default to '#body-wrapper'
                transition: false,
                callback: appendCallback
            };
            controller.appendPartial(partialRequest, this);

            function appendCallback() {
                //this is used to indicate the completion of loading
                setState('filterViewLoaded',false);

                setSubs([
                    ['mapLayer', mapView.showLayer],
                    ['mapLayer', mapView.layerOverlayToggle],
                    ['mapLoaded', model.loadMetaData],
                    ['mapLoaded', mapView.navControl.init],
                    ['sidebar.right', mapView.navControl.move],
                    ['dataLoaded.metaData', mapView.addInitialLayers], //adds zone borders to geojson
                    ['dataLoaded.metaData', resultsView.init],
                    ['dataLoaded.metaData', mapView.placeProjects],
                    ['dataLoaded.metaData', mapView.buildOverlayOptions],
                    ['dataLoaded.raw_project', filterView.init],
                    ['overlayRequest', mapView.addOverlayData],
                    ['overlayRequest', mapView.updateZoneChoiceDisabling],
                    ['joinedToGeo', mapView.addOverlayLayer],
                    ['overlaySet', chloroplethLegend.init],
                    ['hoverBuilding', mapView.showPopup],
                    ['previewBuilding', mapView.showProjectPreview],
                    ['previewBuilding', mapView.highlightPreviewBuilding],
                    ['filteredData', mapView.filterMap],
                    ['filteredViewLoaded',mapView.addExportButton],
                    ['filteredViewLoaded',mapView.exportButton],
                    ['hoverBuildingList', mapView.highlightHoveredBuilding],
                    ['filterViewLoaded', mapView.initialSidebarState],
                    ['filteredProjectsAvailable',mapView.zoomToFilteredProjects],
                    ['initialProjectsRendered',router.initGate],
                    ['filterViewLoaded', router.initGate]
                                                              
                ]);


                //Add the welcome screen
                //Display the proper buttons based on whether we are loading a state or not
                if (router.hasInitialFilterState){
                    //loading saved analysis
                    $('#viewSavedAnalysis').removeClass('hidden');
                    $('#savedStateAlert').removeClass('hidden');
                } else {
                    //when loading fresh
                    $('#openExample1').removeClass('hidden');
                    $('#useTool').removeClass('hidden');
                };

                //Set up buttons to be enabled when page is done loading
                var removeSpinners = function() {
                        $('#openExample1').removeClass('disabled');
                        $('#openExample1 i').removeClass('spinner loading').addClass('check');

                        $('#startTour').removeClass('disabled');
                        $('#startTour i').removeClass('spinner loading').addClass('check');

                        $('#useTool').removeClass('disabled');
                        $('#useTool i').removeClass('spinner loading').addClass('check');

                        $('#viewSavedAnalysis').removeClass('disabled');
                        $('#viewSavedAnalysis i').removeClass('spinner loading').addClass('check');
                    }
                setSubs([['filterViewLoaded',removeSpinners]])

                //Show modal
                $('#welcomeModal').modal({
                    approve: '.positive, .approve, .ok',
                    deny     : '.negative, .deny, .cancel',
                    onApprove: function(d) {

                        //Figure out which button was pressed                      
                        if (d.attr('id') == 'startTour') {
                            console.log("start the tour");

                            mapView.tour = new Shepherd.Tour({
                              defaults: {
                                classes: 'shepherd-theme-arrows',
                                scrollTo: true
                              }
                            });

                          
                            mapView.tour.addStep('layer-choice', {
                                text: "The zone type selected affects the 'Specific Zone' filter as well as all the zone-level datasets shown in blue",
                                attachTo: '#layer-menu right',
                                classes: 'shepherd-skinny shepherd-theme-arrows',
                                when: {
                                    show: function() {
                                        console.log('we can trigger events here if needed');
                                    }
                                },
                                buttons: [
                                    {
                                      text: 'Exit',
                                      classes: 'shepherd-button-secondary',
                                      action: mapView.tour.cancel
                                    }, {
                                      text: 'Next',
                                      action: mapView.tour.next,
                                      classes: 'shepherd-button-example-primary'
                                    }
                                ]
                            });
                            mapView.tour.addStep('project-data', {
                                text: "Change the inputs here to filter projects that meet certain criteria.",
                                attachTo: '#filter-content-proj_units_tot right',
                                classes: 'shepherd-skinny shepherd-theme-arrows',
                                when: {
                                    'before-show': function() {
                                        $('#filter-proj_units_tot').click();
                                    }
                                },
                                buttons: [
                                    {
                                      text: 'Exit',
                                      classes: 'shepherd-button-secondary',
                                      action: mapView.tour.cancel
                                    }, {
                                      text: 'Next',
                                      action: mapView.tour.next,
                                      classes: 'shepherd-button-example-primary'
                                    }
                                ]
                            });

                            mapView.tour.addStep('zone-data', {
                                text: "Data choices marked with a blue icon are zone-level data sets. \
                                       They refer to data about the area the project is in, not the project itself.<br><br>\
                                       Adjusting this filter would show projects in a Ward with a poverty rate between the selected values.<br><br>\
                                       Remember you can change the zone type, but this will remove any existing selections you've made.",
                                attachTo: '#filter-content-poverty_rate right',
                                classes: 'shepherd-skinny shepherd-theme-arrows',
                                when: {
                                    'before-show': function() {
                                        $('#filter-poverty_rate').click();
                                    }
                                },
                                buttons: [
                                    {
                                      text: 'Exit',
                                      classes: 'shepherd-button-secondary',
                                      action: mapView.tour.cancel
                                    }, {
                                      text: 'Next',
                                      action: mapView.tour.next,
                                      classes: 'shepherd-button-example-primary'
                                    }
                                ]
                            });

                              mapView.tour.addStep('search', {
                                title: 'Search for a project',
                                text: 'You can search by project name or address',
                                attachTo: '.dropdown-proj_name_addre bottom',
                                classes: 'shepherd-skinny shepherd-theme-arrows', //needed to use the right style sheet
                                showCancelLink: true,
                                buttons: [
                                   {
                                      text: 'Exit',
                                      classes: 'shepherd-button-secondary',
                                      action: mapView.tour.cancel
                                    }, {
                                      text: 'Next',
                                      action: mapView.tour.next,
                                      classes: 'shepherd-button-example-primary'
                                    }
                                ]
                            });

                            mapView.tour.addStep('export-data', {
                                title: 'Export data',
                                text: 'You can export a CSV file of all the project data here.',
                                attachTo: '#sidebar-right left',
                                classes: 'shepherd-skinny shepherd-theme-arrows', //needed to use the right style sheet
                                showCancelLink: true,
                                 when: {
                                    'before-show': function() {
                                        setState('subNav.right','buildings')
                                    }
                                },
                                buttons: [
                                   {
                                      text: 'Done',
                                      classes: 'shepherd-button-secondary',
                                      action: mapView.tour.cancel
                                    }
                                ]
                            });

                            mapView.tour.start();

                        } else if (d.attr('id') == 'openExample1') {
                            console.log("open example analysis");
                            mapView.showExample1();
                        } else if (d.attr('id') == 'useTool') {
                            //do nothing - all that's needed is to close the screen
                        };
                    },
                    onHide: function(){
                        
                        //If filterView hasn't loaded yet, show the page loading dimmer
                        if (!getState().filterViewLoaded[0]) {

                            //Set dimmer to clear next time the filterViewLoaded event occurs
                            setSubs([
                                ['filterViewLoaded',mapView.clearLoadingDimmer]
                            ]);

                            //Add the loading dimmer underneath. Timeout needed so that it occurs after the current modal hide finishes
                            setTimeout(function(){
                                $('#loading-tool-dimmer').dimmer('show'); //.page.dimmer:first
                            },0);

                        } else {
                            console.log("don't need to show loader")
                        }
                    }
                  }).modal('show');

                

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
                this.map.addControl(new mapboxgl.NavigationControl(), 'top-right');

                this.map.on('load', function() {
                    setState('mapLoaded', true);
                });
                
                // filter decoding was happening too quickly after initialLayers were added (ln 463),
                // before they were fully rendered. even mapBox's 'render' was sometime too early. ussing instead
                // getLayer('projects') to make sure the layers are indeed present. 'render' is fired often; function below
                // checks it against state of the project layer and 
                // !isFilterInitialized to setState initialProjectsRendered. router.initFilters
                // subscribes to that stateChange and turns isFilterInitialized to true so that this stateChange
                // fires only once. 

                var theMap = this.map;
                this.map.on('render', function() {
                  if ( theMap.loaded() && theMap.getLayer('project-enter') !== undefined && !router.isFilterInitialized ) {
                      setState('initialProjectsRendered', true);
                  }
                });

                this.map.on('zoomend', function() {

                    d3.select('#reset-zoom')
                        .style('display', function() {
                            if (Math.abs(mapView.map.getZoom() - mapView.originalZoom) < 0.1 &&
                                Math.abs(mapView.map.getCenter().lng - mapView.originalCenter[0]) < 0.01 &&
                                Math.abs(mapView.map.getCenter().lat - mapView.originalCenter[1]) < 0.01) {
                                return 'none';
                            } else {
                                return 'block';
                            }
                        })
                        .on('click', function() {

                            mapView.map.flyTo({
                                center: mapView.originalCenter,
                                zoom: mapView.originalZoom
                            });

                        });

                });

            }

        },
        clearLoadingDimmer: function(msg, data){
            $('#loading-tool-dimmer').dimmer('hide');
        },
        navControl: {
            el: null,
            init: function(){
                mapView.navControl.el = document.getElementsByClassName('mapboxgl-ctrl-top-right')[0];
                mapView.navControl.el.parentElement.removeChild(mapView.navControl.el);
                document.getElementById(mapView.el).appendChild(mapView.navControl.el);
            },
            move: function(){
                mapView.navControl.el.classList.toggle('movedIn');
            }
        },
        showExample1: function(){
            //Quick example to demonstrate functionality
            //TODO this does not properly set the ui components - probably need to go through the router.js instead
            var urlParams = 'reacn=20_73'
            window.history.replaceState({stateinfo:"elsewhere this is the state object, but we don't have a way to access the correct state object"}, 'newState', '#/HI/' + urlParams);
            router.decodeState()
        },
        initialSidebarState: function(){
            setState('sidebar.left',true);
            setState('sidebar.right',true);
            setState('subNav.left', 'filters');
            setState('subNav.right', 'charts');
        },
        ChloroplethColorRange: function(source_data_name, chloroData, style){
            // CHLOROPLETH_STOP_COUNT cannot be 1! There's no reason you'd
            // make a chloropleth map with a single color, but if you try to,
            // you'll end up dividing by 0 in 'this.stops'. Keep this in mind
            // if we ever want to make CHLOROPLETH_STOP_COUNT user-defined.

            //Utility function for formatting stops cleanly
            var roundedVersionOf = function(val){
                switch(style){
                    case "percent":
                        return Math.roundTo(val, .01);
                    case "money":
                        return Math.roundTo(val, 100);
                    case "number":
                        return Math.roundTo(val, 100);
                    default:
                        return Math.round(val);
                }
            }

            //We only want the scale set based on zones actually displayed - the 'unknown' category returned by the api can
            //especially screw up the scale when using rates as they come back as a count instead of a rate
            var currentLayer = getState().mapLayer[0]
            var activeZones = []
            model.dataCollection[currentLayer].features.forEach(function(feature){
                var zone = feature.properties.NAME;
                activeZones.push(zone)
            });

            //Determine values based on the data span
            var MAX_DOMAIN_VALUE = d3.max(chloroData, function(d){
                if (activeZones.includes(d.zone)) {
                    return d[source_data_name];
                } else {
                    return 0;
                };
            });
            var MIN_DOMAIN_VALUE = d3.min(chloroData, function(d){
                return d[source_data_name];
            });
            var PIVOT_VALUE = ((MAX_DOMAIN_VALUE - MIN_DOMAIN_VALUE) / 3 ) + MIN_DOMAIN_VALUE

            //Choose the colors
            //TODO - loosely based on the PuBu 7-class scheme from colorbrewer2, but interpolation by d3 isn't the same. Could assign manually.
            var CHLOROPLETH_STOP_COUNT = 6;
            var MIN_COLOR = 'rgba(241,238,246,0.7)'//
            var PIVOT_COLOR = 'rgba(116,189,219,0.7)'
            var MAX_COLOR = 'rgba(3,78,123,0.7)'//

            //Assign values to colors
            var colorScale = d3.scaleLinear()
                .domain([MIN_DOMAIN_VALUE, PIVOT_VALUE, MAX_DOMAIN_VALUE])
                .range([MIN_COLOR, PIVOT_COLOR, MAX_COLOR]);

            //Create the range in the format expected
            this.stops = new Array(CHLOROPLETH_STOP_COUNT).fill(" ").map(function(el, i){
                var stopIncrement = MAX_DOMAIN_VALUE/(CHLOROPLETH_STOP_COUNT - 1);
                var domainValue = MAX_DOMAIN_VALUE - (stopIncrement * i);
                    domainValue = roundedVersionOf(domainValue);
                var rangeValue = colorScale(domainValue);
                return [domainValue, rangeValue];
            });

            this.stopsAscending = this.stops.sort(function(a,b){
                return a[0] - b[0];
            });
        },
        initialOverlays: [],

        findOverlayConfig: function(key, value) {
            return mapView.initialOverlays.filter(function(v) {
                return v[key] === value;
            })[0];
        },
        buildOverlayOptions: function() {
            console.log("TODO this needs attention")
            var test = dataChoices.filter(function(d){
                return d['data_level'] === "zone";
            })

            //TODO we want to move this config data into it's own file or to the api
            mapView.initialOverlays = test//TODO load this from dataChoices
        },



        //No longer used - we are moving this into the combined filter/layer setup.
        //Keep this code here until we confirm the removal of separate layers menu with user tests around 7/25
        //TODO remove once confirmed
        /*
        overlayMenu: function(msg, data) {

            if (data === true) {
                mapView.buildOverlayOptions();
                mapView.initialOverlays.forEach(function(overlay) {
                    new mapView.overlayMenuOption(overlay);
                });
            } else {
                console.log("ERROR data loaded === false")
            }
        },
        overlayMenuOption: function(overlay) {


            var parent = d3.select('#overlay-menu')
                .classed("ui styled fluid accordion", true) //semantic UI styling

            var title = parent.append("div")
                .classed("title overlay-title", true);
            title.append("i")
                .classed("dropdown icon", true);
            title.append("span")
                .classed("title-text", true)
                .text(overlay.display_name)
            title.attr("id", "overlay-" + overlay.source); //TODO need to change this to different variable after changing meta logic structure


            var content = parent.append("div")
                .classed("content", true)
              .attr("id", "overlay-about-"+overlay.source)
                .text(overlay.display_text)

            var legendLocation = content.append("div")
                .attr("id", "overlay-" + overlay.source + "-legend") // TODO need to change this to different variable after changing meta logic structure
                .style("height", "150px");

            $('.ui.accordion').accordion({'exclusive':true}); //only one open at a time

            //Set it up to trigger the layer when title is clicked
            document.getElementById("overlay-" + overlay.source).addEventListener("click", clickCallback);

            function clickCallback() {
                var existingOverlayType = getState().overlaySet !== undefined ? getState().overlaySet[0].overlay : null;
                console.log("changing from " + existingOverlayType + " to " + overlay.source);

                if (existingOverlayType !== overlay.source) {
                    setState('overlayRequest', {
                        overlay: overlay.source,
                        activeLayer: getState().mapLayer[0]
                    });
                } else {
                    mapView.clearOverlay();
                };

                //probably not currently working - disabling of layers
                mapView.layerMenuOptions.forEach(function(opt) {
                    if (thisOption.availableLayerNames.indexOf(opt.source) === -1) {
                        opt.makeUnavailable();
                    } else {
                        opt.makeAvailable();
                    }
                });

            }; //end clickCallback
        },

        */


        onReturn: function() {
            console.log('nothing to do');
        },



        clearOverlay: function(layer) {

            var i = layer === 'previous' ? 1 : 0;

            var layerObj = getState().overlaySet !== undefined ? getState().overlaySet[i] : undefined;

            if (layerObj !== undefined) {
                mapView.map.setLayoutProperty(layerObj.activeLayer + '_' + layerObj.overlay, 'visibility', 'none');
                mapView.toggleActive('#' + layerObj.overlay + '-overlay-item');

            }
            if (i === 0) { // i.e. clearing the existing current overlay, with result that none will be visible
                clearState('overlaySet');
                chloroplethLegend.tearDownPrevious();
                mapView.updateZoneChoiceDisabling("msg",{overlay: null});
            }
        },


        layerOverlayToggle: function(msg, data) {
        //Used when the user clicks the zone name to decide if we need to swap the overlay
        //'data' is the name of the zone type (layer) that was clicked

            var overlayState = getState()['overlaySet']
            var previousOverlayState = getState().overlaySet
            var existingOverlayType = getState().overlaySet !== undefined ? getState().overlaySet[0].overlay : null;
            if (previousOverlayState !== undefined) {
                var previousLayer = previousOverlayState[0].activeLayer
                mapView.clearOverlay();
                setState('overlayRequest',{
                                overlay: existingOverlayType,
                                activeLayer: data
                });
            };

            //to use w/ addOverlayData{ overlay: 'building_permits', activeLayer: 'ward'}
        },

        addOverlayData: function(msg, data) { // data e.g. { overlay: 'building_permits', activeLayer: 'ward'}]
            if (data == null) { // ie if the overlays have been cleared
                return;
            }

            var grouping = data.activeLayer

            //If we haven't loaded the data yet, need to get it
            if (getState()['joinedToGeo.' + data.overlay + '_' + data.activeLayer] === undefined) {

                //When data is loaded, display the layer if possible or switch to the default zone type instead.
                function dataCallback(d) {
                    var loadSuccessful = getState()['dataLoaded.' + data.overlay + '_' + data.activeLayer][0]
                    if (loadSuccessful === false) {
                        console.log("Grouping not available, switching to default")
                        //If the data returned is null that aggregation is not available. Use default aggregation instead
                        //Using setState here means that after the data is loaded, the addOverlayData function will be called
                        //again.
                        var config = mapView.findOverlayConfig('source', data.overlay)
                        var default_layer = config.default_layer

                        //Prevent an infinite loop in case default layer isn't available
                        if (data.activeLayer == default_layer){
                            console.log("ERROR: request for data layer returned null")
                        } else {
                            setState('overlayRequest', {
                                overlay: data.overlay,
                                activeLayer: default_layer
                            });
                        };
                    } else {
                        controller.joinToGeoJSON(data.overlay, grouping); // joins the overlay data to the geoJSON *in the dataCollection* not in the mapBox instance
                    };
                }

                //var overlayConfig = mapView.findOverlayConfig('source', data.overlay)
                //var url = overlayConfig.url_format.replace('<zone>',data.activeLayer)
                var url = model.URLS.layerData;
                url = url.replace('<grouping>', data.activeLayer)
                url = url.replace('<source_data_name>', data.overlay)

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

        addOverlayLayer: function(msg, data) { // e.g. data = {overlay:'crime',grouping:'neighborhood_cluster',activeLayer:'neighborhood_cluster'}
            //Called after the data join from addOverlayData's callback
            var source_data_name = data.overlay;

            if (mapView.map.getLayer(data.activeLayer + '_' + source_data_name) === undefined) {


                mapView.map.getSource(data.activeLayer + 'Layer').setData(model.dataCollection[data.activeLayer]); // necessary to update the map layer's data
                // it is not dynamically connected to the dataCollection
                var dataToUse = model.dataCollection[data.overlay + '_' + data.grouping].objects;
                                                                                 // dataCollection
                var thisStyle = mapView.initialOverlays.find(function(obj){return obj['source']==data.overlay}).style;

                // assign the chloropleth color range to the data so we can use it for other
                // purposes when the state is changed
                data.chloroplethRange = new mapView.ChloroplethColorRange(source_data_name, dataToUse, thisStyle);

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
                                'stops': data.chloroplethRange.stopsAscending,
                                'default': 'rgba(128,128,128,0.6)'
                            },
                            'fill-opacity': 1 //using rgba in the chloropleth color range instead
                        }
                    }, 'project');

                };
            mapView.showOverlayLayer(data.overlay, data.activeLayer);

        },

        showOverlayLayer: function(overlay_name, activeLayer) {

            setState('mapLayer', activeLayer); //todo is this needed?

            //Toggle the overlay colors themselves
            mapView.map.setLayoutProperty(activeLayer + '_' + overlay_name, 'visibility', 'visible');
            mapView.toggleActive('#' + overlay_name + '-overlay-item')
            setState('overlaySet', {
                overlay: overlay_name,
                activeLayer: activeLayer
            });

            mapView.clearOverlay('previous');

        },
        toggleActive: function(selector) {
            //TODO I think this is not actually selecting anything?
            console.log("toggling active")
            console.log(selector);
            d3.select(selector)
                .classed('active', function() {
                    if (d3.select(this).attr('class') === 'active') {
                        return false;
                    }
                    return true;
                });
        },
        initialLayers: [
            {
                source: 'ward',
                display_name: 'Ward',
                display_text: 'The largest geograpical division of the city, each with approximately equal population.',
                color: "#0D5C7D",
                visibility: 'visible'
            },
            {
                source: 'neighborhood_cluster',
                display_name: 'Neighborhood Cluster',
                display_text: '39 clusters each combining a set of smaller neighborhoods.',
                color: '#0D5C7D',
                visibility: 'none',
            },
            {
                source: 'census_tract',
                display_name: 'Census Tract',
                display_text: 'A small division used in collection of the US Census.',
                color: '#0D5C7D',
                visibility: 'none'
            }

            //TODO add ANC? Need weighting factors in database first

        ],
        addInitialLayers: function(msg, data) {

            //This function adds the zone layers, i.e. ward, zip, etc.
            if (data === true) {

                //Set up the initial holder of layer buttons
                d3.select("#layer-menu")
                    .append('div')
                        .classed("ui three large buttons",true) //TODO does "three" need to be based on count of layers if we add/remove some?
                        .attr("id","layer-menu-buttons")

                for (var i = 0; i < mapView.initialLayers.length; i++) {
                    console.log("Adding " + mapView.initialLayers[i].source);
                    mapView.addZoneLayerToMap(mapView.initialLayers[i])
                    mapView.addButtonToZoneMenu(mapView.initialLayers[i]);
                }

            } else {
                console.log("ERROR data loaded === false")
            };
        },
        addZoneLayerToMap: function(layer) {
            //Adds an individual zone (ward, zip, etc.) to the geoJSON

            var layerName = layer.source + 'Layer'; // e.g. 'wardLayer'
            var dataRequest = {
                name: layer.source, // e.g. ward
                url: model.URLS.geoJSONPolygonsBase + layer.source + '.geojson',
                callback: addLayerCallback
            };
            controller.getData(dataRequest);

            //TODO we can't control the order of zone type choices because this occurs via callback!
            function addLayerCallback(data) {
                if (mapView.map.getSource(layerName) === undefined) {
                    mapView.map.addSource(layerName, {
                        type: 'geojson',
                        data: data
                    });
                }
                if (layer.visibility === 'visible') {
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

            }
        },

        addButtonToZoneMenu: function(layer) {
            //Appends a new button to the list of zone choices

            console.log("Adding layerMenuOption for " + layer.source);
            d3.select('#layer-menu-buttons')

                .append('button')
                .classed("ui toggle button", true)
                .attr('id', function() {
                    return layer.source + '-menu-item';
                })
                .attr('title', function(){
                    return layer.display_text;
                })
                .classed('active', (layer.visibility === 'visible'))
                .text(function() {
                    return layer.display_name;
                })
                .on('click', function() {
                    setState('mapLayer', layer.source);
                });
        },


        layerMenuOptions: [],


        showLayer: function(msg, data) {
            //'data' is the name of the zone type (layer) that was clicked

            //first clear all existing layers
            var layerChoices = mapView.initialLayers.map(function(i) {
                return i['source']
            })
            for (var i = 0; i < layerChoices.length; i++) {
                mapView.map.setLayoutProperty(layerChoices[i] + 'Layer', 'visibility', 'none');
            }


            //Toggle boundaries ('layer')
            mapView.map.setLayoutProperty(data + 'Layer', 'visibility', 'visible');

            //Make sure the menu reflects the current choice
            d3.selectAll('#layer-menu-buttons button')
                .classed('active',false)
            d3.select('#' + data + '-menu-item')
                .classed('active',true);
        },
        updateZoneChoiceDisabling: function(msg,data) { // e.g. data = {overlay:'crime',grouping:'neighborhood_cluster',activeLayer:'neighborhood_cluster'}
            //Checks to see if the current overlay is different from previous overlay
            //If so, use the 'zones' to enable/disable zone selection buttons

            var layerMenu = d3.select('#layer-menu-buttons')
            layerMenu.selectAll('button')
                .each(function(d) {

                    var zoneButton = d3.select(this)
                    var buttonId = zoneButton.attr('id')
                    var layerType = buttonId.replace("-menu-item","")

                    //Get layers from the overlay config, or if no overlay selected use all available layers
                    var availableLayers = []
                    if (data.overlay == null){
                        mapView.initialLayers.forEach(function(layer) {
                            availableLayers.push(layer.source);
                        });
                    } else {
                        availableLayers = mapView.findOverlayConfig('source', data.overlay)['zones']
                    };


                  //True if in the list, false if not
                  var status = true
                  if (availableLayers.indexOf(layerType) != -1) {
                    status = false
                  }
                  zoneButton.classed('disabled',status)
                });
        },

        placeProjects: function(msg, data) { // some repetition here with the addLayer function used for zone layers. could be DRYer if combined
            // or if used constructor with prototypical inheritance
            if (data === true) {
                //msg and data are from the pubsub module that this init is subscribed to.
                //when called from dataLoaded.metaData, 'data' is boolean of whether data load was successful
                var dataURL = model.URLS.project
                var dataRequest = {
                    name: 'raw_project',
                    url: dataURL,
                    callback: dataCallback
                };
                controller.getData(dataRequest);

                function dataCallback() {
                    mapView.convertedProjects = controller.convertToGeoJSON(model.dataCollection.raw_project);
                    mapView.convertedProjects.features.forEach(function(feature) {
                        feature.properties.matches_filters = true;
                        feature.properties.klass = 'stay';  // 'stay'|'enter'|'exit'|'none'
                     });
                    mapView.listBuildings();
                    mapView.addExportButton();
                    mapView.exportButton();
                    mapView.map.addSource('project', {
                        'type': 'geojson',
                        'data': mapView.convertedProjects
                    });
                    mapView.circleStrokeWidth = 1;
                    mapView.circleStrokeOpacity = 1;
                    mapView.map.addLayer({
                        'id': 'project-unmatched',
                        'type': 'circle',
                        'source': 'project',
                        'filter': ['==', 'klass', 'none'],
                        'paint': {
                            'circle-radius': {
                                'base': 1.75,
                                'stops': [
                                    [11, 4],
                                    [12, 5],
                                    [15, 16]
                                ]
                            },

                            'circle-stroke-opacity': 0.5,
                            'circle-opacity': 0.5,
                            'circle-stroke-width': 0,
                            'circle-color': '#aaaaaa',
                            'circle-stroke-color': '#aaaaaa'

                        }
                    });
                    mapView.map.addLayer({
                        'id': 'project-exit', // add layer for exiting projects. empty at first. very repetitive of project layer, which could be improved
                        'type': 'circle',
                        'source': 'project',
                        'filter': ['==', 'klass', 'exit'],
                        'paint': {
                            'circle-radius': {
                                'base': 1.75,
                                'stops': [
                                    [11, 4],
                                    [12, 5],
                                    [15, 16]
                                ]
                            },
                            'circle-opacity': 0.5,
                            'circle-color': '#aaaaaa',

                            'circle-stroke-opacity': 0.5,
                            'circle-stroke-width': 0,
                            'circle-stroke-color': '#626262'
                        }
                    });
                    mapView.map.addLayer({
                        'id': 'project',
                        'type': 'circle',
                        'source': 'project',
                        'filter': ['==', 'klass', 'stay'],
                        'paint': {
                            'circle-radius': {
                                'base': 1.75,
                                'stops': [
                                    [11, 4],
                                    [12, 5],
                                    [15, 16]
                                ]
                            },
                            'circle-opacity': 0.5,
                            'circle-color': '#fd8d3c',

                            'circle-stroke-width': 0,
                            'circle-stroke-opacity': 0.5,
                            'circle-stroke-color': '#fd8d3c'    //same as circle for existing
                        }
                    });
                    mapView.map.addLayer({
                        'id': 'project-enter', // add layer for entering projects. empty at first. very repetitive of project layer, which could be improved
                        'type': 'circle',
                        'source': 'project',
                        'filter': ['==', 'klass', 'enter'],
                        'paint': {
                            'circle-radius': {
                                'base': 1.75,
                                'stops': [
                                    [11, 4],
                                    [12, 5],
                                    [15, 16]
                                ]
                            },

                            'circle-opacity': 0.5,
                            'circle-color': '#fd8d3c',

                            'circle-stroke-width': 0, //Warning, this is not actually set here - the animateEnterExit overrides it
                            'circle-stroke-opacity': 0.5,
                            'circle-stroke-color': '#fc4203'//'#ea6402'    //darker for entering
                        }
                    });

                    setState('initialLayersAdded', true);

                   //TODO - with the upgraded mapboxGL, this could be done with a 'mouseenter' and 'mouseexit' event
                    mapView.map.on('mousemove', function(e) {
                        //get the province feature underneath the mouse
                        var features = mapView.map.queryRenderedFeatures(e.point, {
                            layers: ['project','project-enter','project-exit', 'project-unmatched']
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



                    mapView.map.on('click', function(e) {
                        var building = (mapView.map.queryRenderedFeatures(e.point, {
                            layers: ['project','project-enter','project-exit', 'project-unmatched']
                        }))[0];

                        //If you click but not on a building, remove any tooltips
                        if (building === undefined) {
                            mapView.removeAllPopups();
                        } else {
                        //If you click on a building, show that building in the side panel
                            setState('subNav.right', 'buildings');
                            setState('previewBuilding', [building, true]); // true ie flag to scroll matchign list
                        }
                    });

                    //Callbacks for hovering over any of the four project layers
                    mapView.map.on('mouseenter', 'project', function(e) {
                        setState('hoverBuilding', e.features[0])
                    });
                    mapView.map.on('mouseenter', 'project-enter', function(e) {
                        setState('hoverBuilding', e.features[0])
                    });
                    mapView.map.on('mouseenter', 'project-exit', function(e) {
                        setState('hoverBuilding', e.features[0])
                    });
                    mapView.map.on('mouseenter', 'project-unmatched', function(e) {
                        setState('hoverBuilding', e.features[0])
                    });

                } // end dataCallback
            } else {
                console.log("ERROR data loaded === false");
            }

        },

        removeAllPopups: function(){
            for (var i = 0; i < mapView.popups.length; i++) {
                if (mapView.popups[i].isOpen()) {
                    mapView.popups[i].remove()
                }
            }
            mapView.popups=[];
        },

        popups: [], //initialize empty

        showPopup: function(msg, data) {
            //Removes any other existing popups, and reveals the one for the selected building

            mapView.removeAllPopups();

            var lngLat = {
                lng: data.properties.longitude,
                lat: data.properties.latitude,
            }
            var popup = new mapboxgl.Popup({
                    'anchor': 'top-right',
                    'closeOnClick':false    //We are manually handling the click event to remove this either on hovering elsewhere or click
                })
                .setLngLat(lngLat)
                .setHTML('<div class="tooltip-field proj_name">' + data.properties.proj_name + '</div>' +
                        '<div class="tooltip-field">' + data.properties.proj_addre + '</div>')
                .addTo(mapView.map);

            popup._container.onclick = function(e) {

                setState('subNav.right', 'buildings');
                setState('previewBuilding', [data, true]); // tru ie flag to scroll matching list
            };

            mapView.popups.push(popup);

            //Close popup if it's open too long
            setTimeout(function(){
                if (popup.isOpen()) {
                    popup.remove()
                }
            },3000);

        },
        scrollMatchingList: function(data){
                var projectData = data[0];
                $('#projects-list .projects-list-selected').removeClass('projects-list-selected'); 
                var $listItem = $('#projects-list #' + projectData.properties.nlihc_id);
                $listItem.addClass('projects-list-selected');
                
                if ( $listItem.length > 0 && data[1]) { // if the map has been filtered the listitem may no longer be in the DOM
                                                        // data[1] == false is the flag to not scroll
                    var difference = $listItem.offset().top - $('#projects-list-group').offset().top; 
                    $('#projects-list-group').animate({
                        scrollTop: $( '#projects-list-group' ).scrollTop() + difference - 7
                    }, 500)
                }
        },  

        showProjectPreview: function(msg, data) {
            var projectData = data[0];
            if ( projectData ) {

                mapView.scrollMatchingList(data);
                  
                if ( projectData.properties.longitude != null && projectData.properties.latitude ){
                    mapView.flyToProject([projectData.properties.longitude, projectData.properties.latitude]);
                }
                //setState('hoverBuildingList', projectData.properties.nlihc_id);
                var project = [projectData.properties];    //defining as one-element array for d3 data binding

                //Bind the selected project to a div that will hold the preview graphics
                var selection = d3.select('#project-preview')
                                .selectAll("div.preview-contents")
                                    .data(project, function(d){
                                        return typeof(d) !== "undefined" ? d.nlihc_id : null; //deals w/ initial div which has no bound data yet
                                    })
                var fadeDuration = 500

                //Transition the whole container of the previously previewed building
                var leaving = selection.exit()
                        .transition()
                        .duration(fadeDuration)
                        .style('opacity',0)
                        .remove()

                //Create the new container
                mapView.showProjectPreview.current = selection.enter()
                            .append('div')
                            .classed("preview-contents",true)
                            .style('opacity',0)
                            //.text(function(d){return d.nlihc_id})

                //callback used to populate container since we need data loaded before it can run
                //callback called after function definition
                mapView.fillContainer = function(meta){
                    var current = mapView.showProjectPreview.current //alias for convenience

                    //Add the building name with a link to the project page
                    var field = getFieldFromMeta('project', 'proj_name') //field is the meta.json that has stuff like display_text
                    var value = project[0]['proj_name'] + ' >>' // adding chevrons to indicate clicking for more, might not
                                                                // even be necessary with underlining

                    current.append('a')
                        .classed('proj_name',true)
                        .text(value)
                        .style("text-decoration", "underline") // to indicate it is a link
                        .on("click", function(e) {
                            setState('selectedBuilding', projectData); //data comes from state - it is the building that was clicked
                            setState('switchView', projectView);
                        });

                    //Add fields that don't have the field name displayed
                    var headerFields =  ['proj_addre','ward','neighborhood_cluster_desc']
                    for (var i = 0; i < headerFields.length; i++) {
                        var field = getFieldFromMeta('project',headerFields[i])
                        var value = project[0][headerFields[i]];
                        value = (value === null | value == "null") ? ' Unknown' : value; // handles when data has "null" as a value

                        current.append('div')
                            .classed('preview-field',true)
                            .classed(headerFields[i],true)
                            .text(value)
                    };

                    //Add line break
                    current.append('br')

                    //Add a definition list of property: value
                    var previewFields =     ['proj_units_assist_max', 'proj_units_tot','subsidy_end_first',
                                            'subsidy_end_last']

                    var dl = current.append('dl')
                            .classed("properties-list",true)
                            .classed("inline",true);

                    for (var i = 0; i < previewFields.length; i++) {
                        var field = getFieldFromMeta('project',previewFields[i])
                        dl.append('dt').text(field['display_name'] + ': '); //todo use meta.json instead

                        var value = project[0][previewFields[i]];
                        value = (value === null | value == "null") ? ' Unknown' : value; // handles when data has "null" as a value
                        dl.append('dd').text(value)
                    }
                };

                controller.getData({
                                name:'metaData',
                                url: model.URLS.metaData,
                                callback: mapView.fillContainer
                                });

                //Make the new container appear after the old one is gone
                setTimeout(function(){
                    mapView.showProjectPreview.current.transition()
                        .duration(fadeDuration)
                        .style('opacity',1)
                },fadeDuration)
            }

        },

        filterMap: function(msg, data) {
            //TODO sometimes this function produces a TypeError "Cannot read property 'features' of undefined" during load
            //This is because filteredData state change on load is getting triggered before convertedProjects is finished loading
            //Doesn't hurt anything, but would be nice to remove error by trigging first call to filteredData later in the load process

            mapView.convertedProjects.features.forEach(function(feature) {
                feature.properties.previous_filters = feature.properties.matches_filters;
                if (data.indexOf(feature.properties.nlihc_id) !== -1) {
                    feature.properties.matches_filters = true;
                    feature.properties.klass = feature.properties.previous_filters === true ? 'stay' : 'enter'; // two trues in a row means stay; new true means enter
                } else {
                    feature.properties.matches_filters = false;
                    feature.properties.klass = feature.properties.previous_filters === false ? 'none' : 'exit'; // two falses in a row means no action; new false means exit
                }
            });
           // mapView.map.setFilter('project-exit', ['==','klass','exit']); // resets exit filter to be meaningful. it's set to nonsense after the animations
                                                                          // so that previous exits don't show when the opacity is set back to 1
            mapView.map.getSource('project').setData(mapView.convertedProjects);
            mapView.animateEnterExit();
            mapView.listBuildings();
        },
        animateEnterExit: function(){
            var delayAnimation = setTimeout(function(){
                mapView.map.setPaintProperty('project-enter','circle-stroke-width', 6);
                var shrinkCircles = setTimeout(function(){
                    mapView.map.setPaintProperty('project-enter','circle-stroke-width', 0);
                },300);

            },250); // a delay is necessary to avoid animating the layer before mapBox finishes applying the filters.
                    // with too little time, you'll see projects that have klass 'stay' animate as if they were 'enter'.
                    // would be nicer with a callback, but I don't htink that's available -JO



        },
        flyToProject: function(lngLatArray) {
            mapView.map.flyTo({
                center: lngLatArray,
                zoom: 15
            });
        },
        /*
        The listBuildings function controls the right sidebar in the main map view.
        Unlike the filter-view side-bar, the buildings list side-bar does not have it's
        own file.  The styling for this section are in the main styles.css file.
        */
        listBuildings: function() {


            var allData = mapView.convertedProjects.features
            var data = allData.filter(function(feature) {
                return feature.properties.matches_filters === true;
            });

            d3.selectAll('.matching-count')
                .text(data.length);

            d3.selectAll('.total-count')
                .text(allData.length);

            var t = d3.transition()
                .duration(750);
            var preview = d3.select('#projects-list')

            var listItems = preview.selectAll('div')
                .data(data, function(d) {
                    return d.properties.nlihc_id; // needs key to do update
                });
                

            listItems.attr('class', 'update');


            listItems.enter().append('div')
                //.attr('class','enter')
                .merge(listItems)
                .html(function(d) {
                    return '<p> <span class="project-title">' + d.properties.proj_name + '</span><br />' +
                        d.properties.proj_addre;
                })
                .on('mouseenter', function(d) {
                    mapView['highlight-timer-' + d.properties.nlihc_id] = setTimeout(function() {
                        setState('hoverBuildingList', d.properties.nlihc_id);
                    }, 500); // timeout minimizes inadvertent highlighting and gives more assurance that quick user actions
                    // won't trip up all the createLayers and remove layers.
                })
                .on('mouseleave', function(d) {
                    clearTimeout(mapView['highlight-timer-' + d.properties.nlihc_id]);
                    setState('hoverBuildingList', false);
                })
                .on('click', function(d) {
                    if ( d.properties.longitude == null || d.properties.latitude == null ) {
                        mapView.alertNoLocationInfo()
                    }
                    setState('previewBuilding', [d, false]); // false is flag to not scroll the list
                })

                .attr('tabIndex', 0)
                .transition().duration(100)
                .attr('class', 'enter')
                .attr('id', function(d){
                    return d.properties.nlihc_id;
                });

            listItems.exit()
                .attr('class', 'exit')
                .transition(t)
                .remove();

            if ( getState().previewBuilding && getState().previewBuilding[0] ){
                setTimeout(function(){
                    mapView.scrollMatchingList(getState().previewBuilding[0]);
                },1000);
            }
         
        },
        alertNoLocationInfo: function(){
            d3.select('#map-wrapper')
              .append('div')
              .classed('no-location-alert', true)
              .style('opacity',0)
              .text('No location available')
              .transition().duration(1000)
              .style('opacity',1)
              .transition().duration(1000)
              .style('opacity',0)
              .remove();
        },
        addExportButton: function() {
          // Get the modal
          var modal = d3.select('#exportDataModal');
          var continuousFiltersTable = d3.select('#exportContinuousFilters');
          var categoricalFiltersTable = d3.select('#exportCategoricalFilters');

          // Get the <span> element that closes the modal
          var span = d3.select(".close")[0];
          d3.select('#csvExportButton')
            .on('click', function(d) {
              continuousFiltersTable._groups[0][0].innerHTML = "";
              categoricalFiltersTable._groups[0][0].innerHTML = "";
              modal.style.display = "block";
              modal.class = "modal-open";
              var activeFilters = filterUtil.getActiveFilterValues();
              var continuousFilters = activeFilters[0];
              var categoricalFilters = activeFilters[1];
              var continuousColumns = ['Filter', 'Min', 'Max', 'Include Nulls'];
              var categoricalColumns = ['Filter', 'Included Categories'];

              console.log("&&& activeFilters", activeFilters);

              if ( continuousFilters.length > 0 ){

                var continuousThead = continuousFiltersTable.append('thead')
                var	continuousTbody = continuousFiltersTable.append('tbody');

                // append the header row
                continuousThead.append('tr')
                  .selectAll('th')
                  .data(continuousColumns).enter()
                  .append('th')
                    .text(function (column) { return column; });

                // create a row for each object in the data
                var continuousRows = continuousTbody.selectAll('tr')
                  .data(continuousFilters)
                  .enter()
                  .append('tr');

                // create a cell in each row for each column
                var continuousCells = continuousRows.selectAll('td')
                  .data(function (row) {
                    return continuousColumns.map(function (column) {
                      return {column: column, value: row[column]};
                    });
                  })
                  .enter()
                  .append('td')
                    .text(function (d) { return d.value; });
              }

              if ( categoricalFilters.length > 0 ){

                var continuousThead = categoricalFiltersTable.append('thead')
                var	continuousTbody = categoricalFiltersTable.append('tbody');

                // append the header row
                continuousThead.append('tr')
                  .selectAll('th')
                  .data(categoricalColumns).enter()
                  .append('th')
                    .text(function (column) { return column; });

                // create a row for each object in the data
                var continuousRows = continuousTbody.selectAll('tr')
                  .data(categoricalFilters)
                  .enter()
                  .append('tr');

                // create a cell in each row for each column
                var continuousCells = continuousRows.selectAll('td')
                  .data(function (row) {
                    return categoricalColumns.map(function (column) {
                      return {column: column, value: row[column]};
                    });
                  })
                  .enter()
                  .append('td')
                    .text(function (d) { return d.value; });
              }

            });
          d3.select('#copyFilterNames')
            .on('click', function(d){
                var activeFilters = filterUtil.getActiveFilterValues();
                var filterTitlesOnly = [].concat.apply([], activeFilters.map(function(objArray){
                    return objArray.map(function(obj){ return obj.Filter; });
                }));
                function setClipBoardToFilterTitleList(event){
                    event.clipboardData.setData('text/plain', filterTitlesOnly.join("\n "));
                    event.preventDefault();
                }
                document.body.addEventListener('copy', setClipBoardToFilterTitleList);
                document.execCommand('copy');
                document.body.removeEventListener('copy', setClipBoardToFilterTitleList);
            });
        },
        exportButton: function() {
          d3.select('#exportCsv')
            .on('click', function(d) {
              exportCsv.exportAllData();
          });
        },

        highlightHoveredBuilding(msg, data) {
            if ( getState().hoverBuildingList[1] ){ // if there's a previous hoverBuildingList state, clear the highlight
                mapView.map.setFilter('project-highlight-hovered-' + getState().hoverBuildingList[1], ['==', 'nlihc_id', '']);
                mapView.map.removeLayer('project-highlight-hovered-' + getState().hoverBuildingList[1]);
            }
            if (data) {
                mapView.map.addLayer({
                    'id': 'project-highlight-hovered-' + data,
                    'type': 'circle',
                    'source': 'project',
                    'paint': {
                        'circle-blur': 0.2,
                        'circle-color': 'transparent',
                        'circle-radius': {
                            'base': 1.75,
                            'stops': [
                                [12, 10],
                                [15, 40]
                            ]
                        },
                        'circle-stroke-width': 4,
                        'circle-stroke-opacity': 1,
                        'circle-stroke-color': '#4D90FE'
                    },
                    'filter': ['==', 'nlihc_id', data]
                });
            }
            
        },
        highlightPreviewBuilding(msg, data) {
            var projectData = data[0];
            if ( getState().previewBuilding[1] ){ // if there's a previous previewBuilding state, clear the highlight
                mapView.map.setFilter('project-highlight-preview-' + getState().previewBuilding[1][0].properties.nlihc_id, ['==', 'nlihc_id', '']);
                mapView.map.removeLayer('project-highlight-preview-' + getState().previewBuilding[1][0].properties.nlihc_id);
            }
            if (projectData) {
                mapView.map.addLayer({
                    'id': 'project-highlight-preview-' + projectData.properties.nlihc_id,
                    'type': 'circle',
                    'source': 'project',
                    'paint': {
                        'circle-blur': 0.2,
                        'circle-color': 'transparent',
                        'circle-radius': {
                                'base': 1.75,
                                'stops': [
                                    [11, 4],
                                    [12, 5],
                                    [15, 16]
                                ]
                            },
                        'circle-stroke-width': 2,
                        'circle-stroke-opacity': 1,
                        'circle-stroke-color': '#bd3621'
                    },
                    'filter': ['==', 'nlihc_id', projectData.properties.nlihc_id]
                });
            }
            
        },
        zoomToFilteredProjects: function(msg, data){
            if ( getState().previewBuilding === undefined || !getState().previewBuilding[0] ) {
                var maxLat = d3.max(data, function(d){
                    return d.latitude;
                });
                var minLat = d3.min(data, function(d){
                    return d.latitude;
                });
                var maxLon = d3.max(data, function(d){
                    if (d.longitude < 0 ) {
                        return d.longitude; // workaround of data error where one project has positive longitude instead of positive
                                            // can remove `if` statement when resolved (issue 405)
                    }
                });
                var minLon = d3.min(data, function(d){
                    return d.longitude;
                });
                mapView.map.fitBounds([[minLon,minLat], [maxLon,maxLat]],
                                {linear: true,
                                padding: {top: 20, bottom: 20, left: 320, right: 370}, //to accomodate sidebars + 20 px
                                maxZoom: 14  //far enough to see whole neighborhood cluster
                                });
                if (getState().filteredProjectsAvailable.length === 1 ) { // if initial onload zoom, reset the originalCenter and originalZoom
                    mapView.map.originalCenter = [mapView.map.getCenter().lng, mapView.map.getCenter().lat];
                    mapView.map.originalZoom = mapView.map.getZoom();
                }
            }
        }
    };
