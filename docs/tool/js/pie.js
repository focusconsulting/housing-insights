"use strict";

Array.prototype.move = function (old_index, new_index) { // HT http://stackoverflow.com/questions/5306680/move-an-array-element-from-one-array-position-to-another
                                                         // native JS for moving around array items
                                                         // used below to always move the all-zone option to the top 
    while (old_index < 0) {
        old_index += this.length;
    }
    while (new_index < 0) {
        new_index += this.length;
    }
    if (new_index >= this.length) {
        var k = new_index - this.length;
        while ((k--) + 1) {
            this.push(undefined);
        }
    }
    this.splice(new_index, 0, this.splice(old_index, 1)[0]);
    return this; // for testing purposes
};
 
 var mapZones = { // object to map mapLayer names (the keys) to the field in the data
                  // later code adds an array of all the values for each type to the objects
                  // for populating the dropdown list
        ward: {
          name: 'Ward2012'
          
        },
        tract: {
          name: 'Geo2010'
          
        },
        zip: {
          name: 'Zip'
        }
    };

var currentZoneType; // 


var PieChart = function(DATA_FILE, dataName, el, field, width, height) { 
    Chart.call(this, DATA_FILE, dataName, el, field, width, height); 
    this.extendPrototype(PieChart.prototype, PieExtension);
}

PieChart.prototype = Object.create(Chart.prototype);

var PieExtension = { 


  returnPieVariable: function(field,zoneType,zoneName) {
    var chart = this,
    zoneIndex;

    if (zoneType === undefined) {
        zoneType = 'ward';
    }

    
    this.nested = d3.nest()    //aggregate data by unique values in [field] defined for each pie at bottom
      .key(function(d) { return d[mapZones[zoneType].name]; }) 
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
    this.nested.move(-1,0); // uses array.prototype.move defined above to move last item ("All") to be first.
    console.log(this.nested);
    if ( zoneType !== currentZoneType ) {
      setOptions(chart.nested);
     }

    if (zoneName === undefined){
        zoneIndex = 0; // default to the first item in the options list, All
    } else {
        zoneIndex = this.nested.findIndex(function(obj){ // ATTN: array.findIndex is ECMAScript 2016; may need
                                                         // different method or polyfill for older browsers
            return obj.key === zoneName;
        });
    }
    this.nested = this.checkForEmpties();
    console.log(this.nested);
    return this.nested[zoneIndex].values.sort(function(a,b){ // need to sort so that 'yes' is always in index 0
        return d3.descending(a.key,b.key);
    });

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
  setup: function(el, field, width, height){
    this.field = field;
   
    this.width = width;
    this.height = height;
    
    
    var chart = this;
    this.pieVariable = this.returnPieVariable(field); // order of yes and no objects in the array cannot be guaranteed, so JO is programmatically finding the index of yes
    console.log(this.pieVariable);
    chart.radius=Math.min(width, height)/2;

    chart.color = d3.scaleOrdinal()
      .domain(['No','Yes'])
      .range(["#b3cde3","#fbb4ae"]);

   chart.svg = d3.select(el)
    .append("svg")
    .attr('width', width+10)
    .attr('height', height+20) // d3 v4 requires setting attributes one at a time. no native support for setting attr or style with objects as in v3. this library would make it possible: mini library D3-selection-mult
    .append("g")
    .attr("transform","translate(" + width /2 + "," + height /2 + ")");

    chart.arc = d3.arc()
        .outerRadius(chart.radius - width/20)
        .innerRadius(chart.radius - width/4);

    chart.pie = d3.pie()
        .sort(null)
        .value(function(d) { return d.value; });

   

    // old colors "#bebada","#fb8072","#80b1d3","#fdb462","#b3de69","#fccde5","#d9d9d9","#bc80bd","#ccebc5","#ffed6f","#2C93E8","#F56C4E"]);

    //d3 pie layout, which calculates the section angles for you
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

    chart.g = chart.svg.selectAll("arc")

        .data(chart.pie(chart.pieVariable))
        .enter().append("g")
        .attr("class", "arc");
        


    chart.paths = chart.g.append('path')

          .attr("d", function(d,i){ // same as chart.arc without function, passes in d
             
             console.log(i,d.data.key)
            return chart.arc(d);
        })
          .style("fill", function(d) { return chart.color(d.data.key); });



    chart.percentage = chart.g.append("text")
        .attr("text-anchor", "middle")
        .attr('class','pie_number')
        .attr('y',5)
        .text(this.returnTextPercent());

    //this is bad. 
    chart.g.append("text")
        
        .attr("y", chart.height / 2 + 10)
        .attr('class','pie_text')
        .attr('text-anchor','middle')
        .text(chart.field);
  }
};


var DATA_FILE ='data/Project.csv';

/*
 *
 */

function changeZoneType() {
  if ( map.clickedLayer !== currentZoneType ) {
    changeZone();
  }
}

 function changeZone(e){
    var zType,
        zName;
    if ( e !== undefined ) { // i.e. function call comes from selecting option in drop-down
      zType = e.target.selectedOptions[0].className;
      zName = e.target.selectedOptions[0].value; 
    } else { // i.e. function call comes from selecting different map layer
      zType = map.clickedLayer;
      zName = 'All';
    }
    
    map.pieCharts.forEach(function(chart){

        chart.pieVariable = chart.returnPieVariable(chart.field,zType,zName); 
    
    chart.paths
      .data(chart.pie(chart.pieVariable))

      .attr("d", function(d,i){ // same as chart.arc without function, passes in d
            console.log(i,d.data.key)
            return chart.arc(d);
        });

      chart.percentage
        .text(chart.returnTextPercent())

     });
  };


function setOptions(nested) {
  
  if ( mapZones[map.clickedLayer].values === undefined ) { // i.e. the  zones withing the zoneType have not been 
                                                           // enumerated yet
        mapZones[map.clickedLayer].values = [];
        nested.forEach(function(obj) {
          mapZones[map.clickedLayer].values.push(obj.key)
        });
        
  }
  var selector = document.getElementById('zone-selector');
  selector.innerHTML = '';
  mapZones[map.clickedLayer].values.forEach(function(zone,i){
    var option = document.createElement('option');
    if ( i === 0 ) { option.setAttribute('selected','selected'); }
    option.setAttribute('class',map.clickedLayer);
    option.setAttribute('value',zone);
    option.id = zone.toLowerCase().replace(/ /g,'-');
    option.innerHTML = zone;
    selector.appendChild(option);
  });  
currentZoneType = map.clickedLayer;
}