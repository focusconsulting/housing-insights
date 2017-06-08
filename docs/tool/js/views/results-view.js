"use strict";

var resultsView = {
    init: function() {
        console.log('resultsView.init()');
        setSubs([
          // filteredData should trigger an update
        ]);
        resultsView.charts = [];
        var instances = ['buildings','units'];
        instances.forEach(function(instance, i){
            resultsView.charts[i] = new DonutChart({
                dataRequest: {
                    name: 'raw_project',
                    url: model.dataCollection.metaData.project.api.raw_endpoint
                },

                count: instance,
                container: '#pie-' + i,
                width: 75,
                height: 95,
                index: i,
                margin: {
                    top:0,
                    right:0,
                    bottom:20,
                    left:0
                }
            })
        });
    }

};