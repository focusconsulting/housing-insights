
var url = 'data/crime_by_ward_demo.json'

function ColumnChart(selection){
    //Set up defaults
    var margin = {top: 20, right: 20, bottom: 20, left: 50},
      width = 760,
      height = 120,
      xValue = function(d) { return d[0]; },
      yValue = function(d) { return d[1]; },
      barPadding = 0.1

      //Stuff created in chart() moved up to this scope
      svg = null
      innerChart = null
      x = null
      y = null

    function chart(selection) {
        selection.each(function(data) {
            
            //Make the graph
            svg = d3.select(this).append('svg')
                .attr("width",width)
                .attr("height",height);

            innerChart = svg.append('g')
                .classed("column-chart",true)
                .attr("transform", "translate(" + margin.left + "," + 0 + ")");

            chart.update(data)
        })
    }
    chart.update = function(data) {
        console.log("yay update!")
        console.log(data)
        var min = d3.min(data, function(d) { return d['matching'] /  d['total'];})
            var max = d3.max(data,function(d) {return d['matching'] /  d['total']})

            var y = d3.scaleBand()
                    .domain(data.map(function(d) { return d.group; }))
                    .range([chart.innerHeight(),0])
                    .padding(barPadding)

            var x = d3.scaleLinear()
                    .domain([0,1]) //alternative use max. This sets to 100%
                    .range([0,chart.innerWidth()])


            //Actual quantity bars
            var bars = innerChart.selectAll('rect.percent')
                .data(data)
                //Anything that only happens to existing bars
                bars.classed("update",true)

                newBars = bars.enter().append('rect')
                    .classed("percent", true)
                    .attr("x", 0)
                    .attr("y", function(d,i) {return y(d.group)})
                    .attr("width", function(d) { 
                        return x(d.matching / d.total);})
                    .attr("height", y.bandwidth())
                    
                //Finish the update pattern
                allBars = newBars.merge(bars)
                leavingBars = bars.exit().remove()

            //Rest of the percent bars
            var bars = innerChart.selectAll('rect.filler')
                .data(data)
                //Anything that only happens to existing bars
                bars.classed("update",true)

                newBars = bars.enter().append('rect')
                    .classed("filler",true)
                    .attr("x", function(d) { return x(d.matching / d.total);})
                    .attr("y", function(d,i) {return y(d.group)})
                    .attr("width", function(d) { 
                        return x((d.total - d.matching) / d.total);})
                    .attr("height", y.bandwidth())
                    
                //Finish the update pattern
                allBars = newBars.merge(bars)
                leavingBars = bars.exit().remove()


            // add the x Axis
            var xAxis = d3.axisBottom(x)
                        .tickFormat(d3.format(".0%"))
                        .ticks(5)

            svg.append("g")
              .attr("transform", "translate(" + margin.left + "," + chart.innerHeight() + ")")
              .call(xAxis);

            // add the y Axis
            svg.append("g")
              .attr("transform", "translate(" + margin.left + "," + 0 + ")")
              .call(d3.axisLeft(y));

    }
    //Calculated attributes accessible from all functions
    chart.innerHeight = function(_){
        if (!arguments.length) {
            var innerHeight = (height - margin.top - margin.bottom)
            return innerHeight;
        }
        console.log("can't set inner height, it's calculated")
        return chart;
    }
    //Calculated attributes accessible from all functions
    chart.innerWidth = function(_){
        if (!arguments.length) {
            var innerWidth = (width - margin.left - margin.right)   
            return innerWidth;
        }
        console.log("can't set inner height, it's calculated")
        return chart;
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
  "data_id": "matching_projects", 
  "grouping": "ward", 
  "items": [
    {"matching": 124, "total": 350, "group": "Ward 1"}, 
    {"matching": 112, "total": 350, "group": "Ward 2"}, 
    {"matching": 12,  "total": 350, "group": "Ward 3"}, 
    {"matching": 110, "total": 350, "group": "Ward 4"}, 
    {"matching": 157, "total": 350, "group": "Ward 5"}, 
    {"matching": 122, "total": 350, "group": "Ward 6"}, 
    {"matching": 291, "total": 350, "group": "Ward 7"}, 
    {"matching": 229, "total": 350, "group": "Ward 8"}
  ]
}


var demoChart = ColumnChart()
        .width(200)
        .height(200)


d3.select('.mychart')
    .datum(apiData['items'])
    .call(demoChart);

setTimeout(function(){
        apiData.items[0].matching = 300
        apiData.items[1].matching = 250

        d3.select('.mychart')
            .datum(apiData['items'])
            .call(demoChart.update);

    }, 3000);


/*
initialize: function(chartOptions) {
      chartOptions.dataRequest.callback = chartCallback; 
  }
*/