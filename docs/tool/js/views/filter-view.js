"use strict";

var filterView = {
    
    components: [
        //TODO this hard coded array of objects is just a temporary method. 
        //This should be served from the API, probably from meta.json
        {   source: 'proj_units_tot',
            display_name: 'Project unit count',
            component_type: 'continuous',
            min: 5,
            max: 200,
            num_decimals_displayed: 0 //0 if integer, 1 otherwise. Could also store data type instead. 
        },
        {   source: 'proj_units_assist_max',
            display_name: 'Subsidized units',
            component_type: 'continuous',
            min: 0,
            max: 150,
            num_decimals_displayed: 0 //0 if integer, 1 otherwise. Could also store data type instead. 
        },
        {   source:'poa_start',
            component_type: 'date',
            min: '1950-01-01', //just example, TODO change to date format
            max: 'now'         //dummy example
        },
        {   source:'ward',
            component_type: 'categorical',
            other: 'feel free to add other needed properties if they make sense'
        }
    ],

    init: function() {
        
        //Add components to the navigation using the appropriate component type
        //TODO later we'll need to make sure this uses the appropriate order
        for (var i = 0; i < filterView.components.length; i++) {
            

            //Set up sliders
            if (filterView.components[i].component_type == 'continuous'){
                
                //TODO ES6 only, see comment in sliderMove for discussion
                //local scope alias. c is for component
                let c = filterView.components[i]
                
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

                //Publish changes to the StateModule
                function sliderMove ( values, handle, unencoded, tap, positions ) {
                    // This is the custom binding module used by the noUiSlider.on() callback. 

                    // values: Current slider values;
                    // handle: Handle that caused the event;
                    // unencoded: Slider values without formatting;
                    // tap: Event was caused by the user tapping the slider (boolean);
                    // positions: Left offset of the handles in relation to the slider

                    //TODO the challenge here is how do we get the property of which slider was actually called inside
                    //this sliderMove function itself?? We can't change method signature because it is defined
                    //by noUiSlider. Maybe we need a constructor to produce a copy of this function for each slider?
                    //If we go with ES6, using 'let' on the for loop will make the slider variable locally scoped 
                    //which solves the problem. Currently using this approach
                    //TODO are we doing only ES6 compatibility???
                    var specific_state_code = 'filterValues.' + c.source //ES6 only.... 
                    setState(specific_state_code,unencoded); 
                }

                //Using 'set' only updates on release. Probably better to use the 'update' method for continuous updates. 
                //using 'set' for now for easier development (less console logging of state changes)
                slider.noUiSlider.on('set', sliderMove);

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


    } //end init
};

console.log("loaded filter-view")
console.log(filterView)
