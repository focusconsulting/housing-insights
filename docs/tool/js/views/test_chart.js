//Do a demo of the chart
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
    {"matching": 229, "total": 350, "group": "Ward 8"},
    {"matching": 229, "total": 350, "group": "Ward 9"}
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

var demoValueChart = new BarChartProto({
                    width: 400,
                    height: 200,
                    container: '.demoValueChart',
                    margin: {top: 20, right: 20, bottom: 20, left: 50},
                    data: apiData['items'],
                    field: 'matching',
                    label: 'group',
                    percentMode: false
                })

var demoPercentChart = new BarChartProto({
                    width: 300,
                    height: 200,
                    container: '.demoPercentChart',
                    margin: {top: 20, right: 20, bottom: 20, left: 50},
                    data: apiData['items'],
                    field: 'percent',
                    label: 'group',
                    percentMode: true
                })


setTimeout(function(){
        apiData.items[0].matching = 500;
        apiData.items[1].matching = 250;
        calculatePercents(apiData.items);
        apiData.items[0].group = "Ward 8";
        apiData.items[7].group = "Ward 1";

        demoValueChart.update(apiData.items);
        demoPercentChart.update(apiData.items);

    }, 3000);