"use strict";

var D3Table = function(container) {    //chartOptions is an object, was DATA_FILE, el, field, sortField, asc, readableField                                                              
/*
Turns an array of objects into an html table. 

Usage:
data = [
  {
    "col1":"foo",
    "col2":"bar"
  },
  {
    "col1":"baz",
    "col2":"bing"
  },
]

var tbl = new D3Table('.containerDivSelectString')
          .data(data)
          .columns(['col1','col2'])
          .create()

You can also specify header values that are not the same as the key in the data object, and custom data formatting functions. 
If the value of a column in the 'columns' list is a string, the label will be the same as the field and the data will be displayed as-is. 
Columns can mix-and-match the string method or the object method, but if you use the object method you must specify the whole object.

var columns = ['col1',
          {field:'col2', 
          label:'Second Column', 
          class:'yoyo', 
          html: function(d){return '$' + d}
          }
        ]

tbl.columns(columns).update()

*/
    this.setup(container); 
    return this;
};

D3Table.prototype = {
    create: function(){
      /*
      This method is called to trigger drawing of the chart once all initial properties have been 
      set using method chaining. Example:

      myChart = new ChartProto('.myContainerSelector')
                .width(500)
                .height(200)
                .create()
      */
      var chart = this
      chart.update()
      return chart
    },
    setup: function(container) {
      /*
      setup initializes all the default parameters, and create the container objects that are only created once. 
      This method is run automatically when a new object is created
      */

      var chart = this; 

      //Setup defaults
      chart._data = []
      chart._columns = []
      chart._container = container
      chart._delay = 200
      chart._duration = 1000

      chart._table = d3.select(container).append('table')
      chart._thead = chart._table.append('thead')
      chart._thead_row = chart._thead.append('tr')
      chart._tbody = chart._table.append('tbody')
      chart._tfoot = chart._table.append('tfoot')
      chart._tfoot_row = chart._tfoot.append('tr')

    },

    resize: function(){
      //Unused in this chart
      return this
    }, 
    update: function(data){
      /*
      Put the data into the chart
      */
      var chart = this

      //Add column headers cells (hc)
      var HC = chart._thead_row.selectAll('td')
          .data(chart.columns())
      var newHC = HC.enter()
                    .append('td')
      var allHC = newHC.merge(HC)
          .html(function(d){return d.label})

      HC.exit().remove()

      //Add the data rows and cells (DRs, DCs)
      var DRs = chart._tbody.selectAll('tr')
        .data(chart.data());
      var newDRs = DRs.enter()
        .append('tr')
      var allDRs = newDRs.merge(DRs)
      var DCs = allDRs.selectAll('td')
        .data(function(row,i){
          return chart.columns().map(function(column){
            return {column:column, value:row[column['field']]}
          })
        })

      var newDCs = DCs.enter()
        .append('td')
      var allDCs = newDCs.merge(DCs)  
        .html(function(d){
            var func = d.column.html
            return func(d.value)
          })
        .attr("class", function(d) {return d.column.class}) //overwrites anything existing

      DRs.exit().remove(); //remove out of date rows
      DCs.exit().remove(); //remove out of date cells

    },      
    //TODO not used currently
    sort: function(field, direction) {
        chart.data.sort(function(a, b) { 
          if (direction === 'asc') return a[chartOptions.sort.field] - b[chartOptions.sort.field];
          return b[chartOptions.sort.field] - a[chartOptions.sort.field]; 
        });             
    },

    /*
    Custom getter/setters
    */
    data: function(_){
        if (!arguments.length) return this._data;
        this._data = _;
        return this;
    },
    columns: function(_){
        if (!arguments.length) return this._columns;
        for (var i = 0; i < _.length; i++) {

          //If entry is just the column name, convert to object w/ defaults
          if (typeof _[i] === 'string'){
            _[i] = {"field":_[i],
                    "label":_[i],
                    "class":"",
                    "html":function(d){return d}
                  }
          } else{
            //do nothing - asssume in proper format. Could add validation here.
          }
        };
        this._columns = _;
        return this;
    },

    container: function(_){
        if (!arguments.length) return this._container;
        this._container = _;
        return this;
    },
    delay: function(_){
        if (!arguments.length) return this._delay;
        this._delay = _;
        return this;
    },
    duration: function(_){
        if (!arguments.length) return this._duration;
        this._duration = _;
        return this;
    }
};



