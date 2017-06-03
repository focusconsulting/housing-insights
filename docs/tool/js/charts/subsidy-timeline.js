"use strict"; 

var SubsidyTimelineChart = function(chartOptions) { 
                                                                                     // First step of inheriting from Chart.
                                                                                     // Call() calls a function. first param is
                                                                                     // the owner / context of the function
                                                                                     // (the `this`). "With call() or apply() 
                                                                                     // you can set the value of this, and 
                                                                                     // invoke a function as a new method of
                                                                                     // an existing object."
                                                                                     // https://www.w3schools.com/js/js_function_invocation.asp
        // extend prototype is a method of Chart, defined in housing-insights.js
                              // param1 = what to extend      param2 = with what
    this.extendPrototype(SubsidyTimelineChart.prototype, subsidyTimelineExtension);

    this.margin = {top: 20, right: 10, bottom: 40, left: 10};         // Since this chart uses axes, I implemented the D3 margin
    this.width = chartOptions.width - this.margin.left - this.margin.right;     // convention, which you may reference at https://bl.ocks.org/mbostock/3019563
    this.height = chartOptions.height - this.margin.top - this.margin.bottom; 

    this.building = getState()['selectedBuilding'][0]['properties'];
    this.initialize(chartOptions);    
};

SubsidyTimelineChart.prototype = Object.create(ChartProto.prototype); // Second step of inheriting from Chart. I can't remember why you
                                                             // have to use Object.create instead of just assignment (=), but
                                                             // you do 

var subsidyTimelineExtension = { // Final step of inheriting from Chart, defines the object with which to extend the prototype
                             // as called in this.extendPrototype(...) above 
    initialize: function(chartOptions) {

        var chart = this,
            data = model.dataCollection[chartOptions.dataRequest.name]['items'],
            groups; // the groups variable is used to draw a multi-part figure for each datum
            
        chart.svg = d3.select(chartOptions.container) // select elem (div#chart-0)
              .append('svg')        // append svg element 
                .attr('width', this.width + this.margin.left + this.margin.right)   // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult
                .attr('height', this.height + this.margin.top + this.margin.bottom) // continuation of d3 margin convention
              .append("g")
                .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");
        console.log("Just after chart.svg in subsidy-timeline.js");

        chart.minTime = d3.min(data, function(d){
          return chart.timeParser.toUTC(d['subsidy_start_first']);
        });
        console.log("Just after chart.minTime in subsidy-timeline.js");
        chart.maxTime = d3.max(data, function(d){
          return chart.timeParser.toUTC(d['subsidy_end_first']);
        });
        console.log("Just after chart.maxTime in subsidy-timeline.js");
        chart.xScale = d3.scaleTime()
                    .domain([new Date(chart.minTime), new Date(chart.maxTime)]).range([0, .9 * this.width]);
        console.log("Just after chart.xScale in subsidy-timeline.js");
        chart.yScale = function(i){
              return this.height/data.length * i + 10;
          }; // There is probably a default d3 scale that accomplishes this, but it was simple enough
              // that I didn't want to spend the time to dig through the docs. You are welcome to
              // find it and replace this.

        groups = chart.svg.selectAll('g')
              .data(data)
              .enter()
              .append('g');
        console.log("Just after chart.svg.selectAll('g') in subsidy-timeline.js");
     
        groups.append('line')
              .attr('x1', function(d){
                console.log("d['subsidy_start_first']", d['subsidy_start_first']);
                return chart.xScale(new Date(chart.timeParser.toUTC(d['subsidy_start_first'])));
              })
              .attr('x2', function(d){
                return chart.xScale(new Date(chart.timeParser.toUTC(d['subsidy_end_first'])));
              })
              .attr('y1', function(d, i){
                return chart.yScale(i);
              })
              .attr('y2', function(d, i){
                return chart.yScale(i);
              })
              .style('stroke', 'black');
        console.log("Just after groups.append('line') in subsidy-timeline.js");

        groups.append('text')
              .attr('x', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['subsidy_end_first'])) + 3;
              })
              .attr('y', function(d,i){
                return chart.yScale(i) + 5;
              })
              .text(function(d){
                return chart.timeParser.year(d['subsidy_end_first']);
              })
              .style('fill', '#999999');
        console.log("Just after groups.append('text'), first call, in subsidy-timeline.js");

        groups.append('text')
              .attr('x', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['subsidy_end_first']))-15;
              })
              .attr('y', function(d,i){
                return chart.yScale(i) - 4;
              })
              .text(function(d){
                return d['program'];
              })
              .attr('text-anchor','end');
        console.log("Just after groups.append('text'), second call, in subsidy-timeline.js");

        groups.append('text')
              .attr('x', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['subsidy_end_first'])) - 15;
              })
              .attr('y', function(d,i){
                return chart.yScale(i) + 16;
              })
              .text(function(d){
                return "Subsidized units: " + d['proj_units_assist_min'];
              })
              .attr('fill','gray')
              .attr('text-anchor','end');        
        console.log("Just after groups.append('text'), third call, in subsidy-timeline.js");

        // the following three sections are decorative

        groups.append('circle')
              .attr('cx', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['subsidy_start_first']));
              })
              .attr('cy', function(d,i){
                return chart.yScale(i);
              })
              .attr('r', 3)
              .style('fill', 'black');
        console.log("Just after groups.append('circle') in subsidy-timeline.js");

        groups.append('polygon')
              .attr('points', function(d, i){
                let x2 = chart.xScale(chart.timeParser.parsedDate(d['subsidy_end_first'])),
                    x1 = x2 - 7,
                    y2 = chart.yScale(i),
                    y1 = y2 + 5,
                    y3 = y2 - 5;
                return `${x1},${y1} ${x2},${y2} ${x1},${y3}`
              })
              .style('stroke', 'black')
              .style('fill', 'black');
        console.log("Just after groups.append('polygon') in subsidy-timeline.js");

        groups.append('line')
              .attr('x1', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['subsidy_end_first']));
              })
              .attr('x2', function(d){
                return chart.xScale(chart.timeParser.parsedDate(d['subsidy_end_first']));
              })
              .attr('y1', function(d,i){
                return chart.yScale(i) - 7;
              })
              .attr('y2', function(d,i){
                return chart.yScale(i) + 7;
              })
              .style('stroke', 'black');
        console.log("Just after groups.append('line') in subsidy-timeline.js");

        chart.svg.append('g')
                  .attr("transform", "translate(0," + this.height + ")")
                  .call(d3.axisBottom(chart.xScale))
                  .style('stroke', 'black');
        console.log("Just after chart.svg.append('g'), around line 169, in subsidy-timeline.js");

        chart.svg.append('line')
                  .attr('x1', chart.xScale(new Date()))
                  .attr('x2', chart.xScale(new Date()))
                  .attr('y1', 0)
                  .attr('y2', this.height + 20)
                  .style('stroke', 'rgba(0,0,0,.4)')
                  .style('stroke-width', 4);
        console.log("Just after chart.svg.append('line'), around line 178, in subsidy-timeline.js");

        chart.svg.append('text')
                  .attr('x', chart.xScale(new Date()) - 15)
                  .attr('y', this.height + 35)
                  .text('Today');
        console.log("Just after chart.svg.append('text'), around line 184, in subsidy-timeline.js");
      }, // end setup

      timeParser: {   // This is very data format dependent, and will need to be replaced when we have
                      // a final data format

                      // PG: currently working with Strings of the format '0000-00-00'.
    
        month: function(string) {
          return +string.substr(5, 2);
        },
        day: function(string){
          return +string.substr(8, 2);
        },
        year: function(string){
          //TODO this is a super hacky way to deal with these null values that will need to change when we switch to API
          if(string === null || string === 'N' || string === '' || string === 0){
            return '2017'
          };
         return +string.substr(0, 4);
        },
        toUTC: function(string){
          console.log("Argument for toUTC", string);
          //TODO this is a super hacky way to deal with these null values that will need to change when we switch to API
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
