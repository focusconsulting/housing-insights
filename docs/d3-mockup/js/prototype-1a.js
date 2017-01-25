(function() { // wrapping script in immediately invoked function expression (IIFE, 'iffy') to contain scope
    'use strict'; // forcing good behavior 

    var Chart,
        app,

        SQUARE_WIDTH = 10, // symbolic constants all caps following convention. removing from options object below
        SQUARE_SPACER = 2,
        COLUMNS = 7,
        DATA_FILE = 'https://raw.githubusercontent.com/codefordc/housing-insights/dev/scripts/small_data/Neighborhood_Profiles/nc_housing.csv';

    Chart = function(el,field,sortField,asc) {
        this.setup(el,field,sortField,asc);
        //this.update();  placeholder
        //this.resize();  placeholder
    };

    Chart.prototype = {
        setup: function(el,field,sortField,asc) {
            var chart = this,
                tool_tip = d3.tip()
                  .attr("class", "d3-tip")
                  .offset([-8, 0])
                  .direction('e')
                  .html(function(d){
                      return "Percentage of vacant housing units for rent: " + d[field];
                    });
                //here the text of the tooltip is hard coded in but we'll need a human-readable field in the data to provide that text
                
              
            app.data.sort(function(a, b) { //sorting with JS prototype sort function
                if (asc) return a[sortField] - b[sortField]; // if options abov was to sort ascending
                return b[sortField] - a[sortField]; // if not
              }); 

            chart.svg = d3.select(el)
                .attr('width', 100)
                .attr('height', 100); // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult

            chart.minValue = d3.min(app.data, function(d) {
                return d[field]
            });

            chart.maxValue = d3.max(app.data, function(d) {
                return d[field]
            });

            chart.scale = d3.scaleLinear().domain([chart.minValue, chart.maxValue]).range([0.1, 1]); // in v3 this was d3.scale.linear()
            chart.svg.selectAll('rect')
                .data(app.data)
                .enter() // for all `rect`s that don't yet exist
                .append('rect')
                .attr('width', SQUARE_WIDTH)
                .attr('height', SQUARE_WIDTH)
                .attr('fill', '#325d88')
                .attr('fill-opacity', function(d) { // fill-opacity is a function of the value
                    return chart.scale(d[field]); // takes the field value and maps it according to the scaling function defined above
                })
                .attr('x', function(d, i) {
                    return (i * SQUARE_WIDTH + SQUARE_SPACER * i) - Math.floor(i / COLUMNS) * (SQUARE_WIDTH + SQUARE_SPACER) * COLUMNS;
                }) // horizontal placement is function of the index and the number of columns desired
                .attr('y', function(d, i) {
                    return Math.floor(i / COLUMNS) * SQUARE_WIDTH + (Math.floor(i / COLUMNS) * SQUARE_SPACER);
                }) // vertical placement function of index and number of columns. Math.floor rounds down to nearest integer
                .on('mouseover', tool_tip.show)
                .on('mouseout', tool_tip.hide)
                .call(tool_tip);


                  
                

        }// end setup()
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

    d3.csv(DATA_FILE, app.initialize);

})(); // end IIFE