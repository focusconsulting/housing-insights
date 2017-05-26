"use strict";

var filterView = {
    
    components: [
        //TODO this hard coded array of objects is just a temporary method. 
        //This should be served from the API, probably from meta.json
        //"source" is the column name from the filter table, which should match the table in the original database table. 
        //  For this approach to work, it will be cleanest if we never have duplicate column names in our sql tables unless the data has
        //  the same meaning in both places (e.g. 'ward' and 'ward' can appear in two tables but should have same name/format)

        {   source: 'proj_units_tot',
            display_name: 'Project unit count',
            component_type: 'continuous',
            data_type:'integer',
            min: 5,
            max: 200,
            num_decimals_displayed: 0 //0 if integer, 1 otherwise. Could also store data type instead. 
        },
        {   source: 'acs_rent_median',
            display_name: 'Neighborhood Rent (ACS median)',
            component_type: 'continuous',
            data_type:'decimal',
            min: 0,
            max: 2500,
            num_decimals_displayed: 0 //0 if integer, 1 otherwise. Could also store data type instead. 
        },
        {   source:'poa_start',
            component_type: 'date',
            data_type: 'timestamp',
            min: '1950-01-01', //just example, TODO change to date format
            max: 'now'         //dummy example
        },
        {   source:'ward',
            component_type: 'categorical',
            data_type: 'text',
            other: 'feel free to add other needed properties if they make sense'
        }
    ],

    init: function() {
        
        //Make sure other functionality is hooked up
        setSubs([
            ['filterViewLoaded', filterUtil.init]
        ]);

        document.querySelectorAll('.sidebar-tab').forEach(function(tab){
            tab.onclick = filterView.toggleSidebar;
        });
        //Add components to the navigation using the appropriate component type
        //TODO later we'll need to make sure this uses the appropriate order
        for (var i = 0; i < filterView.components.length; i++) {
            

            //Set up sliders
            if (filterView.components[i].component_type == 'continuous'){
                
                var c = filterView.components[i]
                
                console.log("Found a continuous source!");

                var parent = d3.select('#filter-components')
                    .append("div")
                      .attr("class","filter-group");
                parent.append("p")
                  .attr("class","filter-label")
                  .text(c.display_name);
                parent.append("div")
                  .attr("id",c.source)
                  .attr("class","filter")
                  .attr("class","slider");

                
                var slider = document.getElementById(c.source);
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
                        setState(specific_state_code,unencoded); 
                    }
                }

                //Construct a new copy of the function with access to the current c variable
                var currentSliderCallback = makeSliderCallback(c)

                //Using 'set' only updates on release. Probably better to use the 'update' method for continuous updates. 
                //using 'set' for now for easier development (less console logging of state changes)
                slider.noUiSlider.on('set', currentSliderCallback);

            };//end slider setup


            //set up categorical pickers
            if (filterView.components[i].component_type == 'categorical'){
                console.log("Found a categorical filter! (need code to add this element)")
                //Add a div with label and select element
                //Bind user changes to a setState function
            };


            //set up date pickers
            if (filterView.components[i].component_type == 'date'){
                console.log("Found a date filter! (need code to add this element)")
                //Add a div with label and select element
                //Bind user changes to a setState function
            };

        }; //end for loop. All components on page.


        //After all filter components are loaded, user is allowed to filter data
        setState('filterViewLoaded',true);

    }, //end init
    toggleSidebar: function(e){
        var sBar = e.currentTarget.parentElement;
        sBar.classList.toggle('active'); // not supported in lte ie9
        sBar.querySelector('.triangle-left').classList.toggle('right');
    }
};

