
var url = 'data/crime_by_ward_demo.json'

function ColumnChart(selection){
    //Set up defaults
    var margin = {top: 20, right: 20, bottom: 20, left: 20},
      width = 760,
      height = 120,
      xValue = function(d) { return d[0]; },
      yValue = function(d) { return d[1]; },
      barGap = 2

    function chart(selection) {
        console.log('time to make a chart');
        selection.each(function(data) {

            var min = d3.min(data, function(d) { return d['count'];})
            var max = d3.max(data,function(d) {return d['count']})

            //calculated settings
            var innerHeight = (height - margin.top - margin.bottom)
            var innerWidth = (width - margin.left - margin.right)

            //TODO look up how to use ordinal scale
            var barThickness = (innerHeight / data.length) - barGap
            console.log(data.length)

            //todo currently not used
            var y = d3.scaleBand()
                    .domain(data)
                    .range([innerHeight,0])

            var x = d3.scaleLinear()
                    .domain([0,max])
                    .range([0,innerWidth])

            //Make the graph
            var svg = d3.select(this).append('svg')
                .attr("width",width)
                .attr("height",height);

            var innerChart = svg.append('g')
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            var bars = innerChart.selectAll('rect')
                .data(data)

            bars.attr("class","update")

            newBars = bars.enter().append('rect')
                .attr("x", 0)
                .attr("y", function(d,i) {return i * (barThickness + barGap)})
                .attr("width", function(d) { return x(d.count);})
                .attr("height", barThickness)
                

            allBars = newBars.merge(bars)

            leavingBars = bars.exit().remove()

        })
    }

    //Custom getter/setters to allow method chaining
    chart.container = function(_) {
        if (!arguments.length) return container;
        container = _;
        return chart;
    }
    chart.data = function(_) {
        if (!arguments.length) return data;
        data = _;
        return chart;
    }
    chart.width = function(_){
        if (!arguments.length) return width;
        width = _;
        return chart;
    }
    chart.height = function(_){
        if (!arguments.length) return height;
        height = _;
        return chart;
    }

    return chart;
}


//Do a demo of the chart
var apiData = {
  "data_id": "ward", 
  "grouping": "ward", 
  "items": [
    {"count": 124, "group": "Ward 1"}, 
    {"count": 112, "group": "Ward 2"}, 
    {"count": 12,"group": "Ward 3"}, 
    {"count": 110,"group": "Ward 4"}, 
    {"count": 157,"group": "Ward 5"}, 
    {"count": 122,"group": "Ward 6"}, 
    {"count": 291,"group": "Ward 7"}, 
    {"count": 229,"group": "Ward 8"}
  ]
}

var demoChart = ColumnChart()
        .width(800)
        .height(200)


d3.select('.mychart')
    .datum(apiData['items'])
    .call(demoChart);



/*
initialize: function(chartOptions) {
      chartOptions.dataRequest.callback = chartCallback; 
  }
*/