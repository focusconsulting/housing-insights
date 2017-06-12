"use strict";

var resultsView = {

    init: function(msg, data) {
        console.log(msg,data);
        //msg and data are from the pubsub module that this init is subscribed to. 
        // changed Jun 8 to be called by filteredData
        
        console.log('resultsView.init()');
        
        resultsView.charts = [];
        var instances = ['Buildings','Units'];
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
        setSubs([
          ['filteredData', DonutChart.prototype.updateSubscriber]
        ]);        
    }
};