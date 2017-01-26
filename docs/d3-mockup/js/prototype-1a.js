(function() { // wrapping script in immediately invoked function expression (IIFE, 'iffy') to contain scope
    'use strict'; // forcing good behavior 

    var Chart,
        app,

        SQUARE_WIDTH = 10, // symbolic constants all caps following convention. removing from options object below. options may change
        SQUARE_SPACER = 2,
        COLUMNS = 7,
        DATA_FILE = 'https://raw.githubusercontent.com/codefordc/housing-insights/dev/scripts/small_data/Neighborhood_Profiles/nc_housing.csv';

    Chart = function(el,field,sortField,asc) {
        this.setup(el,field,sortField,asc);
    };

    Chart.prototype = {
        setup: function(el,field,sortField,asc) {
            var chart = this, // stashing `this` (Chart) into variable for access later within narrower scopes (like the scale functions)
                tool_tip = d3.tip()
                  .attr("class", "d3-tip")
                  .offset([-8, 0])
                  .direction('e')
                  .html(function(d){
                      return "Percentage of vacant housing units for rent: " + d[field];  //here the text of the tooltip is hard coded in but we'll need a human-readable field in the data to provide that text
                    });

            app.data.sort(function(a, b) { // sorting data array with JS prototype sort function
                if (asc) return a[sortField] - b[sortField]; // if asc parameter in Chart constructor call is true
                return b[sortField] - a[sortField]; // if not
              });  

            chart.svg = d3.select(el) // select elem (div#chart-0)
                .append('svg')        // append svg element 
                .attr('width', 100)   // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult
                .attr('height', 100);
                

            chart.minValue = d3.min(app.data, function(d) { // d3.min iterates through datums (d) and return the smallest
                return d[field]
            });

            chart.maxValue = d3.max(app.data, function(d) { // d3.max iterates through datums (d) and return the largest
                return d[field]
            });

            chart.scale = d3.scaleLinear().domain([chart.minValue, chart.maxValue]).range([0.1, 1]); // in v3 this was d3.scale.linear(). maps the values in the data (domain) to the output values you want (range)
            
            chart.svg.selectAll('rect') // selects svg element `rect`s whether they exist yet or not          
                .data(app.data) // binds to data
                .enter() // for all `rect`s that don't yet exist
                .append('rect') // create the `rect`
                .attr('width', SQUARE_WIDTH)
                .attr('height', SQUARE_WIDTH)
                .attr('fill', '#325d88') // note svg-specific propert names eg fill, not background
                .attr('fill-opacity', 0.1)                
                .on('mouseover', tool_tip.show) // .show is defined in links d3-tip library
                .on('mouseout', tool_tip.hide)  // .hide is defined in links d3-tip library
                .call(tool_tip);
             
            chart.positionBlocks(0);
            chart.changeOpacity(field);

             chart.button = d3.select(el) // creates the button to randomly resort and appends it in the el (div#chart-0)
                .append('button')
                .text('Resort randomly')
                .on('click', function(){
                    chart.resort();
                });
        },  // end setup()

        positionBlocks: function(duration){
                       
             this.svg.selectAll('rect')
                .transition().duration(duration)
                .attr('x', function(d, i) {
                    return (i * SQUARE_WIDTH + SQUARE_SPACER * i) - Math.floor(i / COLUMNS) * (SQUARE_WIDTH + SQUARE_SPACER) * COLUMNS;
                }) // horizontal placement is function of the index and the number of columns desired
                .attr('y', function(d, i) {
                    return Math.floor(i / COLUMNS) * SQUARE_WIDTH + (Math.floor(i / COLUMNS) * SQUARE_SPACER);
                }) // vertical placement function of index and number of columns. Math.floor rounds down to nearest integer
        }, // end positionBlocks

        changeOpacity: function(field){
            var chart = this;
            chart.svg.selectAll('rect')
            
            .transition().delay(250).duration(750)
            .attr('fill-opacity', function(d) { // opacity is a function of the value
                    return chart.scale(d[field]); // takes the field value and maps it according to the scaling function defined above
                }) 
        },

        resort: function(){
            
            this.svg.selectAll('rect').sort(function(a,b){
                return d3.ascending(Math.random(), Math.random());
            });
            this.positionBlocks(500);
        } // end resort()
    }; // end prototype

    app = {
        data: [],
        initialize: function(json) {
            json.forEach(function(obj) { //iterate over each object of the data array
                for (var key in obj) { // iterate over each property of the object
                    if (obj.hasOwnProperty(key)) {
                        obj[key] = isNaN(+obj[key]) ? obj[key] : +obj[key]; // + operator converts to number unless result would be NaN
                    }
                }
            });
            app.data = json;
                        //params:(element    , field to visualize            ,  field to sort by         , ascending [boolean])   
            app.chart = new Chart('#chart-0', 'PctVacantHsgUnitsForRent_2000', 'NumOccupiedHsgUnits_2010', false);

        }
    }

    d3.csv(DATA_FILE, app.initialize); // ALL STARTS HERE

})(); // end IIFE