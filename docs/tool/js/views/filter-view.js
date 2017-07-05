"use strict";

var filterView = {

    components: [
        //TODO this hard coded array of objects is just a temporary method.
        //This should be served from the API, probably from meta.json
        //"source" is the column name from the filter table, which should match the table in the original database table.
        //  For this approach to work, it will be cleanest if we never have duplicate column names in our sql tables unless the data has
        //  the same meaning in both places (e.g. 'ward' and 'ward' can appear in two tables but should have same name/format)
        {   source:'location',
            display_name: 'Location',
            display_text: "Dropdown menu updates when selecting a new zone type. <br><br>Logic Incomplete: still need to a) clear the existing filter when new zone is selected and b) writecallback for the locationFilterControl",
            component_type: 'location',
            data_type: 'text',
            data_level: 'project'
        },

        /*
        {   source:'ward',
            display_name: 'Location: Ward',
            display_text: "The largest geograpical division of the city.",
            component_type: 'categorical',
            data_type: 'text',
            data_level: 'project'
        },
        {   source:'neighborhood_cluster_desc',
            display_name: 'Location: Neighborhood Cluster',
            display_text: "39 clusters each combining a set of smaller neighborhoods.",
            component_type: 'categorical',
            data_type: 'text',
            data_level: 'project'
        },
        {   source:'anc',
            display_name: 'Location: ANC',
            display_text: 'Advisory Neighborhood Council',
            component_type: 'categorical',
            data_type: 'text',
            data_level: 'project'
        },
        {   source:'census_tract',
            display_name: 'Location: Census Tract',
            display_text: 'A small division used in collection of the US Census.',
            component_type: 'categorical',
            data_type: 'text',
            data_level: 'project'
        },
        {   source:'zip',
            display_name: 'Location: Zipcode',
            display_text: '',
            component_type: 'categorical',
            data_type: 'text',
            data_level: 'project'
        },
        */
        {   source: 'proj_units_tot',
            display_name: 'Total units in project',
            display_text: 'Total count of units in the project, including both subsidized and market rate units.',
            component_type: 'continuous',
            data_type:'integer',
            min: 0,
            max: 717,
            num_decimals_displayed: 0, //0 if integer, 1 otherwise. Could also store data type instead. 
            data_level: 'project'
        },
        
        {   source: 'proj_units_assist_max',
            display_name: "Subsidized units (max)",
            display_text: "The number of subsidized units in the project. When a project participates in multiple subsidy programs, this number is the number of units subsidized by the program with the most units. Partially overlapping subsidies could result in more units than are reflected here.",
            component_type: 'continuous',
            data_type:'integer',
            min:0,
            max:600,
            num_decimals_displayed:0,
            data_level: 'project'
        },
        {   source: 'hud_own_type',
            display_name:'Ownership Type (per HUD)',
            display_text:"This field is only available for buildings participating in HUD programs; others are listed as 'Unknown'",
            component_type: 'categorical',
            data_type:'text',
            data_level: 'project'
        },

        {   source: 'acs_median_rent',
            display_name: 'ACS: Median Neighborhood Rent',
            display_text: 'Filters to buildings that are in a census tract that has a median rent between the indicated levels, per the American Community Survey. ACS rent combines both subsidized and market rate rent.',
            component_type: 'continuous',
            data_type:'decimal',
            min: 0,
            max: 2500,
            num_decimals_displayed: 0, //0 if integer, 1 otherwise. Could also store data type instead.
            data_level: 'zone'
        },

        //TODO this is a dummy data set to show a second option for combined overlay/filtering!!!
        {
            source: "building_permits_construction",
            display_name: "Building Permits: Construction 2016",
            display_text: "Important! This is not actually included in our filter data yet, shown as a demo",
            component_type: 'continuous',
            data_type:'decimal',
            min: 0,
            max: 2500,
            num_decimals_displayed: 0, //0 if integer, 1 otherwise. Could also store data type instead.
            data_level: 'zone'
        },




        {   source: 'portfolio',
            display_name: 'Subsidy Program',
            display_text: 'Filters to buildings that participate in at least one of the selected programs. Note some larger programs are divided into multiple parts in this list',
            component_type:'categorical',
            data_type: 'text',
            data_level: 'project'
        },
        {   source:'poa_start',
            display_name:'Subsidy Start Date',
            display_text: 'Filters to buildings with at least one subsidy whose start date falls between the selected dates.',
            component_type: 'date',
            data_type: 'timestamp',
            min: '1950-01-01', //just example, TODO change to date format
            max: 'now',         //dummy example
            data_level: 'project'
        },
        {   source:'poa_end',
            display_name:'Subsidy End Date',
            display_text: 'Filters to buildings with at least one subsidy whose end date falls between the selected dates.',
            component_type: 'date',
            data_type: 'timestamp',
            min: '1950-01-01', //just example, TODO change to date format
            max: 'now',         //dummy example
            data_level: 'project'
        },
       
    ],

    addClearPillboxes: function(msg,data){
    
        for (var i=0; i < filterView.filterControls.length; i++){
            var x = filterView.filterControls[i]['component']['source'] //display_name
        }

        //Compare our activated filterValues (from the state module) to the list of all 
        //possible filterControls to make a list containing only the activated filter objects. 
        //filterValues = obj with keys of the 'source' data id and values of current setpoint
        //filterControls = list of objects that encapsulates the actual component including its clear() method
        var activeFilterIds = []
        var filterValues = filterUtil.getFilterValues()
        for (var key in filterValues){
            if (filterValues[key][0].length != 0){
                var control = filterView.filterControls.find(function(obj){
                    return obj['component']['source'] === key;
                })
                activeFilterIds.push(control)
            };
        }
        
        //Use d3 to bind the list of control objects to our html pillboxes
        var oldPills = d3.select('#clear-pillbox-holder')
                        .selectAll('.clear-single')
                        .data(activeFilterIds)
                        .classed("not-most-recent",true);

        var allPills = oldPills.enter().append("div")
            .attr("class","ui label transition visible")
            .classed("clear-single",true)
          .merge(oldPills)
            .text(function(d) { return d['component']['display_name'];});

        //Add the 'clear' x mark and its callback
        allPills.each(function(d) {
            d3.select(this).append("i")
                .classed("delete icon",true)
                .on("click", function(d) {
                    d.clear();
                })
        });

        oldPills.exit().remove();

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
                ['mapLayer', filterView.updateLocationFilterControl],
                ['filterViewLoaded', filterView.updateLocationFilterControl] //handles situation where initial mapLayer state is triggered before the dropdown is available to be selected
            ]);

            setState('subNav.left','layers');
            setState('subNav.right','buildings');

            document.querySelectorAll('.sidebar-tab').forEach(function(tab){
                tab.onclick = function(e){
                    var sideBarMsg = e.currentTarget.parentElement.id.replace('-','.');
                    filterView.toggleSidebarState(sideBarMsg);
                }
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
            return slider.noUiSlider.get()[0] === c.min && slider.noUiSlider.get()[1] === c.max;
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

    buildFilterComponents: function(){

        //We need to read the actual data to get our categories, mins, maxes, etc. 
        var workingData = model.dataCollection['filterData'].items; 
        
        //Add components to the navigation using the appropriate component type
        for (var i = 0; i < filterView.components.length; i++) {

            //Set up sliders
            if (filterView.components[i].component_type == 'continuous'){
                
                new filterView.continuousFilterControl(filterView.components[i]);
            }
                           

            var parent = d3.select('#filter-components')
                  .classed("ui styled fluid accordion", true)   //semantic-ui styling
            $('#filter-components').accordion({'exclusive':true}) //allows multiple opened

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
            this.pill.classList.add('ui', 'label', 'transition', 'visible');

            this.site = document.getElementById('button-filters');
            this.replacedText = this.site.innerText;

            this.trigger = document.createElement('i');
            this.trigger.id = 'clearFiltersTrigger';
            this.trigger.classList.add('delete', 'icon');

            this.site.innerText = "";

            this.pill.innerText = this.replacedText;

            this.site.appendChild(this.pill);
            this.pill.appendChild(this.trigger);
            
            this.trigger.addEventListener('click', function(){
                filterView.clearAllFilters();
            });
        },
        replacedText: undefined,
        site: undefined,
        tearDown: function(){
            console.log("this.pill", this.pill);
            console.log("this.pill.parentElement", this.pill.parentElement);
            this.pill.parentElement.removeChild(this.pill);
            this.trigger.parentElement.removeChild(this.trigger);
            this.site.innerText = this.replacedText;
        },
        trigger: undefined
    },

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
    }

};
