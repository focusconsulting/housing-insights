(function() { // wrapping script in immediately invoked function expression (IIFE, 'iffy') to contain scope
    'use strict'; // forcing good behavior 

    var Chart,
        MovingBlockChart,
        app,
        extendPrototype,

        SQUARE_WIDTH = 10, // symbolic constants all caps following convention
        SQUARE_SPACER = 2,
        ROWS = 12,
        DATA_FILE = 'https://raw.githubusercontent.com/codefordc/housing-insights/dev/scripts/small_data/PresCat_Export_20160401/Project.csv';

    extendPrototype = function(destinationPrototype, obj){ // using this function for inheritance. 
                                                           // extend a constructor's prototype with 
                                                           // the keys/values in obj. 
        for(var i in obj){
            destinationPrototype[i] = obj[i];
        }
    }
    
    Chart = function(el,field,sortField,asc) {

        this.initialSetup(el,field,sortField,asc); //on chart creation, we run setup function; setup function adds listeners for update chart behavior (e.g. resorting, etc.).

    };

    Chart.prototype = {
        initialSetup: function(el,field,sortField,asc) { // renamed from 'setup' to avoid clashes with
                                                         // child objects of Chart, which also use 'setup'. Can
                                                         // perhaps rename to 'setup' after changing the
                                                         // inheritance code.
            var chart = this // stashing `this` (Chart) into variable for access later within narrower scopes (like the scale functions)

            app.data.sort(function(a, b) { // sorting data array with JS prototype sort function
                if (asc) return a[sortField] - b[sortField]; // if asc parameter in Chart constructor call is true
                return b[sortField] - a[sortField]; // if not
              });  

            chart.svg = d3.select(el) // select elem (div#chart-0)
                .append('svg')        // append svg element 
                .attr('width', 100 + '%')   // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult
                .attr('height', 200); // SVG object dimensions are hard-coded now, but it may be 
                                      // useful to set these as, say, a parameter in constructors that
                                      // inherit from Chart.

            chart.minValue = d3.min(app.data, function(d) { // d3.min iterates through datums (d) and return the smallest
                return d[field]
            });

            chart.maxValue = d3.max(app.data, function(d) { // d3.max iterates through datums (d) and return the largest
                return d[field]
            });

            chart.scale = d3.scaleLinear().domain([chart.minValue, chart.maxValue]).range([0.1, 1]); // in v3 this was d3.scale.linear(). maps the values in the data (domain) to the output values you want (range)

        } // end setup()

    }; // end prototype
    
    MovingBlockChart = function(el, field, sortField, asc) {
        Chart.call(this, el, field, sortField, asc); // First step of inheriting from Chart
        this.setup(el, field, sortField, asc); 
    }
    
    MovingBlockChart.prototype = Object.create(Chart.prototype); // Second step of inheriting from Chart
    
    extendPrototype(MovingBlockChart.prototype, { // Final step of inheriting from Chart.
        setup: function(el, field, sortField, asc){
            var chart = this, 
                tool_tip = d3.tip()
                    .attr("class", "d3-tip")
                    .offset([-8, 0])
                    .direction('e')
                    .html(function(d){
                        return '<b>' + d.Proj_Name + '<br>' + d.Proj_Addre + '</b><br><br>Total units: ' + d.Proj_Units_Tot;  //here the text of the tooltip is hard coded in but we'll need a human-readable field in the data to provide that text
                      });
             
            chart.svg.selectAll('rect') // selects svg element `rect`s whether they exist yet or not          
                .data(app.data) // binds to data
                .enter() // for all `rect`s that don't yet exist
                .append('rect') // create the `rect`
                .attr('width', SQUARE_WIDTH)
                .attr('height', SQUARE_WIDTH)
                .attr('fill', '#325d88') // note svg-specific property names eg fill, not background
                .attr('fill-opacity', 0.1)                
                .on('mouseover', tool_tip.show) // .show is defined in links d3-tip library
                .on('mouseout', tool_tip.hide)  // .hide is defined in links d3-tip library
                .call(tool_tip);
         
            chart.positionBlocks(0);
            chart.changeOpacity(field);

            chart.buttonRand = d3.select(el) // creates the button to randomly resort and appends it in the el (div#chart-0)
                .append('button')
                .text('Resort randomly')
                .on('click', function(){
                    chart.resort('random');
                });

            chart.buttonZip = d3.select(el) // creates the button to randomly resort and appends it in the el (div#chart-0)
                .append('button')
                .text('Resort by zip')
                .on('click', function(){
                    chart.resort('zip');
                });

            chart.buttonUnit = d3.select(el) // creates the button to randomly resort and appends it in the el (div#chart-0)
                .append('button')
                .text('Resort by unit count')
                .on('click', function(){
                    chart.resort('unit');
                });

            chart.slider = d3.select(el)
                .append('input')
                .attr('type', 'range')
                .attr('id', 'inputSlider')
                .attr('step', '.01')      // .01 is kind of a magic number and probably should be made responsive to the data
                .style('margin-top', '1em') // these two style elements are pretty arbitrary
                .style('width', '40%');
                

            d3.select('#inputSlider')
                .attr('min', chart.minValue)
                .attr('max', chart.maxValue);

            chart.slider.on('mousedown', function(){ // this anonymous function wraps
                     chart.sliderAction(field);  // another function in order to pass a
                }, false);                      // parameter despite being an event listener

        },  // end setup()

        positionBlocks: function(duration){
                    
            this.svg.selectAll('rect')
                .transition().duration(duration)
                .attr('y', function(d, i) {
                    return (i * SQUARE_WIDTH + SQUARE_SPACER * i) - Math.floor(i / ROWS) * (SQUARE_WIDTH + SQUARE_SPACER) * ROWS;
                }) // horizontal placement is function of the index and the number of ROWS desired
                .attr('x', function(d, i) {
                    return Math.floor(i / ROWS) * SQUARE_WIDTH + (Math.floor(i / ROWS) * SQUARE_SPACER);
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

        resort: function(value){

            /* for demo purposes only. production tool will have many events that trigger update and 
             * (potentially) resort functions. probably best and easiest to eventually  use an observer pattern
             * or pub/sub (publish/subscribe) (same thing?) pattern to connect user- ot client-inititiated events (including resize)
             * with update functions
             */
            
          switch(value){ 
                
                case 'random':
                this.svg.selectAll('rect').sort(function(a,b){
                    return d3.ascending(Math.random(), Math.random());
                });
                break;

                case 'zip':
                this.svg.selectAll('rect').sort(function(a,b){
                    return d3.ascending(a.Proj_Zip, b.Proj_Zip);
                });
                break;

                case 'unit':
                this.svg.selectAll('rect').sort(function(a,b){
                    return d3.ascending(a.Proj_Units_Tot, b.Proj_Units_Tot);
                });
                break;
            }
            this.positionBlocks(500);

        }, // end resort()

        sliderAction: function(field){
                        document.querySelector('body').addEventListener('mousemove', checkColors, false);
                    
                        function checkColors() {
                            let value = document.querySelector('#inputSlider').value;
                            d3.selectAll('rect').attr('fill', function(d){
                              if(d[field] < value){
                                return 'gray';
                              } else {
                                return 'blue';
                              }
                            });

                            d3.select('body').on('mouseup', function(){
                                document.querySelector('body').removeEventListener('mousemove', checkColors);
                            }, false);
                        };  
        }       // end sliderAction()

    }); // end prototype

       
    
        
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
            console.log(app.data);
                        //params:(element    , field to visualize            ,  field to sort by         , ascending [boolean])   
            app.blockChart = new MovingBlockChart('#chart-0', 'Proj_Units_Tot', 'Proj_Zip', false);

        }
    }

    d3.csv(DATA_FILE, app.initialize); // ALL STARTS HERE

})(); // end IIFE