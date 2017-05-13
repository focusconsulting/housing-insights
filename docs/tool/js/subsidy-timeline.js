"use strict"; 


// I added the building variable to take the NLIHC id. This should be changed to our standard way of accepting that.
var SubsidyTimelineChart = function(DATA_FILE, dataName, el, field, sortField, asc, readableField, width, height, building) { 
    Chart.call(this, DATA_FILE, dataName, el, field, sortField, asc, readableField, width, height, building); 
                                                                                     // First step of inheriting from Chart.
                                                                                     // Call() calls a function. first param is
                                                                                     // the owner / context of the function
                                                                                     // (the `this`). "With call() or apply() 
                                                                                     // you can set the value of this, and 
                                                                                     // invoke a function as a new method of
                                                                                     // an existing object."
                                                                                     // https://www.w3schools.com/js/js_function_invocation.asp
        // extend prototype is a method of Chart, defined in housing-insights.js, which MovingBlockChart has inherited from
                              // param1 = what to extend      param2 = with what
        this.extendPrototype(SubsidyTimelineChart.prototype, subsidyTimelineExtension);
        this.margin = {top: 20, right: 10, bottom: 40, left: 10};         // Since this chart uses axes, I implemented the D3 margin
        this.width = width - this.margin.left - this.margin.right;     // convention, which you may reference at https://bl.ocks.org/mbostock/3019563
        this.height = height - this.margin.top - this.margin.bottom; 
        this.building = building;
 

        
    
  };

SubsidyTimelineChart.prototype = Object.create(Chart.prototype); // Second step of inheriting from Chart. I can't remember why you
                                                             // have to use Object.create instead of just assignment (=), but
                                                             // you do 

var subsidyTimelineExtension = { // Final step of inheriting from Chart, defines the object with which to extend the prototype
                             // as called in this.extendPrototype(...) above 
    setup: function(dataName, el, field, sortField, asc, readableField) {

        var chart = this,
            data = chart.data.filter(function(d){ return d['nlihc_id'] === chart.building}),
                              // the filter here removes data for all other buildings using the building parameter
            groups; // the groups variable is used to draw a multi-part figure for each datum
        console.log(this.width, this.margin.left, this.margin.right);
        console.log(el);
        chart.svg = d3.select(el) // select elem (div#chart-0)
              .append('svg')        // append svg element 
                .attr('width', this.width + this.margin.left + this.margin.right)   // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult
                .attr('height', this.height + this.margin.top + this.margin.bottom) // continuation of d3 margin convention
              .append("g")
                .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

        console.log(chart['data']);
        console.log(data);


        chart.minTime = d3.min(data, function(d){
          return chart.timeParser.toUTC(d['poa_start']);
        });
        chart.maxTime = d3.max(data, function(d){
          return chart.timeParser.toUTC(d['poa_end']);
        });
        chart.xScale = d3.scaleTime()
                    .domain([new Date(chart.minTime), new Date(chart.maxTime)]).range([0, .9 * this.width]);
        chart.yScale = function(i){
              return this.height/data.length * i + 10;
          }; // There is probably a default d3 scale that accomplishes this, but it was simple enough
              // that I didn't want to spend the time to dig through the docs. You are welcome to
              // find it and replace this.


        groups = chart.svg.selectAll('g')
              .data(data)
              .enter()
              .append('g');

     
        groups.append('line')
              .attr('x1', function(d){
                return chart.xScale(new Date(chart.timeParser.toUTC(d['poa_start'])));
              })
              .attr('x2', function(d){
                return chart.xScale(new Date(chart.timeParser.toUTC(d['poa_end'])));
              })
              .attr('y1', function(d, i){
                return chart.yScale(i);
              })
              .attr('y2', function(d, i){
                return chart.yScale(i);
              })
              .style('stroke', 'black');

        groups.append('text')
              .attr('x', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['poa_end'])) + 3;
              })
              .attr('y', function(d,i){
                return chart.yScale(i) + 5;
              })
              .text(function(d){
                return chart.timeParser.year(d['poa_end']);
              })
              .style('fill', '#999999');

        groups.append('text')
              .attr('x', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['poa_end']))-15;
              })
              .attr('y', function(d,i){
                return chart.yScale(i) - 4;
              })
              .text(function(d){
                return d['program'];
              })
              .attr('text-anchor','end');

        groups.append('text')
              .attr('x', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['poa_end'])) - 15;
              })
              .attr('y', function(d,i){
                return chart.yScale(i) + 16;
              })
              .text(function(d){
                return "Subsidized units: " + d['units_assist'];
              })
              .attr('fill','gray')
              .attr('text-anchor','end');        

        // the following three sections are decorative

        groups.append('circle')
              .attr('cx', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['poa_start']));
              })
              .attr('cy', function(d,i){
                return chart.yScale(i);
              })
              .attr('r', 3)
              .style('fill', 'black');

        groups.append('polygon')
              .attr('points', function(d, i){
                let x2 = chart.xScale(chart.timeParser.parsedDate(d['poa_end'])),
                    x1 = x2 - 7,
                    y2 = chart.yScale(i),
                    y1 = y2 + 5,
                    y3 = y2 - 5;
                return `${x1},${y1} ${x2},${y2} ${x1},${y3}`
              })
              .style('stroke', 'black')
              .style('fill', 'black');

        groups.append('line')
              .attr('x1', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['poa_end']));
              })
              .attr('x2', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['poa_end']));
              })
              .attr('y1', function(d,i){
                return chart.yScale(i) - 7;
              })
              .attr('y2', function(d,i){
                return chart.yScale(i) + 7;
              })
              .style('stroke', 'black');

        chart.svg.append('g')
                  .attr("transform", "translate(0," + this.height + ")")
                  .call(d3.axisBottom(chart.xScale))
                  .style('stroke', 'black');

        chart.svg.append('line')
                  .attr('x1', chart.xScale(new Date()))
                  .attr('x2', chart.xScale(new Date()))
                  .attr('y1', 0)
                  .attr('y2', this.height + 20)
                  .style('stroke', 'rgba(0,0,0,.4)')
                  .style('stroke-width', 4);

        chart.svg.append('text')
                  .attr('x', chart.xScale(new Date()) - 15)
                  .attr('y', this.height + 35)
                  .text('Today');
      }, // end setup

      timeParser: {   // This is very data format dependent, and will need to be replaced when we have
                      // a final data format
    
        month: function(string) {
          return +string.substr(5, 2);
        },
        day: function(string){
          return +string.substr(8, 2);
        },
        year: function(string){
          //TODO this is a super hacky way to deal with these null values that will need to change when we switch to API
          if(string === 'N' || string === '' || string === 0){
            return '2017'
          };
         return +string.substr(0, 4);
        },
        toUTC: function(string){
          //TODO this is a super hacky way to deal with these null values that will need to change when we switch to API
          console.log(string);
          if(string === 'N' || string === '' || string === 0){
            return Date.UTC('2017','04','17')
          };
          if(typeof(string) === 'string'){
            return Date.UTC(this.year(string), this.month(string), this.day(string));
          };
        },
        parsedDate: function(string){
          return new Date(this.toUTC(string));
        }
        

      } // end timeParser


}; // end prototype

/*
 * Constructor calls below. First done inline; second only when the data from the first is available, using PubSub module 
 */

var DATA_FILE = './data/Subsidy.csv';
console.log(subsidyTimelineExtension);

buildingID =  app.getParameterByName('building') 
// first Chart loads new data
new SubsidyTimelineChart(DATA_FILE,'projectCSV','#subsidy-timeline-chart','Proj_Units_Tot','Proj_Zip',false,'Total Units',1000,300,buildingID); 

// second chart uses the same data as first. its constructor is wrapped in a function subscribed
// to the publishing of the data being loaded. using this pattern, we can have several charts on a 
// page based on the same data


/* EXAMPLE OF HOW TO CALL SUBSEQUENT CHART BASED ON SAME DATE AS ANOTHER */

// wrapper function.the name doesn't matter; it just needs to be echoed below in the PubSu.subscribe method

// function subscriber1( msg, data ){ // for now the subscribed function directly calls the Chart constructor but
//                                           // in future we could have it look for all constructors waiting to be called,
//                                           // defined elsewhere
//     console.log( msg, data );
//     new MovingBlockChart(null,'projectCSV','#chart-1','Proj_Units_Tot','Proj_Units_Tot',true,'Total Units','100%',200);
//                                                                                              // second Chart uses same data 
//                                                                                              // as first. Needs to wait until
//                                                                                              // that data is loaded before being
//                                                                                              // initiated.

// };

// add the function to the list of subscribers for a particular topic (projectCSV/load in this case)
// we're keeping the returned token, in order to be able to unsubscribe
// from the topic later on (probably not necessary for us, not yet at least)
// var token = PubSub.subscribe( 'projectCSV/load', subscriber1 );
