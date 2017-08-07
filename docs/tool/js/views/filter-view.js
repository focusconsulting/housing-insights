"use strict";

var filterView = {

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
                //['nullsShown', filterView.indicateActivatedFilters],
                ['anyFilterActive', filterView.handleFilterClearance],
                ['filterValues', filterView.addClearPillboxes],
                //['nullsShown', filterView.addClearPillboxes],
                ['dataLoaded.filterData', filterView.formatFilterDates],
                ['filterDatesFormatted', filterView.buildFilterComponents],
                ['subNavExpanded.right', filterView.expandSidebar],
                ['mapLayer', filterView.clearLocationBasedFilters],
                ['mapLayer', filterView.updateLocationFilterControl],
                ['mapLayer', filterView.resetZoneFilters],
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
                        url: model.URLS.filterData
                    }) 
        } else {
            console.log("ERROR data loaded === false")
        };

        // For inheritance
        filterView.continuousFilterControl.prototype = Object.create(filterView.filterControl.prototype);
        filterView.categoricalFilterControl.prototype = Object.create(filterView.filterControl.prototype);
        filterView.locationFilterControl.prototype = Object.create(filterView.categoricalFilterControl.prototype);

    }, //end init
    // Iterate through dataCollection.filterData and, for any property
    // that's of type 'date', turn the value into a JS date.
    // This is necessary for comparing dates.
    formatFilterDates: function(){
        var dateComponents = filterView.components.filter(function(component){
            return component.component_type === 'date';
        });

        // assumes the string is of the format yyyy-mm-dd.
        function makeDateFromString(val){
            if(val === null){ return null }
            var dateSplit = val.split('-');
            
            return new Date(+dateSplit[0], +dateSplit[1] - 1, +dateSplit[2]);
        }

        model.dataCollection.filterData.objects.forEach(function(item){
            dateComponents.forEach(function(dateComponent){
                if(item.hasOwnProperty(dateComponent.source)){
                    item[dateComponent.source] = makeDateFromString(item[dateComponent.source]);
                }
            });
        });

        setState("filterDatesFormatted", true);

    },
    filterControls: [],
    filterControlsDict: {},
    filterControl: function(component){
        //TODO refactor to use Dict instead of list version. Keeping both for now
        filterView.filterControls.push(this);
        filterView.filterControlsDict[component.short_name] = this;
        this.component = component;
    },
    nullValuesToggle: function(component, filterControl){
        var ths = this;
        this.container = document.createElement('div');
        this.container.classList.add('nullsToggleContainer');
        this.element = document.createElement('input');
        this.element.setAttribute('type', 'checkbox');
        this.element.setAttribute('value', 'showNulls-' + component.source);
        this.element.setAttribute('name', 'showNulls-' + component.source);

        if(filterControl.hasOwnProperty('nullsShown') && filterControl.nullsShown){
            this.element.checked = filterControl.nullsShown;
        }
        var txt = document.createTextNode("Unknown values included");

        var toggleAction;

        this.toDOM = function(parentElement){
            parentElement.appendChild(this.container);
            this.container.appendChild(this.element);
            this.container.appendChild(txt);
        }

        // toggles between values 'true' and 'false' 
        // of object.property when the switch is clicked.
        this.bindPropertyToToggleSwitch = function(object, property, callback){
            function toggleProperty(){
                // Assign the property if it hasn't been assigned.
                object[property] = object[property] || false;
                object[property] = !object[property];

                callback();
            }
            this.element.addEventListener('change', toggleProperty);
            toggleAction = toggleProperty;
        }

        this.triggerToggleWithoutClick = function(){
            if(toggleAction){
                toggleAction();
                this.element.checked = filterControl.nullsShown;
            }
        }
    },
    filterInputs: {}, // adding filterInputs object so we can access them later -JO
    dateInputs: {}, // same for date inputs - JO
    // filterTextInput takes as a parameter an array of keys.
    // It produces text inputs corresponding to these keys and
    // tracks their values.
    // sourceObj is one element in dataChoices.
    // keyValuePairsArray takes the form, [[key, val], [key, val]...]
    filterTextInput: function(sourceObj, keyValuePairsArrayMin, keyValuePairsArrayMax){
        var output = {
            min: {},
            max: {}
        };

        var initialValues = {
            min: keyValuePairsArrayMin,
            max: keyValuePairsArrayMax
        }

        var submitButton = document.createElement('button');
        submitButton.classList.add('nullValuesToggleSubmit');
        submitButton.setAttribute('type', 'button');

        //function that creates the text boxes on the page
        this.toDOM = function(parentElement, separatorCallback){
            // separatorCallback is a function that returns
            // a JavaScript Node object to be appended after each
            // input element.

            var toSpan = document.createElement('span');
            toSpan.textContent = 'to';
            for(var pole in output){
                for(var key in output[pole]){
                    parentElement.appendChild(output[pole][key]);
                    if(separatorCallback && Object.keys(output[pole]).indexOf(key) < Object.keys(output[pole]).length - 1){
                        parentElement.appendChild(separatorCallback());
                    }
                }
                if(pole === 'min'){
                    parentElement.appendChild(toSpan);
                }
            }
            parentElement.appendChild(submitButton);
        }

        this.setValues = function(keyValuePairsArrayMin, keyValuePairsArrayMax){
            for(var i = 0; i < keyValuePairsArrayMin.length; i++){
                output.min[keyValuePairsArrayMin[i][0]].value = keyValuePairsArrayMin[i][1];
            }
            for(var i = 0; i < keyValuePairsArrayMax.length; i++){
                output.max[keyValuePairsArrayMax[i][0]].value = keyValuePairsArrayMax[i][1];
            }
        }

        this.reset = function(){
            this.setValues(initialValues.min, initialValues.max);
        }

        this.returnValues = function(){
            var valueOutput = {
                min: {},
                max: {}
            };
            for(var pole in valueOutput){
                for(var key in output[pole]){
                    valueOutput[pole][key] = output[pole][key].value;
                }
            }
            return valueOutput;
        }

        this.setInputCallback = function(callback){
            
            this.callback = callback; // making callback function a property of the filterTextInput so we can access it later -JO
            var checkKeyPress = function(e){
                if(e.charCode === 9 || e.charCode === 13){
                    callback();
                }
            }

            submitButton.addEventListener('click', callback);

            var setUpInputEventListeners = function (element){

                function setUpKeyPressListener(e){
                    element.addEventListener('keypress', checkKeyPress);
                }

                function tearDownKeyPressListener(e){
                    element.removeEventListener('keypress', checkKeyPress)
                }

                element.addEventListener('focus', setUpKeyPressListener);
                element.addEventListener('blur', function(e){
                   callback();
                   tearDownKeyPressListener(e);
                });
            }
            for(var pole in output){
                for(var key in output[pole]){
                    setUpInputEventListeners(output[pole][key]);
                }
            }

        }

        this.allInputElements = function(){
            var minInputs = Object.keys(output['min']).map(function(key){
                return output['min'][key];
            });

            var maxInputs = Object.keys(output['max']).map(function(key){
                return output['max'][key];
            });
            return minInputs.concat(maxInputs);
        }


        //Create the element and put it 
        for (var i = 0; i < keyValuePairsArrayMin.length; i++){
            output['min'][keyValuePairsArrayMin[i][0]] = document.createElement('input');
            output['min'][keyValuePairsArrayMin[i][0]].setAttribute(
                'id', sourceObj.source + '-' + keyValuePairsArrayMin[i][0] + '-text'
            );
            output['min'][keyValuePairsArrayMin[i][0]].classList.add('filter-text');
            output['min'][keyValuePairsArrayMin[i][0]].classList.add(keyValuePairsArrayMin[i][0] + '-text');
            output['min'][keyValuePairsArrayMin[i][0]].setAttribute('name', keyValuePairsArrayMin[i][0]);
            output['min'][keyValuePairsArrayMin[i][0]].value = keyValuePairsArrayMin[i][1];
        }
        for (var i = 0; i < keyValuePairsArrayMax.length; i++){
            output['max'][keyValuePairsArrayMax[i][0]] = document.createElement('input');
            output['max'][keyValuePairsArrayMax[i][0]].setAttribute(
                'id', sourceObj.source + '-' + keyValuePairsArrayMax[i][0] + '-text'
            );
            output['max'][keyValuePairsArrayMax[i][0]].classList.add('filter-text');
            output['max'][keyValuePairsArrayMax[i][0]].classList.add(keyValuePairsArrayMax[i][0] + '-text');
            output['max'][keyValuePairsArrayMax[i][0]].setAttribute('name', keyValuePairsArrayMax[i][0]);
            output['max'][keyValuePairsArrayMax[i][0]].value = keyValuePairsArrayMax[i][1];
        }

    },
    continuousFilterControl: function(component){
        //Creates a new filterControl on the sidebar. 
        //component is the variable of configuration settings pulled from dataChoices.js

        //Aliases
        var c = component;
        var ths = this;

        //Setup
        filterView.filterControl.call(this, component);
        var contentContainer = filterView.setupFilter(c);
        
        //Find initial values for controls
        this.calculateParams = function(){
        //Uses the current data set to define min/max levels for the UI. 
        //Can be re-run to find new values if the zone type is changed
            
            //If calculating params, reset nullsShown checkbox
            this.nullsShown = true;

            //If it's a zone-level data set, need to choose the right column
            var modifier = c.data_level == 'zone' ? ("_" + getState()['mapLayer'][0]) : '' 
            var data_field = c.source + modifier
            
            var allDataValuesForThisSource = model.dataCollection.filterData.objects.map(function(item){
                return item[data_field];
            });
            this.minDatum = d3.min(allDataValuesForThisSource) || 0;
            this.maxDatum = d3.max(allDataValuesForThisSource) || 1;
            this.stepCount = Math.max(1, parseInt((this.maxDatum - this.minDatum)/500));

            if (c.style === "percent") {
                this.minDatum = Math.round(this.minDatum * 100) / 100;
                this.maxDatum = Math.round(this.maxDatum * 100) / 100;
            } else { //"number", "money"
                this.minDatum = Math.round(this.minDatum);
                this.maxDatum = Math.round(this.maxDatum);
            }
        }
        
        this.calculateParams();

        //Make the slider itself
        contentContainer.append("div")
            .classed("filter", true)
            .classed("slider",true)
            .attr("id",c.source);

        this.slider = document.getElementById(c.source);
        
        noUiSlider.create(this.slider, {
            start: [this.minDatum, this.maxDatum],
            connect: true,
            tooltips: [ false, false ], //using textboxes instead
            range: {
                'min': this.minDatum,
                'max': this.maxDatum
            },
            step: this.stepCount
        });
        
        ////////////////////////
        //Set up the text boxes
        ////////////////////////

        //Create object instance
        var textBoxes = new filterView.filterTextInput( 
            c,        
            [['min', this.minDatum]],
            [['max', this.maxDatum]]
        );
        filterView.filterInputs[this.component.short_name] = textBoxes;
 
        //Append a 'span' that will hold the text input boxes
        var inputContainer = document.createElement('span');
        inputContainer.setAttribute('id', c.source + '-input');
        inputContainer.classList.add('text-input', 'continuous');
        document.getElementById('filter-content-' + c.source).appendChild(inputContainer);

        //Add it to the DOM
        textBoxes.toDOM(
            document.getElementById(c.source + '-input')//parent dom object
        );
        textBoxes.allInputElements().forEach(function(el){
            el.classList.add('continuous-input-text');
        });


        ////////////////////////
        //Set up nulls toggle
        ////////////////////////
        //Set up the toggle button for nulls
        var toggle = new filterView.nullValuesToggle(c, ths);
        toggle.toDOM(document.getElementById('filter-content-' + c.source));


        ////////////////////////
        //Link UI components to state and each other
        ////////////////////////
        
        //Toggle
        //TODO this binding needs to be rewritten - currently it switches back and forth, so can break if set to wrong initial state
        toggle.bindPropertyToToggleSwitch(ths, 'nullsShown', function(){
            setState('nullsShown.' + c.source, ths.nullsShown);
        });

        //Textbox
        var inputCallback = function(){
        //When textbox inputs change - need to adjust the slider and setState. 

            var specific_state_code = 'filterValues.' + component.source
            var returnVals = textBoxes.returnValues();

            this.slider.noUiSlider.set(
                [returnVals['min']['min'], returnVals['max']['max']]
            );

            setState(specific_state_code, [returnVals['min']['min'], returnVals['max']['max'], ths.nullsShown]);
        }

        textBoxes.setInputCallback(inputCallback);

        //slider
        function makeSliderCallback(component, doesItSetState){
            //Make a copy of the callback with access to current variables

            return function sliderCallback ( values, handle, unencoded, tap, positions ) {
                /*  This is the custom binding module used by the noUiSlider.on() callback.
                    values: Current slider values;
                    handle: Handle that caused the event;
                    unencoded: Slider values without formatting;
                    tap: Event was caused by the user tapping the slider (boolean);
                    positions: Left offset of the handles in relation to the slider
                */

                // Round the filter up
                unencoded = unencoded.map(function(el){
                    return el >= 0 ? Math.ceil(el) : el;
                });

                //Bind the slider values to the textboxes
                var min = unencoded[0]
                var max = unencoded[1]
                textBoxes.setValues([['min', min]],[['max', max]]);

                //Set the filterValues state
                if(doesItSetState){
                    var specific_state_code = 'filterValues.' + component.source
                    unencoded.push(ths.nullsShown);
                    setState(specific_state_code,unencoded);
                }

            }
        }

        // Changing value should trigger map update
        var currentSliderCallback = makeSliderCallback(c, true)
        this.slider.noUiSlider.on('change', currentSliderCallback);

        // Sliding slider should update textboxes only
        var slideSliderCallback = makeSliderCallback(c, false)
        this.slider.noUiSlider.on('slide', slideSliderCallback);



        //Public methods
        this.clear = function(){
            var specific_state_code = 'filterValues.' + component.source;

            this.slider.noUiSlider.set([this.minDatum,this.maxDatum])
            textBoxes.setValues([['min', this.minDatum]],[['max', this.maxDatum]]);

            if ( !getState()['nullsShown.' + component.source][0] ) {
                toggle.triggerToggleWithoutClick();
            } 
            setTimeout(function(){ // not sure why but forcing this to run async (with setTimeout hack) is the only
                                   // way it works. as if otherwise it fires before toggle.triggerToggleWithoutClick finished
                setState(specific_state_code, []);
            });
        };

        this.isTouched = function(){
            var returnVals = textBoxes.returnValues();
            return returnVals.min.min !== this.minDatum || returnVals.max.max !== this.maxDatum || this.nullsShown === false;
        };

        this.set = function(min,max,nullValue){

            textBoxes.setValues([['min', min]],[['max', max]]);
            this.slider.noUiSlider.set([min, max]);
            //TODO set toggle in better way
            document.querySelector('[name="showNulls-' + c.source + '"]').checked = nullValue;

            setState('filterValues.' + c.source,[min,max,nullValue]);
        };


        this.rebuild = function() {
            this.calculateParams()
            this.slider.noUiSlider.updateOptions({
                start: [this.minDatum, this.maxDatum],
                range: {
                    'min': this.minDatum,
                    'max': this.maxDatum
                }
            });
            this.clear()
        }

        // At the very end of setup, set the 'nullsShown' state so that it's available for
        // use by code in filter.js that iterates through filterValues.
        setState('nullsShown.' + c.source, ths.nullsShown);
    },
    dateFilterControl: function(component){
        //Creates a new filterControl on the sidebar. 
        //component is the variable of configuration settings pulled from dataChoices.js


        filterView.filterControl.call(this, component);
        var c = this.component;
        var ths = this;

        this.nullsShown = true;

        var contentContainer = filterView.setupFilter(c);

        var slider = contentContainer.append('div')
            .classed('filter', true)
            .classed('slider', true)
            .attr('id', c.source);

        var inputContainer = document.createElement('span');
        inputContainer.setAttribute('id', c.source + '-input');
        inputContainer.classList.add('text-input', 'date');

        document.getElementById('filter-content-' + c.source).appendChild(inputContainer);

        // this is used for d3.min and d3.max.
        var componentValuesOnly = model.dataCollection.filterData.objects.map(function(item){
            return item[c.source];
        });
            
        var minDatum = d3.min(componentValuesOnly);
        var maxDatum = d3.max(componentValuesOnly);

        slider = document.getElementById(c.source);
        noUiSlider.create(slider, {
            start: [minDatum, maxDatum],
            connect: true,
            tooltips: [ false, false ],
            range: {
                'min': minDatum.getFullYear(),
                'max': maxDatum.getFullYear()
            },
            step: 1
        });
        // as with textInputs, adds each instance of dateInput to the filterView.dateInputs object, so it can be accessed
        // later
        filterView.filterInputs[this.component.short_name] = new filterView.filterTextInput(
            component,        
            [
                ['day', minDatum.getDate()],
                ['month', minDatum.getMonth() + 1],
                ['year', minDatum.getFullYear()]
            ],
            [
                ['day', maxDatum.getDate()],
                ['month', maxDatum.getMonth() + 1],
                ['year', maxDatum.getFullYear()]
            ]
        );
        var dateInputs = filterView.filterInputs[this.component.short_name];
        function makeSliderCallback(component, doesItSetState){

            return function sliderCallback ( values, handle, unencoded, tap, positions ) {
                // This is the custom binding module used by the noUiSlider.on() callback.

                // values: Current slider values;
                // handle: Handle that caused the event;
                // unencoded: Slider values without formatting;
                // tap: Event was caused by the user tapping the slider (boolean);
                // positions: Left offset of the handles in relation to the slider
                var specific_state_code = 'filterValues.' + component.source

                var dateForYear = function(minOrMax, year){
                    var minOrMaxObj = {
                        'min': minDatum,
                        'max': maxDatum
                    }
                    if(year === minOrMaxObj[minOrMax].getFullYear()){
                        return minOrMaxObj[minOrMax];
                    }
                    else{
                        return new Date(year, 0, 1);
                    }
                }

                var newMinDate = dateForYear('min', +unencoded[0]);
                var newMaxDate = dateForYear('max', +unencoded[1]);

                dateInputs.setValues(
                    [
                        ['year', newMinDate.getFullYear()],
                        ['month', newMinDate.getMonth() + 1],
                        ['day', newMinDate.getDate()]
                    ],
                    [
                        ['year', newMaxDate.getFullYear()],
                        ['month', newMaxDate.getMonth() + 1],
                        ['day', newMaxDate.getDate()]
                    ]
                );
                
                if(doesItSetState){
                    setState(specific_state_code,[newMinDate, newMaxDate, ths.nullsShown]);
                }
            }
        }

        var currentSliderCallback = makeSliderCallback(c, true);
        var slideSliderCallback = makeSliderCallback(c, false);
        
        // Binding currentSliderCallback to 'change'
        // so that it doesn't trigger when the user changes
        // the filter values through the text input boxes
        // (which then move the slider to a certain position)
        slider.noUiSlider.on('change', currentSliderCallback);
        
        // Change the value of the text input elements without
        // setting state
        slider.noUiSlider.on('slide', slideSliderCallback);

        function getValuesAsDates(){

            var minVals = dateInputs.returnValues()['min'];
            var maxVals = dateInputs.returnValues()['max'];

            return {
                min: new Date(minVals.year, minVals.month - 1, minVals.day),
                max: new Date(maxVals.year, maxVals.month - 1, maxVals.day)
            }

        }

        var inputCallback = function(){
            var specific_state_code = 'filterValues.' + component.source

            var dateValues = getValuesAsDates();
            
            slider.noUiSlider.set(
                [dateValues.min.getFullYear(), dateValues.max.getFullYear()]
            );

            setState(specific_state_code, [dateValues.min, dateValues.max, ths.nullsShown]);
        }

        // For separating date inputs with a '/'
        function addSlash(){
            return document.createTextNode('/');
        }

        dateInputs.setInputCallback(inputCallback);
        dateInputs.toDOM(
            document.getElementById(c.source + '-input'),
            addSlash
        );

        var toggle = new filterView.nullValuesToggle(c, ths);
        toggle.bindPropertyToToggleSwitch(ths, 'nullsShown', function(){
            setState('nullsShown.' + c.source, ths.nullsShown);
        });
        toggle.toDOM(document.getElementById('filter-content-' + c.source));


        this.clear = function(){
            var specific_state_code = 'filterValues.' + component.source;
            // noUISlider native 'reset' method is a wrapper for the valueSet/set method that uses the original options.
            slider.noUiSlider.reset();
            dateInputs.reset();
            if ( !getState()['nullsShown.' + component.source][0] ) {
                toggle.triggerToggleWithoutClick();
            } 
            setTimeout(function(){ // not sure why but forcing this to run async (with setTimeout hack) is the only
                                   // way it works. as if otherwise it fires before toggle.triggerToggleWithoutClick finished
                setState(specific_state_code, []);
            });
        }

        this.isTouched = function(){
            var dateValues = getValuesAsDates();
            return dateValues.min !== minDatum || dateValues.max !== maxDatum || this.nullsShown === false;
        }

        // At the very end of setup, set the 'nullsShown' state so that it's available for
        // use by code in filter.js that iterates through filterValues.
        setState('nullsShown.' + c.source, ths.nullsShown);

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

            return content;

    },  

    categoricalFilterControl: function(component){
        //Creates a new filterControl on the sidebar. 
        //component is the variable of configuration settings pulled from dataChoices.js

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
        var layerType = getState()['mapLayer'][0];
        var choices = filterView.locationFilterChoices[layerType];

        //remove all existing choices
        d3.selectAll("#location option").remove();

        //Add the new ones in
        for(var j = 0; j < choices.length; j++){
            d3.select('#location').append("option")
                .attr("value", choices[j])
                .text(choices[j]);
        }
        
    },

    locationFilterChoices: {}, //populated based on data in the buildFilterComponents function
    
    components: dataChoices, //TODO replace all filterView.components references with dataChoices references after @ptgott merges in his changes

    buildFilterComponents: function(){

        //We need to read the actual data to get our categories, mins, maxes, etc. 
        var workingData = model.dataCollection['filterData'].objects; 
        
        var parent = d3.select('#filter-components')
                  .classed("ui styled fluid accordion", true)   //semantic-ui styling
            $('#filter-components').accordion({'exclusive':true}) //allows multiple opened

        //Add components to the navigation using the appropriate component type
        for (var i = 0; i < filterView.components.length; i++) {

            console.log("building filter component: " + filterView.components[i].source);
            
            //Set up sliders
            if (filterView.components[i].component_type === 'continuous'){
                
                new filterView.continuousFilterControl(filterView.components[i]);
            }

            if (filterView.components[i].component_type === 'date'){
                new filterView.dateFilterControl(filterView.components[i]);
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
    clearLocationBasedFilters: function(){
        function isLocationBased(filterControl){
            return filterControl.component.component_type === 'location';
        }
        function isZoneBased(filterControl){
            return filterControl.component.data_level === 'zone';
        }
        for(var i = 0; i < filterView.filterControls.length; i++){
            if(isLocationBased(filterView.filterControls[i]) && filterView.filterControls[i].isTouched()){
                filterView.filterControls[i].clear();
            }
            /*
            if(isZoneBased(filterControl)){
                filterControl.adjustContentToCurrentMapLayer();
            }
            */
        }
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
            d3.select('#'+this.pill.id)
                .transition()
                    .duration(750)
                    .style("opacity",0)
                    .remove();

        }    
    },
    addClearPillboxes: function(msg,data){

        //Compare our activated filterValues (from the state module) to the list of all 
        //possible filterControls to make a list containing only the activated filter objects. 
        //filterValues = obj with keys of the 'source' data id and values of current setpoint
        //filterControls = list of objects that encapsulates the actual component including its clear() method
        var activeFilterControls = []
        var filterValues = filterUtil.getFilterValues()
        for (var key in filterValues){
            // An 'empty' filterValues array has a single element,
            // the value of nullsShown.
            if (filterValues[key][0].length != 0){
                var control = filterView.filterControls.find(function(obj){
                    return obj['component']['source'] === key;
                })
                activeFilterControls.push(control)
            };
        }

        var nullsShown = filterUtil.getNullsShown();
        Object.keys(nullsShown).forEach(function(key){
            var control = filterView.filterControls.find(function(obj){
                return obj['component']['source'] === key;
            })
            // The default nullsShown value is 'true'. If it's different than the default,
            // and the control hasn't already been added to activeFilterControls,
            // add the data choice's associated control to the array that we're using
            // to determine which filters to mark as altered.
            if(nullsShown[key][0] === false && activeFilterControls.indexOf(control) === -1){
                activeFilterControls.push(control);
            }
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
                 
        allPills.exit()
        .transition()
            .duration(750)
            .style("opacity",0)
            .remove();

        
        
    },
    handleFilterClearance: function(message, data){
        if(data === true){
            filterView.clearAllButton.init();
        }
        if(data === false){
            filterView.clearAllButton.tearDown();
        }
    },
    resetZoneFilters: function(){
        for (var i=0; i < filterView.filterControls.length; i++) {
            var control = filterView.filterControls[i];
            if (control.component.data_level === 'zone') {
                control.rebuild();
            }  
        }
    },
    indicateActivatedFilters: function(){
        //add/remove classes to the on-page elements that tell the users which filters are currently activated
        //e.g. the filter sidebar data name titles
        var filterValues = filterUtil.getFilterValues();
        var nullsShown = filterUtil.getNullsShown();
        var filterStateIsActive = getState()['anyFilterActive'] && getState()['anyFilterActive'][0] == true;

        var activeNullsShownKeys = Object.keys(nullsShown).filter(function(key){
            return nullsShown[key][0] === false;
        })

        var activeFilterValuesKeys = Object.keys(filterValues).filter(function(key){
            return filterValues[key][0].length > 0;
        })

        var allActiveKeys = activeFilterValuesKeys.concat(activeNullsShownKeys);

        var noRemainingFilters = allActiveKeys.length === 0;

        Object.keys(filterValues).forEach(function(key){
            var activated = allActiveKeys.indexOf(key) !== -1
            d3.select('#filter-'+key)
                .classed("filter-activated",activated);
        });

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
