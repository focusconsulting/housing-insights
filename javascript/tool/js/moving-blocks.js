"use strict";

/*
 * This file is an example of how to build a constructor (a specific chart) that prototypically inherits from the shared Chart
 * constructor (in housing-insight.js). The MovingBlockChart constructor inherits all methods and properties defined in Chart
 * and add to its prototype the methods and properties specific to moving blocks.
 */

var SQUARE_WIDTH = 10, // symbolic constants all caps following convention
    SQUARE_SPACER = 2,
    ROWS = 12;


// NOTE: the first parameters of specific chart calls mirror those in the Chart constructor (now 1–6);
// parameters after tha can be additional
                                          
                               //   1      2    3         4       5       6       
var MovingBlockChart = function(DATA_FILE, el, field, sortField, asc, readableField, width, height) { 
        
        // extend prototype is a method of Chart, defined in housing-insights.js, which MovingBlockChart has inherited from
                              // param1 = what to extend      param2 = with what 
        this.extendPrototype(MovingBlockChart.prototype, movingBlockExtension); 
        console.log(width);

        this.width = width;   // for extra parameters to be available in the extended prototype, they have to set
        this.height = height; // as properties of `this`
        Chart.call(this, DATA_FILE, el, field, sortField, asc, readableField); 

                                                                                     // First step of inheriting from Chart.
                                                                                     // Call() calls a function. first param is
                                                                                     // the owner / context of the function
                                                                                     // (the `this`). "With call() or apply()
                                                                                     // you can set the value of this, and
                                                                                     // invoke a function as a new method of
                                                                                     // an existing object."
                                                                                     // https://www.w3schools.com/js/js_function_invocation.asp

    
  }

MovingBlockChart.prototype = Object.create(Chart.prototype); // Second step of inheriting from Chart. 

       


var movingBlockExtension = { // Final step of inheriting from Chart, defines the object with which to extend the prototype
                             // as called in this.extendPrototype(...) above
    setup: function(el, field, sortField, asc, readableField){
        var chart = this,

            data = chart.data // chart.data (this.data) is set in the Chart prototype, taken from app.dataCollection[xxxx] 

            var tool_tip = d3.tip()
                .attr("class", "d3-tip")
                .offset([-8, 0])
                .direction('e')
                .html(function(d){
                    return '<b>' + d.Proj_Name + '<br>' + d.Proj_Addre + '</b><br><br>' + readableField + ': ' + d[field];  //here the text of the tooltip is hard coded in but we'll need a human-readable field in the data to provide that text
                  });
                  console.log(data);

                  console.log(el);
                  console.log(chart.width);

        chart.svg = d3.select(el) 
                .append('svg')    
                .attr('width', chart.width) 
                .attr('height', chart.height); 
                                     
         
        chart.svg.selectAll('rect') 
            .data(data) 
            .enter() 
            .append('rect') 
            .attr('width', SQUARE_WIDTH)
            .attr('height', SQUARE_WIDTH)
            .attr('fill-opacity', 0.1)
            .on('mouseover', tool_tip.show) 
            .on('mouseout', tool_tip.hide)  
            .call(tool_tip);

        chart.scale = d3.scaleLinear().domain([chart.minValue, chart.maxValue]).range([0.1, 1]);
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
                chart.resort('Proj_Zip');
            });

        chart.buttonUnit = d3.select(el) // creates the button to randomly resort and appends it in the el (div#chart-0)
            .append('button')
            .text('Resort by value')
            .on('click', function(){
                chart.resort(field);
            });

        chart.slider = d3.select(el)
            .append('input')
            .attr('type', 'range')
            .attr('id', 'inputSlider')
            .attr('step', '.01')      
            .style('margin-top', '1em') 
            .style('width', '40%');


        d3.select('#inputSlider')
            .attr('min', chart.minValue)
            .attr('max', chart.maxValue);

        chart.slider.on('mousedown', function(){ // this anonymous function wraps
                 chart.sliderAction(field);  // another function in order to pass a
            }, false);                      // parameter despite being an event listener

    }, 

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
      .attr('fill-opacity', function(d, i, array) { 
          var value;
          if (isNaN(d[field])) { // some fields have NaN values and d3.sort was puuting them in the middle of the range
            value = 0;           // this sorts them as if their value was zero and also adds a null-value class to `rect`
                                 //  so that it can be styled appropriately
            array[i].setAttribute('class', 'null-value');
          } else {
            value = chart.scale(d[field]);
          }

          return value;

      })
      .attr('onclick', function(d){
        return 'location.href="./building.html?building=' + d.Proj_address_id + '"';
      }); 

    },

    resort: function(value){

        /* for demo purposes only. production tool will have many events that trigger update and
         * (potentially) resort functions. probably best and easiest to eventually  use an observer pattern
         * or pub/sub (publish/subscribe) (same thing?) pattern to connect user- ot client-inititiated events (including resize)
         * with update functions
         */
          var chart = this;
          console.log(value);

      if (value === 'random') {
        this.svg.selectAll('rect').sort(function(a, b){
                return d3.ascending(Math.random(), Math.random());
            });
      } else {
         this.svg.selectAll('rect').sort(function(a, b){
                var aProxy = (isNaN(a[value])) ? -1 : a[value];
                var bProxy = (isNaN(b[value])) ? -1 : b[value];
                return d3.ascending(aProxy, bProxy);
            });

      }

        this.positionBlocks(500);

    }, // end resort()

    sliderAction: function(field){
                    document.querySelector('body').addEventListener('mousemove', checkColors, false);

                    function checkColors(event) {
                        console.log(event);
                        let value = document.querySelector('#inputSlider').value;
                        d3.selectAll('rect').attr('class', function(d){
                          if(d[field] < value){ // threshold now sets class of `rect` rather than hard-coding in value
                            return 'under-threshold';
                          } else {
                            return '';
                          }
                        });

                        d3.select('body').on('mouseup', function(){
                            document.querySelector('body').removeEventListener('mousemove', checkColors);
                        }, false);
                    };
    }       // end sliderAction()

}; // end prototype

/*

 * Constructor calls below. 
 */

var DATA_FILE ='data/Project.csv';

// first Chart loads new data

                  // DATA_FILE,   el,          field,       sortField, asc, readableField, width, height
new MovingBlockChart(DATA_FILE,'#chart-0','Proj_Units_Tot','Proj_Zip',false,'Total Units','100%',200); 

// second constructor is in a timeout function to illustrate how a later chart can use an existing data object
// rather than fetch the data again. if called without the timeout, the data object would not be ready yet.
// only for illusttation: no harm would be done by calling it right away

                      
  window.setTimeout(function(){
                        // DATA_FILE,   el,          field,       sortField, asc, readableField, width, height
    new MovingBlockChart(DATA_FILE,'#chart-1','Proj_Units_Tot','Proj_Units_Tot',true,'Total Units','100%',200);
                                                                                             
  }, 1000);