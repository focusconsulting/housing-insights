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
            display_name: 'Ward',
            component_type: 'categorical',
            data_type: 'text',
            other: 'feel free to add other needed properties if they make sense',
            options: ["Ward 1", "Ward 2", "Ward 3", "Ward 4", "Ward 5", "Ward 6", "Ward 7", "Ward 8"]
        }
    ],

    init: function() {

        //Make sure other functionality is hooked up
        setSubs([
            ['filterViewLoaded', filterUtil.init],
            ['sidebar', filterView.toggleSidebar],
            ['subNav', filterView.toggleSubNavButtons]



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
                if ( getState()['sidebar.' + leftRight] && getState()['sidebar.' + leftRight][0] ) { // if the accociated sidebar is open
                    if (getState()['subNav.' + leftRight][0] === subNavType) { // if the clicked subNav button is already active
                        setState('sidebar.' + leftRight, false); // close the sidebar
                    }
                } else {
                    setState('sidebar.' + leftRight, true); // open the sidebar
                }
                setState('subNav.' + leftRight, subNavType);
               /* console.log('click');
                var leftRight = e.currentTarget.parentElement.id.replace('-options','');
                console.log(leftRight);
                var sideBarMsg = 'sidebar.' + leftRight;
                var subButton = e.currentTarget.id.replace('button-','');
                console.log(subButton);
                if (getState()[sideBarMsg] && getState()[sideBarMsg][0])  { // if the associated sidebar is open
                    if (getState()['subNav.' + leftRight] && getState()['subNav.' + leftRight][0] === e.currentTarget.id){
                        filterView.toggleSidebarState(sideBarMsg);
                        setState('subNav.' + leftRight, e.currentTarget.id);
                    } else {
                        setState('subNav.' + leftRight, 'none');
                    }

                }*/
            }
        });
        //Add components to the navigation using the appropriate component type
        //TODO later we'll need to make sure this uses the appropriate order
        for (var i = 0; i < filterView.components.length; i++) {


            //Set up sliders
            if (filterView.components[i].component_type == 'continuous'){

              var c = filterView.components[i]
              console.log(c)
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

              var c = filterView.components[i];
              console.log(c)
                console.log("Found a categorical filter! (need code to add this element)")
                //Add a div with label and select element
                //Bind user changes to a setState function

                var parent = d3.select('#filter-components')
                    .append("div")
                      .attr("class","filter-group");
                parent.append("p")
                  .attr("class","filter-label")
                  .text(c.display_name);
                var selector = parent.append("div")
                  .attr("id",c.source)
                  .attr("class","filter")
                  .attr("class","categorical");
                var uiSelector = selector.append("select")
                  .attr("class", "ui fluid search dropdown")
                  .attr("multiple", " ")
                  .attr("id", "select");

                for(var i = 0; i < c.options.length; i++){
                  uiSelector.append("option").attr("value", c.options[i]).text(c.options[i])
                  var select = document.getElementById(c.source);
                }
                $('.ui.dropdown')
                .dropdown()
                ;
                $('#select')
                .dropdown()
                ;
                $("select").change(function(){
                  var selectedValues = [];
                  $("option:selected").each(function(){
                    selectedValues.push($(this).val());
                  });
                  console.log(selectedValues);
                  return false;
  })
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
    toggleSidebar: function(msg,data){
        console.log('toggleSidebar');
        var sBar = document.getElementById(msg.replace('.','-'));
        var leftRight = msg.indexOf('left') !== -1 ? 'left' : 'right';
        console.log(leftRight);
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
        console.log(data);
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
