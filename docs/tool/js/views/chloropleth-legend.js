"use strict"

var chloroplethLegend = {
  init: function(message,data){

    var joinedToGeoName = "joinedToGeo." + data.overlay + "_" + data.activeLayer;
    var chloroplethRange = getState()[joinedToGeoName][0].chloroplethRange;

    chloroplethLegend.tearDownPrevious();

    var wrapperId = 'overlay-about-' + data.overlay;

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

      // Copied shamelessly from:
      // https://stackoverflow.com/questions/2901102/how-to-print-a-number-with-commas-as-thousands-separators-in-javascript
      // This probably belongs at a broader scope, though currently
      // is only used below.
      function numberWithCommas(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
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
                      var stopMax = (i === ary.length - 1 ? "" : " - " + (+ary[i+1][0] - 1));
                      return numberWithCommas(d[0]) + numberWithCommas(stopMax);
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