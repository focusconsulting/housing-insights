"use strict";

var resultsView = {

    init: function(msg, data) {
        console.log(msg,data);
        //msg and data are from the pubsub module that this init is subscribed to. 
        // changed Jun 8 to be called by filteredData
        

        resultsView.charts = [];
        var instances = ['Buildings','Units'];

        instances.forEach(function(instance, i){
            console.log("trying to add donuts")
            resultsView.charts[i] = new DonutChart({
                dataRequest: {
                    name: 'raw_project',
                    url: model.URLS.project
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


        /////////////////////////////////////////////////////////////////////
        //Example only - bar chart
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

        //Calculate percents
        var calculatePercents = function(data) {
            for (var i = 0; i < data.length; i++) {
                var d = data[i]
                d.percent = d['matching'] / d['total'] 
            };   
        };

        calculatePercents(apiData.items);

        //TODO don't hardcode this index
        console.log("try to add bar chart")
        var barChart = new BarChart('#demoPercentChart')
            .width(300)
            .height(200)
            .margin({top: 0, right: 20, bottom: 20, left: 50})
            .data(apiData['items'])
            .field('percent')
            .label('group')
            .percentMode(true)
            .create()


        




    }
};