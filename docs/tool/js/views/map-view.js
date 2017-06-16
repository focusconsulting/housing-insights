    "use strict";

    var mapView = {
        el: 'map-view',

        init: function() { // as single page app, view init() functions should include only what should happen the first time
            // the view is loaded. things that need to happen every time the view is made active should be in
            // the onReturn methods. nothing needs to be there so far for mapView, but buildingView for instance
            // should load the specific building info every time it's made active.
            console.log(this);
            var partialRequest = {
                partial: this.el,
                container: null, // will default to '#body-wrapper'
                transition: false,
                callback: appendCallback
            };
            controller.appendPartial(partialRequest, this);

            function appendCallback() {
                console.log(this);
                setSubs([
                    ['mapLayer', mapView.showLayer],
                    ['mapLayer', mapView.layerOverlayToggle],
                    ['mapLoaded', model.loadMetaData],
                    ['dataLoaded.metaData', mapView.addInitialLayers], //adds zone borders to geojson
                    ['dataLoaded.metaData', resultsView.init],
                    ['dataLoaded.metaData', mapView.placeProjects],
                    ['dataLoaded.metaData', mapView.overlayMenu],
                    ['dataLoaded.raw_project', filterView.init],
                    ['overlayRequest', mapView.addOverlayData],
                    ['overlayRequest', mapView.updateZoneChoiceDisabling],
                    ['joinedToGeo', mapView.addOverlayLayer],
                    ['overlaySet', chloroplethLegend.init],
                    ['previewBuilding', mapView.showPopup],
                    ['filteredData', mapView.filterMap],
                    ['hoverBuildingList', mapView.highlightBuilding]


                ]);


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

                this.map.addControl(new mapboxgl.NavigationControl(), 'bottom-left');

                this.map.on('load', function() {
                    setState('mapLoaded', true);
                });

                this.map.on('zoomend', function() {

                    d3.select('#reset-zoom')
                        .style('display', function() {
                            if (Math.abs(mapView.map.getZoom() - mapView.originalZoom) < 0.001 &&
                                Math.abs(mapView.map.getCenter().lng - mapView.originalCenter[0]) < 0.001 &&
                                Math.abs(mapView.map.getCenter().lat - mapView.originalCenter[1]) < 0.001) {
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
        ChloroplethColorRange: function(chloroData){
            // CHLOROPLETH_STOP_COUNT cannot be 1! There's no reason you'd 
            // make a chloropleth map with a single color, but if you try to,
            // you'll end up dividing by 0 in 'this.stops'. Keep this in mind
            // if we ever want to make CHLOROPLETH_STOP_COUNT user-defined.
            var CHLOROPLETH_STOP_COUNT = 5;
            var MIN_COLOR = 'rgba(255,255,255,0.6)'// "#fff";
            var MAX_COLOR = 'rgba(30,92,223,0.6)'//"#1e5cdf";

            //We only want the scale set based on zones actually displayed - the 'unknown' category returned by the api can 
            //especially screw up the scale when using rates as they come back as a count instead of a rate
            var currentLayer = getState().mapLayer[0]
            var activeZones = []
            model.dataCollection[currentLayer].features.forEach(function(feature){
                var zone = feature.properties.NAME;
                activeZones.push(zone)
            });

            var MAX_DOMAIN_VALUE = d3.max(chloroData, function(d){
                if (activeZones.includes(d.group)) {
                    return d.count;
                } else {
                    return 0;
                };
            });

            var MIN_DOMAIN_VALUE = d3.min(chloroData, function(d){
                return d.count;
            });

            var colorScale = d3.scaleLinear()
                .domain([MIN_DOMAIN_VALUE, MAX_DOMAIN_VALUE])
                .range([MIN_COLOR, MAX_COLOR]);

            this.stops = new Array(CHLOROPLETH_STOP_COUNT).fill(" ").map(function(el, i){
                var stopIncrement = MAX_DOMAIN_VALUE/(CHLOROPLETH_STOP_COUNT - 1);
                var domainValue = Math.round((MAX_DOMAIN_VALUE - (stopIncrement * i))*1000)/1000; //stupid javascript rounding. Close enough for this purpose. 
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

            console.log(location.hostname);

            //TODO we want to move this config data into it's own file or to the api
            mapView.initialOverlays = [{
                    name: "crime_violent_12",
                    display_name: "Crime Rate: Violent 12 months",
                    display_text: "Number of violent crime incidents per 100,000 people reported in the past 12 months.",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/rate/crime/violent/12/<zone>",
                    zones: ["ward", "neighborhood_cluster", "census_tract"],
                    default_layer: "ward",
                    style: "number"
                },
                {
                    name: "crime_nonviolent_12",
                    display_name: "Crime Rate: Non-Violent 12 months",
                    display_text: "Number of non-violent crime incidents per 100,000 people reported in this zone in the past 12 months.",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/rate/crime/nonviolent/12/<zone>",
                    zones: ["ward", "neighborhood_cluster", "census_tract"],
                    default_layer: "ward",
                    style: "number"
                },
                {
                    name: "crime_all_3",
                    display_name: "Crime Rate: All 3 months",
                    display_text: "Total number of crime incidents per 100,000 people reported in the past 12 months.",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/rate/crime/all/3/<zone>",
                    zones: ["ward", "neighborhood_cluster", "census_tract"],
                    default_layer: "ward",
                    style: "number"
                },
                {
                    name: "building_permits_construction",
                    display_name: "Building Permits: Construction 2016",
                    display_text: "Number of construction building permits issued in the zone during 2016. (2017 data not yet available)",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/count/building_permits/construction/12/<zone>?start=20161231", //TODO need to add start date
                    zones: ["ward", "neighborhood_cluster", "zip"],
                    default_layer: "ward",
                    style: "number"
                },
                {
                    name: "building_permits_all",
                    display_name: "Building Permits: All 2016",
                    display_text: "Number of construction building permits issued in the zone during 2016. (2017 data not yet available)",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/count/building_permits/all/12/<zone>?start=20161231",
                    zones: ["ward", "neighborhood_cluster", "zip"],
                    default_layer: "ward",
                    style: "number"
                },
                {
                    name: "poverty_rate",
                    display_name: "ACS: Poverty Rate",
                    display_text: "Fraction of residents below the poverty rate.",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/census/poverty_rate/<zone>",
                    zones: ["ward", "neighborhood_cluster", "census_tract"],
                    default_layer: "census_tract",
                    style: "percent"
                },
                {
                    name: "income_per_capita",
                    display_name: "ACS: Income Per Capita",
                    display_text: "Average income per resident",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/census/income_per_capita/<zone>",
                    zones: ["ward", "neighborhood_cluster", "census_tract"],
                    default_layer: "census_tract",
                    style: "money"
                },
                {
                    name: "labor_participation",
                    display_name: "ACS: Labor Participation",
                    display_text: "Percent of the population that is working",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/census/labor_participation/<zone>",
                    zones: ["ward", "neighborhood_cluster", "census_tract"],
                    default_layer: "census_tract",
                    style: "percent"
                },
                {
                    name: "fraction_single_mothers",
                    display_name: "ACS: Fraction Single Mothers",
                    display_text: "Percent of the total population that is a single mother",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/census/fraction_single_mothers/<zone>",
                    zones: ["ward", "neighborhood_cluster", "census_tract"],
                    default_layer: "census_tract",
                    style: "percent"
                },
                {
                    name: "fraction_black",
                    display_name: "ACS: Fraction Black",
                    display_text: "Proportion of residents that are black or African American",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/census/fraction_black/<zone>",
                    zones: ["ward", "neighborhood_cluster", "census_tract"],
                    default_layer: "census_tract",
                    style: "percent"
                },
                {
                    name: "fraction_foreign",
                    display_name: "ACS: Fraction Foreign",
                    display_text: "Percent of the population that is foreign born",
                    url_format: "http://hiapidemo.us-east-1.elasticbeanstalk.com/api/census/fraction_foreign/<zone>",
                    zones: ["ward", "neighborhood_cluster", "census_tract"],
                    default_layer: "census_tract",
                    style: "percent"
                }
                
            ];
        },

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
            title.attr("id", "overlay-" + overlay.name); //TODO need to change this to different variable after changing meta logic structure

            var content = parent.append("div")
                .classed("content", true)
              .attr("id", "overlay-about-"+overlay.name)
                .text(overlay.display_text)

            $('.ui.accordion').accordion({'exclusive':true}); //only one open at a time

            //Set it up to trigger the layer when title is clicked
            document.getElementById("overlay-" + overlay.name).addEventListener("click", clickCallback);

            function clickCallback() {
                var existingOverlayType = getState().overlaySet !== undefined ? getState().overlaySet[0].overlay : null;
                console.log("changing from " + existingOverlayType + " to " + overlay.name);

                if (existingOverlayType !== overlay.name) {
                    setState('overlayRequest', {
                        overlay: overlay.name,
                        activeLayer: getState().mapLayer[0]
                    });
                } else {
                    mapView.clearOverlay();
                };

                //probably not currently working - disabling of layers
                mapView.layerMenuOptions.forEach(function(opt) {
                    if (thisOption.availableLayerNames.indexOf(opt.name) === -1) {
                        opt.makeUnavailable();
                    } else {
                        opt.makeAvailable();
                    }
                });

            }; //end clickCallback
        },




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
                        var config = mapView.findOverlayConfig('name', data.overlay)
                        var default_layer = config.default_layer

                        //Prevent an infinite loop
                        if (data.activeLayer == default_layer){
                            console.log("ERROR: request for data layer returned null")
                        } else {
                            setState('overlayRequest', {
                                overlay: data.overlay,
                                activeLayer: default_layer
                            });
                        };
                    } else {
                        controller.joinToGeoJSON(data.overlay, grouping, data.activeLayer); // joins the overlay data to the geoJSON *in the dataCollection* not in the mapBox instance
                    };
                }

                var overlayConfig = mapView.findOverlayConfig('name', data.overlay)
                var url = overlayConfig.url_format.replace('<zone>',data.activeLayer)

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

            if (mapView.map.getLayer(data.activeLayer + '_' + data.overlay) === undefined) {

                mapView.map.getSource(data.activeLayer + 'Layer').setData(model.dataCollection[data.activeLayer]); // necessary to update the map layer's data
                // it is not dynamically connected to the dataCollection
                var dataToUse = model.dataCollection[data.overlay + '_' + data.grouping].items;                                                                                     // dataCollection           
        
                // assign the chloropleth color range to the data so we can use it for other
                // purposes when the state is changed
                data.chloroplethRange = new mapView.ChloroplethColorRange(dataToUse);

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
                                'stops': data.chloroplethRange.stopsAscending
                            },
                            'fill-opacity': 1 //using rgba in the chloropleth color range instead
                        }
                    });

                console.log(data.chloroplethRange.stopsAscending);
                };
            mapView.showOverlayLayer(data.overlay, data.activeLayer);

        },
        updateZoneChoiceDisabling: function(msg,data) { // e.g. data = {overlay:'crime',grouping:'neighborhood_cluster',activeLayer:'neighborhood_cluster'}
            //Checks to see if the current overlay is different from previous overlay
            //If so, use the 'zones' to enable/disable zone selection buttons
            
            var layerMenu = d3.select('#layer-menu').classed("myclass",true)
            layerMenu.selectAll('a')
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
                        availableLayers = mapView.findOverlayConfig('name', data.overlay)['zones']
                    };


                  //True if in the list, false if not
                  var status = true
                  if (availableLayers.indexOf(layerType) != -1) {
                    status = false
                  }
                  zoneButton.classed('unavailable',status)
                });
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
            d3.select(selector)
                .attr('class', function() {
                    if (d3.select(this).attr('class') === 'active') {
                        return '';
                    }
                    return 'active';
                });
        },
        initialLayers: [{
                source: 'ward',
                color: "#002D61",
                visibility: 'visible'
            },
            {
                source: 'neighborhood_cluster',
                color: '#0D5C7D',
                visibility: 'none',
            },
            {
                source: 'census_tract',
                color: '#8DE2B8',
                visibility: 'none'
            },
            {
                source: 'zip',
                color: '#0D7B8A',
                visibility: 'none'
            }
        ],
        addInitialLayers: function(msg, data) {

            //This function adds the zone layers, i.e. ward, zip, etc.
            if (data === true) {
                //controller.appendPartial('layer-menu','main-view');
                mapView.initialLayers.forEach(function(layer) { // refers to mapView instead of this bc being called form PubSub
                    //  context. `this` causes error
                    mapView.addLayer(layer);
                });
            } else {
                console.log("ERROR data loaded === false")
            };
        },
        addLayer: function(layer) {
            //Adds an individual zone (ward, zip, etc.) to the geoJSON

            var layerName = layer.source + 'Layer'; // e.g. 'wardLayer'
            var dataRequest = {
                name: layer.source, // e.g. ward
                url: model.URLS.geoJSONPolygonsBase + layer.source + '.geojson',
                callback: addLayerCallback
            };
            controller.getData(dataRequest);

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
                mapView.addToLayerMenu(layer);
            }
        },

        addToLayerMenu: function(layer) {

            d3.select('#layer-menu')
                .append('a')
                .attr('href', '#')
                .attr('id', function() {
                    return layer.source + '-menu-item';
                })
                .attr('class', function() {
                    if (layer.visibility === 'visible') {
                        return 'active';
                    }
                    return '';
                })
                .text(function() {
                    return layer.source.split('_')[0].toUpperCase();
                })
                .on('click', function() {
                    d3.event.preventDefault();
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
            d3.selectAll('#layer-menu a')
                .attr('class', '');
            d3.select('#' + data + '-menu-item')
                .attr('class', 'active');
        },

        placeProjects: function(msg, data) { // some repetition here with the addLayer function used for zone layers. could be DRYer if combined
            // or if used constructor with prototypical inheritance
            if (data === true) {
                //msg and data are from the pubsub module that this init is subscribed to.
                //when called from dataLoaded.metaData, 'data' is boolean of whether data load was successful
                console.log(msg, data);
                var dataURLInfo = model.dataCollection.metaData.project.api;
                var dataURL = dataURLInfo.raw_endpoint;
                var dataRequest = {
                    name: 'raw_project',
                    url: dataURL,
                    callback: dataCallback
                };
                controller.getData(dataRequest);

                function dataCallback() {
                    console.log('in callback');
                    mapView.convertedProjects = controller.convertToGeoJSON(model.dataCollection.raw_project);
                    mapView.convertedProjects.features.forEach(function(feature) {
                        feature.properties.matches_filters = true;
                    });
                    mapView.listBuildings();
                    mapView.map.addSource('project', {
                        'type': 'geojson',
                        'data': mapView.convertedProjects
                    });
                    mapView.circleStrokeWidth = 1;
                    mapView.circleStrokeOpacity = 1;
                    mapView.map.addLayer({
                        'id': 'project',
                        'type': 'circle',
                        'source': 'project',
                        'paint': {
                            'circle-radius': {
                                'base': 1.75,
                                'stops': [
                                    [11, 3],
                                    [12, 4],
                                    [15, 15]
                                ]
                            },
                            'circle-opacity': 0.3,
                            'circle-color': {
                                property: 'category_code', // the field on which to base the color. this is probably not the category we want for v1
                                type: 'categorical',
                                stops: [
                                    ['1 - At-Risk or Flagged for Follow-up', '#f03b20'],
                                    ['2 - Expiring Subsidy', '#8B4225'],
                                    ['3 - Recent Failing REAC Score', '#bd0026'],
                                    ['4 - More Info Needed', '#A9A9A9'],
                                    ['5 - Other Subsidized Property', ' #fd8d3c'],
                                    ['6 - Lost Rental', '#A9A9A9']
                                ]
                            },
                            'circle-stroke-width': mapView.circleStrokeWidth,
                            'circle-stroke-opacity': mapView.circleStrokeOpacity,

                            'circle-stroke-color': {
                                property: 'category_code',
                                type: 'categorical',
                                stops: [
                                    ['1 - At-Risk or Flagged for Follow-up', '#f03b20'],
                                    ['2 - Expiring Subsidy', '#8B4225'],
                                    ['3 - Recent Failing REAC Score', '#bd0026'],
                                    ['4 - More Info Needed', '#A9A9A9'],
                                    ['5 - Other Subsidized Property', ' #fd8d3c'],
                                    ['6 - Lost Rental', '#A9A9A9']
                                ]
                            }
                        }
                    });
                    // TODO: MAKE LEGEND
                    mapView.map.on('mousemove', function(e) {
                        //get the province feature underneath the mouse
                        var features = mapView.map.queryRenderedFeatures(e.point, {
                            layers: ['project']
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
                        console.log(e);
                        var building = (mapView.map.queryRenderedFeatures(e.point, {
                            layers: ['project']
                        }))[0];
                        console.log(building);
                        if (building === undefined) return;
                        setState('previewBuilding', building);
                    });
                } // end dataCallback
            } else {
                console.log("ERROR data loaded === false");
            }

        },

        showPopup: function(msg, data) {
            console.log(data);

            if (document.querySelector('.mapboxgl-popup')) {
                d3.select('.mapboxgl-popup')
                    .remove();
            }

            var lngLat = {
                lng: data.properties.longitude,
                lat: data.properties.latitude,
            }
            var popup = new mapboxgl.Popup({
                    'anchor': 'top-right'
                })
                .setLngLat(lngLat)
                .setHTML('<a href="#">See more about ' + data.properties.proj_name + '</a>')
                .addTo(mapView.map);

            popup._container.querySelector('a').onclick = function(e) {
                e.preventDefault();
                setState('selectedBuilding', data);
                setState('switchView', buildingView);
            };

        },
        filterMap: function(msg, data) {

            mapView.convertedProjects.features.forEach(function(feature) {
                if (data.indexOf(feature.properties.nlihc_id) !== -1) {
                    feature.properties.matches_filters = true;
                } else {
                    feature.properties.matches_filters = false;
                }
            });
            mapView.map.getSource('project').setData(mapView.convertedProjects);
            mapView.map.setFilter('project', ['==', 'matches_filters', true]);
            mapView.listBuildings();

            setTimeout(function() {
                mapView.growShrinkId = requestAnimationFrame(mapView.animateSize);
            }, 0);
            /*
            console.log(data.toString().replace(/([^,]+)/g,"'$1'"));
            var idStr = data.toString().replace(/([^,]+)/g,"'$1'")
            var str = "NL000001";
            mapView.map.setFilter('project',['in','nlihc_id', data]);*/
        },
        animateSize: function(timestamp) {
            setTimeout(function() {
                mapView.shrinkGrow = mapView.shrinkGrow || 'grow';
                mapView.circleStrokeWidth = mapView.shrinkGrow === 'grow' ? mapView.circleStrokeWidth * 2 : mapView.circleStrokeWidth / 2; // ( 20 - mapView.circleStrokeWidth ) / ( 1000 / ( timestamp - mapView.lastTimestamp ));
                mapView.circleStrokeOpacity = mapView.shrinkGrow === 'grow' ? mapView.circleStrokeOpacity / 1.2 : mapView.circleStrokeOpacity * 1.2;
                mapView.map.setPaintProperty('project', 'circle-stroke-width', mapView.circleStrokeWidth);
                mapView.map.setPaintProperty('project', 'circle-stroke-opacity', mapView.circleStrokeOpacity);
                
                //Grow, then shrink, then stop
                if (mapView.shrinkGrow === 'grow' && mapView.circleStrokeWidth >= 10) {
                    //go the other way
                    mapView.shrinkGrow = 'shrink';
                }
                if (mapView.shrinkGrow === 'shrink' && mapView.circleStrokeWidth <= 1) {
                    //stop
                    mapView.shrinkGrow = 'grow'; //ready for next time
                    cancelAnimationFrame(mapView.growShrinkId);
                } else {
                    //keep going same direction w/ recursive call
                    mapView.growShrinkId = requestAnimationFrame(mapView.animateSize);
                }
            }, (1000 / 20));
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
            var preview = d3.select('#buildings-list')

            var listItems = preview.selectAll('div')
                .data(data, function(d) {
                    return d.properties.nlihc_id;
                });

            listItems.attr('class', 'update');

            listItems.enter().append('div')
                //.attr('class','enter')
                .merge(listItems)
                .html(function(d) {
                    return '<p> <span class="project-title">' + d.properties.proj_name + '</span><br />' +
                        d.properties.proj_addre + '<br />' +
                        'Owner: ' + d.properties.hud_own_name + '</p>';
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
                    if (mapView.map.getLayer('project-highlight-' + d.properties.nlihc_id)) {
                        mapView.map.setFilter('project-highlight-' + d.properties.nlihc_id, ['==', 'nlihc_id', '']);
                        mapView.map.removeLayer('project-highlight-' + d.properties.nlihc_id);
                    }
                })
                .on('click', function(d) {

                    mapView.map.flyTo({
                        center: [d.properties.longitude, d.properties.latitude],
                        zoom: 15
                    });
                    setState('previewBuilding', d);
                })

                .attr('tabIndex', 0)
                .transition().duration(100)
                .attr('class', 'enter');

            listItems.exit()
                .attr('class', 'exit')
                .transition(t)
                .remove();

        },
        highlightBuilding(msg, data) {
            if (data) {
                mapView.map.addLayer({
                    'id': 'project-highlight-' + data,
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
        }
    };
