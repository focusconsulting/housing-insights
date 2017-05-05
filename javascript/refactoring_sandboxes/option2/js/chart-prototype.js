var Chart = function(chartOptions) {    //chartOptions is an object, was DATA_FILE, el, field, sortField, asc, readableField                                                              
    
    this.initialize(chartOptions); 
};

Chart.prototype = {
    
    initialize: function(chartOptions) {
      var chart = this; 
      chartOptions.dataRequest.callback = chartCallback;         
      controller.getData(chartOptions.dataRequest) // dataRequest is an object {name:<String>[, params:<Array>[,callback:<Function>]]}
      function chartCallback(data){
        chart.data = data.items;
        if (chartOptions.sort !== undefined ) {
          chart.data.sort(function(a, b) { 
            if (chartOptions.sort.direction === 'asc') return a[chartOptions.sort.field] - b[chartOptions.sort.field];
            return b[chartOptions.sort.field] - a[chartOptions.sort.field]; 
          });            
        }
        chart.minValue = d3.min(chart.data, function(d) { 
              return d[chartOptions.field]
        });
        chart.maxValue = d3.max(chart.data, function(d) { 
              return d[chartOptions.field]
        });
        chart.setup(chartOptions); 
      }
    },                       
    extendPrototype: function(destinationPrototype, obj){ 
      for(var i in obj){
          destinationPrototype[i] = obj[i];
      } 
    } 
};