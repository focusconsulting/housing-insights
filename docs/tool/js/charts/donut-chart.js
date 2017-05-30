"use strict";

var DonutChart = function(chartOptions) { //
    PieChartProto.call(this, chartOptions); 
    this.extendPrototype(DonutChart.prototype, DonutChartExtension);
}

DonutChart.prototype = Object.create(PieChartProto.prototype);

var DonutChartExtension = { 
  returnPieVariable: function(field,zoneType,zoneName) {
    var chart = this,
    zoneIndex;
    this.nested = d3.nest()    //aggregate data by unique values in [field] defined for each pie at bottom
      .key(function(d) { return d[resultsView.zoneMapping[zoneType].name]; }) 
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
    zoneIndex = this.nested.findIndex(function(obj){ 
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
    
    this.zoneType = chartOptions.zoneType;
    this.zoneName = chartOptions.zoneName;
    var chart = this;
    
    this.pieVariable = this.returnPieVariable(this.field, this.zoneType, this.zoneName); // order of yes and no objects in the array cannot be guaranteed, so JO is programmatically finding the index of yes
    
    

    

      // no longer need to invoke d3.pie because the angle of one arc is easy to calculate
    /*chart.pie = d3.pie()
        .sort(null)
        .value(function(d) { return d.value; });
    */
    
    chart.foreground = chart.svgCentered.append('path')
      .style("fill", '#fd8d3c')
      .datum({endAngle: 0});

    chart.percentage = chart.svgCentered.append("text")
        .attr("text-anchor", "middle")
        .attr('class','pie_number')
        .attr('y',5);

     
    if (chartOptions.index === 0){
      setState('firstPieReady', true);
    }
    
    this.update();
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
        .text(chart.field); // TODO: use meta.json to provide readable field names, or arrange for API to return them
  }

};

