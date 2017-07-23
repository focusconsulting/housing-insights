"use strict";

var filterView = {

    addClearPillboxes: function(msg,data){

        //Compare our activated filterValues (from the state module) to the list of all 
        //possible filterControls to make a list containing only the activated filter objects. 
        //filterValues = obj with keys of the 'source' data id and values of current setpoint
        //filterControls = list of objects that encapsulates the actual component including its clear() method
        var filterValues = filterUtil.getFilterValues();

        var keysWithActiveFilterValues = Object.keys(filterValues).filter(function(key){
            return filterValues[key][0].length !== 0;
        });

        var activeFilterControls = filterView.filterControls.filter(function(filterControl){
            return keysWithActiveFilterValues.indexOf(filterControl.component.source) !== -1;
        });
      
        //Use d3 to bind the list of control objects to our html pillboxes
        var allPills = d3.select('#clear-pillbox-holder')
                        .selectAll('.clear-single')
                        .data(activeFilterControls, function(d){
                            return d.component.source;
                        })
                        .classed("not-most-recent",true);

        allPills.enter().append("div")
            .attr("class","ui label transition hidden")
            .classed("clear-single",true)
            // Animate a label that 'flies' from the filter component
            // to the pillbox.
            .text(function(d) { return d['component']['display_name'];})
            .each(function(d){
                var originElement = document.getElementById("filter-content-"+d.component.source);
                var destinationElement = this;
                var flyLabel = document.createElement('div');
                flyLabel.textContent = this.textContent;
                console.log("flyer this", this);
                flyLabel.classList.add('ui', 'label', 'transition', 'visible', 'clear-single-flier');
                var originRect = originElement.getBoundingClientRect();
                flyLabel.style.left = originRect.left + 'px';
                flyLabel.style.top = ((originRect.top + originRect.bottom)/2) + 'px';
                var flyLabelX = document.createElement('i');
                flyLabelX.classList.add('delete', 'icon');
                document.body.appendChild(flyLabel);
                flyLabel.appendChild(flyLabelX);
                // Change the 'top' and 'left' CSS properties of flyLabel,
                // triggering its CSS transition.
                window.setTimeout(function(){
                    flyLabel.style.left = destinationElement.getBoundingClientRect().left + 'px';
                    flyLabel.style.top = destinationElement.getBoundingClientRect().top + 'px';
                }, 1);

                // Remove flyLabel after its transition has elapsed.
                window.setTimeout(function(){
                    flyLabel.parentElement.removeChild(flyLabel);
                    destinationElement.classList.remove('hidden');
                    destinationElement.classList.add('visible');
                }, 1500);

            })
        //Add the 'clear' x mark and its callback
            .append('i')
            .classed("delete icon",true)
            .on("click", function(d) {
                d.clear();
            })
                       
        allPills.exit().remove();
    },

    init: function(msg, data) {
        //msg and data are from the pubsub module that this init is subscribed to. 
        //when called from dataLoaded.metaData, 'data' is boolean of whether data load was successful
        
        if ( data === true ) {
            //Make sure other functionality is hooked up
            setSubs([
                ['filterViewLoaded', filterUtil.init],
                ['sidebar', filterView.toggleSidebar],
                ['subNav', filterView.toggleSubNavButtons],
                ['filterValues', filterView.indicateActivatedFilters],
                ['anyFilterActive', filterView.handleFilterClearance],
                ['filterValues', filterView.addClearPillboxes],
                ['subNavExpanded.right', filterView.expandSidebar],
                ['mapLayer', filterView.updateLocationFilterControl],
                ['filterViewLoaded', filterView.updateLocationFilterControl] //handles situation where initial mapLayer state is triggered before the dropdown is available to be selected
            ]);

            setState('subNav.left','layers');
            setState('subNav.right','buildings');

            //TODO this is for the triangular boxes to expand/collapse, which might be tweaked in new UI. Check if this is still relevant. 
            document.querySelectorAll('.sidebar-tab').forEach(function(tab){
                tab.onclick = function(e){
                    var sideBarMsg = e.currentTarget.parentElement.id.replace('-','.');
                    filterView.toggleSidebarState(sideBarMsg);
                }
            });

            //Expand/Collapse right sidebar control clickbacks
            d3.select('#expand-sidebar-right')
                .on('click', function(){
                    //toggle which control is shown
                    d3.selectAll('#sidebar-control-right i').classed("hidden",true)
                    d3.select('#compress-sidebar-right').classed("hidden",false)

                    setState('subNavExpanded.right',true)
                });

            d3.select('#compress-sidebar-right')
                .on('click', function(){
                    //Toggle which control is shown
                    d3.selectAll('#sidebar-control-right i').classed("hidden",true)
                    d3.select('#expand-sidebar-right').classed("hidden",false)

                    setState('subNavExpanded.right',false)
                });

            document.querySelectorAll('.sub-nav-button').forEach(function(button){
                button.onclick = function(e){
                    var leftRight = e.currentTarget.parentElement.id.replace('-options','');
                    var subNavType = e.currentTarget.id.replace('button-','');
                    if ( getState()['sidebar.' + leftRight] && getState()['sidebar.' + leftRight][0] ) { // if the associated sidebar is open
                        if (getState()['subNav.' + leftRight][0] === subNavType) { // if the clicked subNav button is already active
                            setState('sidebar.' + leftRight, false); // close the sidebar
                        }
                    } else {
                        setState('sidebar.' + leftRight, true); // open the sidebar
                    }
                    setState('subNav.' + leftRight, subNavType);
                }
            });

            //Get the data and use it to dynamically apply configuration such as the list of categorical options
            controller.getData({
                        name: 'filterData',
                        url: model.URLS.filterData, 
                        callback: filterView.buildFilterComponents
                    }) 
        } else {
            console.log("ERROR data loaded === false")
        };

        // For inheritance
        filterView.continuousFilterControl.prototype = Object.create(filterView.filterControl.prototype);
        filterView.categoricalFilterControl.prototype = Object.create(filterView.filterControl.prototype);
        filterView.locationFilterControl.prototype = Object.create(filterView.categoricalFilterControl.prototype);

    }, //end init
    filterControls: [],
    filterControl: function(component){
        filterView.filterControls.push(this);
        this.component = component;
    },
    continuousFilterControl: function(component){
        filterView.filterControl.call(this, component);
        var c = this.component;
        var contentContainer = filterView.setupFilter(c);

        var slider = contentContainer.append("div")
                .classed("filter", true)
                .classed("slider",true)
                .attr("id",c.source);


        slider = document.getElementById(c.source); //d3 select method wasn't working, override variable
        noUiSlider.create(slider, {
            start: [c.min, c.max],
            connect: true,

            //the wNumb is a number formatting library. This is what was recommended by noUiSlider; we should consider using elsewhere.
            //order of the two wNumb calls corresponds to left and right slider respectively.
            tooltips: [ wNumb({ decimals: c.num_decimals_displayed }), wNumb({ decimals: c.num_decimals_displayed }) ],
            range: {
                'min': c.min,
                'max': c.max
            }

        });

        //Each slider needs its own copy of the sliderMove function so that it can use the current component
        function makeSliderCallback(component){
            return function sliderCallback ( values, handle, unencoded, tap, positions ) {
                // This is the custom binding module used by the noUiSlider.on() callback.

                // values: Current slider values;
                // handle: Handle that caused the event;
                // unencoded: Slider values without formatting;
                // tap: Event was caused by the user tapping the slider (boolean);
                // positions: Left offset of the handles in relation to the slider
                var specific_state_code = 'filterValues.' + component.source
                
                //If the sliders have been 'reset', remove the filter
                if (component.min == unencoded[0] && component.max == unencoded[1]){
                    unencoded = [];
                }
                setState(specific_state_code,unencoded);
            }
        }

        //Construct a new copy of the function with access to the current c variable
        var currentSliderCallback = makeSliderCallback(c)

        //Using 'set' only updates on release. Probably better to use the 'update' method for continuous updates.
        //using 'set' for now for easier development (less console logging of state changes)
        slider.noUiSlider.on('set', currentSliderCallback);

        this.clear = function(){
            // noUISlider native 'reset' method is a wrapper for the valueSet/set method that uses the original options.
            slider.noUiSlider.reset();
        }

        this.isTouched = function(){
            // Since the result of 'get()' is a string, coerce it into a number
            // before determining equality.
            return +slider.noUiSlider.get()[0] !== c.min || +slider.noUiSlider.get()[1] !== c.max;
        }

    },
    setupFilter: function(c){
    //This function does all the stuff needed for each filter regardless of type. 
    //It returns the "content" div, which is where the actual UI element for doing
    //filtering needs to be appended

            //Add a div with label and select element
            //Bind user changes to a setState function
            var parent = d3.select('#filter-components')
            var title = parent.append("div")
                    .classed("title filter-title",true)
                    .classed(c.data_level, true)

                //Add data-specific icon
                if(c.data_level == 'project') {
                    title.append("i")
                    .classed("building icon",true)
                    .attr("style","margin-right:8px;")
                } else if(c.data_level == 'zone'){
                    title.append("i")
                    .classed("icons",true)
                    .attr("style","margin-right:8px;")
                    .html('<i class="home blue icon"></i><i class="corner blue home icon"></i>')
                }
                
                title.append("span")
                    .classed("title-text",true)
                    .text(c.display_name)

                title.attr("id", "filter-"+c.source)

            var content = parent.append("div")
                    .classed("filter", true)
                    .classed(c.component_type,true)
                    .classed("content", true)
                    .attr("id","filter-content-"+c.source);

            var description = content.append("div")
                            .classed("description",true)

                    //Add data-specific icon
                if(c.data_level == 'project') {
                    var helper = description.append("p")
                        .classed("project-flag",true)

                    helper.append("i")
                    .classed("building icon small",true)
                    
                    helper.append("span")
                    .html("Project-specific data set")

                } else if(c.data_level == 'zone'){
                    var helper = description.append("p")
                        .classed("neighborhood-flag", true)

                    helper.append("i")
                    .classed("icons small",true)
                    .html('<i class="home blue icon"></i><i class="corner blue home icon"></i>')
                    
                    helper.append("span")
                    .html("Neighborhood level data set")                   
                    
                }

                description.append("p").html(c.display_text)
            
            //Set it up to trigger the layer when title is clicked
            document.getElementById("filter-" + c.source).addEventListener("click", clickCallback);
            function clickCallback() {
                //TODO this is hacked at the moment, need to restructure how a merged filter+overlay would work together
                //Currently hacking by assuming the overlay.name is the same as c.source (these are essentially the code name of the data set). 
                //True only for ACS median rent, the demo data set. 
                //This function is very similar to the overlay callback but w/ c.source instead of overlay.name
                if (c.data_level == 'zone'){
                    var existingOverlayType = getState().overlaySet !== undefined ? getState().overlaySet[0].overlay : null;
                    console.log("changing from " + existingOverlayType + " to " + c.source);

                    if (existingOverlayType !== c.source) {
                        setState('overlayRequest', {
                            overlay: c.source,
                            activeLayer: getState().mapLayer[0]
                        });

                    } else {
                        mapView.clearOverlay();
                    };
                } else {
                    mapView.clearOverlay();
                };
            }; //end clickCallback

            return content

    },  

    categoricalFilterControl: function(component){
        filterView.filterControl.call(this, component);
        var c = this.component;
        var contentContainer = filterView.setupFilter(c);

        var uiSelector = contentContainer.append("select")
            .classed("ui fluid search dropdown",true)
            .classed("dropdown-" + c.source,true)    //need to put a selector-specific class on the UI to run the 'get value' statement properly
            .attr("multiple", " ")
            .attr("id", c.source);

        //Add the dropdown menu choices
        for(var j = 0; j < c.options.length; j++){
            uiSelector.append("option").attr("value", c.options[j]).text(c.options[j])
            //var select = document.getElementById(c.source);
        }

        $('#'+c.source).dropdown({ fullTextSearch: 'exact' });

        //Set callback for when user makes a change
        function makeSelectCallback(component){
            return function(){
            var selectedValues = $('.ui.dropdown.'+'dropdown-'+component.source).dropdown('get value');
            var specific_state_code = 'filterValues.' + component.source
            setState(specific_state_code,selectedValues);
        }};
        var currentSelectCallback = makeSelectCallback(c)
        
        //TODO change this to a click event instead of any change
        $(".dropdown-"+c.source).change(currentSelectCallback);

        this.clear = function(){
            // 'restore defaults' as an argument of .dropdown resets the dropdown menu to its original state,
            // per the Semantic UI docs.
            $('.dropdown-' + c.source).dropdown('restore defaults');
        }
        
        this.isTouched = function(){
           return $('.dropdown-' + c.source).dropdown('get value').length > 0;
        }

    },


    locationFilterControl: function(component){
        filterView.categoricalFilterControl.call(this, component);
        var c = this.component;
        var contentContainer = d3.select("#filter-content-"+c.source)
        var uiSelector = d3.select(c.source)


        console.log("Set up location filter")
        //TODO we will need to override the callback with a different callback that knows how to tell the state module the right zone type

    },

    updateLocationFilterControl: function(msg,data){
        //Find out what layer is active. (using getState so we can subscribe to any event type)
        var layerType = getState()['mapLayer'][0]
        var choices = filterView.locationFilterChoices[layerType]

        //remove all existing choices
        d3.selectAll("#location option").remove()

        //Add the new ones in
        for(var j = 0; j < choices.length; j++){
            d3.select('#location').append("option")
                .attr("value", choices[j])
                .text(choices[j])
        }
        
    },

    locationFilterChoices: {}, //populated based on data in the buildFilterComponents function
    
    components: dataChoices, //TODO replace all filterView.components references with dataChoices references after @ptgott merges in his changes

    buildFilterComponents: function(){

        //We need to read the actual data to get our categories, mins, maxes, etc. 
        var workingData = model.dataCollection['filterData'].items; 
        
        var parent = d3.select('#filter-components')
                  .classed("ui styled fluid accordion", true)   //semantic-ui styling
            $('#filter-components').accordion({'exclusive':true}) //allows multiple opened

        //Add components to the navigation using the appropriate component type
        for (var i = 0; i < filterView.components.length; i++) {

            console.log("building filter component: " + filterView.components[i].source);
            
            //Set up sliders
            if (filterView.components[i].component_type == 'continuous'){
                
                new filterView.continuousFilterControl(filterView.components[i]);
            }

            
            //set up categorical pickers
            if (filterView.components[i].component_type == 'categorical'){

                //First find the unique list of categories
                var result = [];
                for (var dataRow = 0; dataRow < workingData.length; dataRow++) {
                    if(!result.includes(workingData[dataRow][filterView.components[i].source])){
                        result.push(workingData[dataRow][filterView.components[i].source]);
                    }
                };
                filterView.components[i]['options'] = result;

                new filterView.categoricalFilterControl(filterView.components[i]);
                  
            };

            //set up location picker
            if (filterView.components[i].component_type == 'location'){
                //Create the object itself
                var location_options = ["First select a zone type"];
                filterView.components[i]['options'] = location_options;
                new filterView.locationFilterControl(filterView.components[i]);  

                ///////////////////////////////////////////////////
                //Save the drop down choices for each location type for later use
                ///////////////////////////////////////////////////
                
                //Make empty lists for each type of dropdown
                mapView.initialLayers.forEach(function(layerDefinition){
                    filterView.locationFilterChoices[layerDefinition.source] = []
                });

                //Iterate over the data itself and build a set of unique values
                for (var dataRow = 0; dataRow < workingData.length; dataRow++) {

                    mapView.initialLayers.forEach(function(layerDefinition){
                        if(!filterView.locationFilterChoices[layerDefinition.source].includes(
                                workingData[dataRow][layerDefinition.source])
                            ){
                                filterView.locationFilterChoices[layerDefinition.source].push(
                                    workingData[dataRow][layerDefinition.source]
                                );
                            }
                    }); 
                };
                
            };

            if (filterView.components[i].component_type == 'date'){
                //Add a div with label and select element
                //Bind user changes to a setState function
            };

        }; //end for loop. All components on page.


        //After all filter components are loaded, user is allowed to filter data
        setState('filterViewLoaded',true);

    },
    clearAllFilters: function(){
        for(var i = 0; i < filterView.filterControls.length; i++){
            if(filterView.filterControls[i].isTouched()){
                filterView.filterControls[i].clear();
            }
        }
        filterView.indicateActivatedFilters();
    },

    clearAllButton: {
        init: function(){
            var thisButton = this;

            this.pill = document.createElement('div');
            this.pill.id = 'clearFiltersPillbox';
            this.pill.classList.add('ui', 'label', 'transition', 'visible', 'clear-all');

            this.site = document.getElementById('clear-pillbox-holder');

            this.site.insertBefore(this.pill, this.site.firstChild);
            this.pill.textContent = "Clear all filters";
            
            this.pill.addEventListener('click', function(){
                filterView.clearAllFilters();
            });
        },
        site: undefined,
        tearDown: function(){
            this.pill.parentElement.removeChild(this.pill);
        }    },

    handleFilterClearance: function(message, data){
        if(data === true){
            filterView.clearAllButton.init();
        }
        if(data === false){
            filterView.clearAllButton.tearDown();
        }
    },
    
    indicateActivatedFilters: function(){
        //add/remove classes to the on-page elements that tell the users which filters are currently activated
        //e.g. the filter sidebar data name titles
        var filterValues = filterUtil.getFilterValues();
        var filterStateIsActive = getState()['anyFilterActive'] && getState()['anyFilterActive'][0] == true;
        var noRemainingFilters = ((Object.keys(filterValues)).filter(function(key){
            return filterValues[key][0].length > 0;
        })).length == 0;

        for (key in filterValues){
            var activated = filterValues[key][0].length == 0 ? false : true;
            
            d3.select('#filter-'+key)
                .classed("filter-activated",activated);
        
        };

        if(noRemainingFilters && filterStateIsActive){
            setState('anyFilterActive', false);
        }
        if(!noRemainingFilters && !filterStateIsActive){
            setState('anyFilterActive', true);
        }
    },
    toggleSidebar: function(msg,data){
        var sBar = document.getElementById(msg.replace('.','-'));
        var leftRight = msg.indexOf('left') !== -1 ? 'left' : 'right';
        if ( data === true ) {
            sBar.classList.add('active'); // not supported in lte ie9
            document.getElementById('button-' + getState()['subNav.' + leftRight][0]).classList.add('active');
        } else {
            sBar.classList.remove('active'); // not supported in lte ie9
            document.getElementById('button-' + getState()['subNav.' + leftRight][0]).classList.remove('active');

        }
    },
    toggleSidebarState(sideBarMsg){
        if (getState()[sideBarMsg] && getState()[sideBarMsg][0]) {
            setState(sideBarMsg, false);
        } else {
            setState(sideBarMsg, true);
        }
    },
    toggleSubNavButtons(msg, data) {
        
        var leftRight = msg.indexOf('left') !== -1 ? 'left' : 'right';
        if ( getState()['sidebar.' + leftRight] && getState()['sidebar.' + leftRight][0] ) {
            document.querySelectorAll('#' + leftRight + '-options .sub-nav-button').forEach(function(button){
               button.classList.remove('active');
            });
            document.querySelector('#' + leftRight + '-options #button-' + data).classList.add('active');
        }
        document.querySelector('#' + data).classList.add('active');
        if ( getState()['subNav.' + leftRight] && getState()['subNav.' + leftRight][1] ){
            document.querySelector('#' + getState()['subNav.' + leftRight][1]).classList.remove('active');
        }
    },
    expandSidebar: function(msg, data){
        //data is the state of the expansion, either true or false

        //TODO this does not touch the fact that the sidebar can also be active or not. With current setup this does not cause issues but if controls are rearranged could be an issue
        d3.select('#sidebar-right').classed('expanded', data)
    }

};
