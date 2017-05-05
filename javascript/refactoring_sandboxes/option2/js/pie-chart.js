"use strict";

var PieChart = function(chartOptions) { //
    Chart.call(this, chartOptions); 
    this.extendPrototype(PieChart.prototype, PieExtension);
}

PieChart.prototype = Object.create(Chart.prototype);

var PieExtension = { 
  returnPieVariable: function(field,zoneType,zoneName) {
    var chart = this,
    zoneIndex;    
    this.nested = d3.nest()    //aggregate data by unique values in [field] defined for each pie at bottom
      .key(function(d) { return d[sideBar.zoneMapping[zoneType].name]; }) 
      .key(function(d) { return d[field]; })
      .rollup(function(v) { return v.length; })
      .entries(chart.data);

    var allObject = { // create object for sum of all zones
        key:'All',
        values: [
            {
                key: 'No',
                value: 0
            },
            {
                key: 'Yes',
                value: 0
            }
        ]    
    };

    this.nested.forEach(function(obj){ // sum up the yeses and nos
        obj.values.forEach(function(yesNo){
            allObject.values.find(function(allValue){ 
                return allValue.key === yesNo.key;
            }).value += yesNo.value;
        });
    });
    this.nested.sort(function(a,b){
      return d3.ascending(a.key,b.key);
    });
    this.nested.push(allObject);
    this.nested.move(-1,0); // uses array.prototype.move defined in housing-insights.js to move last item ("All") to be first.    
   /* if ( zoneType !== currentZoneType ) {
      setOptions(chart.nested);
    }*/
    zoneIndex = this.nested.findIndex(function(obj){ // ATTN: array.findIndex is ECMAScript 2016; may need
                                                     // different method or polyfill for older browsers
        return obj.key === zoneName;
    });
    this.nested = this.checkForEmpties();
    var stagePieVariable = this.nested[zoneIndex].values.sort(function(a,b){ // need to sort so that 'yes' is always in index 0
        return d3.descending(a.key,b.key);
    });
    return this.addPercentYes(stagePieVariable);
  },
  addPercentYes: function(stagePieVariable){ // adds a third key/value to each chart's object for the percent yes
                                             // now plotting only one arc bound to data, the percent yes, on top of
                                             // static backdground. much of the preceding data manipulation is no longer
                                             // necessary, but I'm leaving it in for now. It's more extensible, if we ever need
                                             // to plot more than 2 variables in a pie. JO
    var total = stagePieVariable[0].value + stagePieVariable[1].value;
    var percentYes = stagePieVariable[0].value / total;
    stagePieVariable.push({'key':'percentYes','value': percentYes});
    return stagePieVariable;
  },
  checkForEmpties: function(){ // when the sum is zero, the nesting fails to create an object. this method
                               // creates a dummy object such as {key:'Yes',value:0}
        
        this.nested.forEach(function(zone){
            if ( zone.values.length < 2 ) {
                var presentKey = zone.values[0].key;
                var missingKey = presentKey === 'Yes' ? 'No' : 'Yes';
                zone.values.push({key: missingKey, value: 0});
            }
        });
       return this.nested; 
  },  
  setup: function(chartOptions){
    
    this.field = chartOptions.field;
    this.width = chartOptions.width;
    this.height = chartOptions.height;
    this.zoneType = chartOptions.zoneType;
    this.zoneName = chartOptions.zoneName;
    var chart = this;
    
    this.pieVariable = this.returnPieVariable(this.field, this.zoneType, this.zoneName); // order of yes and no objects in the array cannot be guaranteed, so JO is programmatically finding the index of yes
    chart.radius = Math.min(this.width, this.height) / 2;
    
    chart.svg = d3.select(chartOptions.container)
      .append("svg")
      .attr('width', this.width+10)
      .attr('height', this.height+20) // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult
      .append("g")
      .attr("transform","translate(" + this.width /2 + "," + this.height /2 + ")");

    chart.arc = d3.arc()
      .outerRadius(chart.radius - this.width/20)
      .innerRadius(chart.radius - this.width/4)
      .startAngle(0);

    chart.background = chart.svg  // appends full-circle backgroud arc. will bind only "yes" arc over this one
                                  // to simplfy animation (always same start angle) JO
      .append('path')
      .datum({endAngle: 2 * Math.PI})
      .style("fill", "#ddd")
      .attr("d", chart.arc);

      // no longer need to invoke d3.pie because the angle of one arc is easy to calculate
    /*chart.pie = d3.pie()
        .sort(null)
        .value(function(d) { return d.value; });
    */
    
    chart.foreground = chart.svg.append('path')
      .style("fill", '#fd8d3c')
      .datum({endAngle: 0});

    chart.percentage = chart.svg.append("text")
        .attr("text-anchor", "middle")
        .attr('class','pie_number')
        .attr('y',5);

     chart.label = chart.svg.append("text")
        .attr("y", chart.height / 2 + 10)
        .attr('class','pie_text')
        .attr('text-anchor','middle');
    
    if (chartOptions.index === 0){
      setState('firstPieReady', true);
    }
    
    this.update();
  },
  arcTween: function(newAngle) { // HT: http://bl.ocks.org/mbostock/5100636
    var chart = this;
    return function(d){
      var interpolate = d3.interpolate(d.endAngle, newAngle);
      return function(t) {
        d.endAngle = interpolate(t);
        return chart.arc(d);
      };
    };    
  },
  returnTextPercent: function(){
    var chart = this;    
    var textPercent;
        textPercent = d3.format(".0%")((chart.pieVariable[0].value)/(chart.pieVariable[1].value+chart.pieVariable[0].value));        
    return textPercent;
  },
  update: function(){
    var chart = this;
    chart.foreground
      .transition().duration(750)
      .attrTween("d", chart.arcTween(chart.pieVariable[2].value * Math.PI * 2));
    chart.percentage
        .text(this.returnTextPercent());
    chart.label 
        .text(chart.field); // TODO: use data manifest to provide readable field names, or arrange for API to return them
  }
};