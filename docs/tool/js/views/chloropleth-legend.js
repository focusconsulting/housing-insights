"use strict"

var chloroplethLegend = {
  init: function(message,data){
    var joinedToGeoName = "joinedToGeo." + data.overlay + "_" + data.activeLayer;
    var chloroplethRange = getState()[joinedToGeoName][0].chloroplethRange;
    var overlayConfig = mapView.initialOverlays.find(function(obj){return obj['name']==data.overlay});

    chloroplethLegend.tearDownPrevious();

    var wrapperId = 'overlay-' + data.overlay + '-legend';

    var partialRequest = {
        partial: 'chloropleth-legend',
        container: wrapperId,
        transition: false,
        callback: partialCallback
    }
    controller.appendPartial(partialRequest, this);
    // A ChloroplethColorRange is assigned to the 'data' object
    // that results from the joinedToGeo setState() call and that 
    // is passed to addOverlayLayer as the 'data' argument.
    // The ugly-looking joinedToGeoName variable
    // retrieves the chloropleth color range. 
    // There's got to be a more elegant solution out there for
    // assigning a chloropleth color range to a data overlay and
    // retrieving the color range along with the overlay.

    function partialCallback(){

      // This probably belongs at a broader scope, though currently
      // is only used below.
      function formatNumber(x,style) {
        if (style=="number") {
          x = Math.round(x)
          return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","); //adds thousands separators, from https://stackoverflow.com/questions/2901102/how-to-print-a-number-with-commas-as-thousands-separators-in-javascript
        }
        if (style == "percent") {
          return Math.round(x * 100) + "%";
        }
        if (style == "money"){
          x = x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","); //adds thousands separators
          x = "$" + x
          return x
        }
      }


      var eachLegendItem = d3.select('#chloroplethLegend ul')
                              .selectAll('li')
                              .data(chloroplethRange.stopsAscending)
                              .enter()
                              .append('li');
      eachLegendItem.append('div')
                    .classed("chloroplethLegendSquare", true)
                    .style("background-color", function(d){
                      return d[1];
                    });
      eachLegendItem.append('span')
                    .text(function(d, i){
                        var ary = chloroplethRange.stopsAscending;
                        var stopMax = (i === ary.length - 1 ? null : (+ary[i+1][0]  )); //removed subtract 1 because doesn't work w/ percents. TODO should fix this to provide a logical "less than but not equal to" display!
                        var style = overlayConfig['style']

                        if (stopMax !== null) {
                            var descriptor = formatNumber(d[0],style) + " - " + formatNumber(stopMax,style);
                        } else {
                            var descriptor = formatNumber(d[0],style) 
                        };
                      return descriptor
                    });
    }
  
  },
  tearDownPrevious: function(){
    var lgnd = document.getElementById('chloroplethLegend');
    if(lgnd !== null){
      lgnd.parentElement.removeChild(lgnd);
    }
  }

}