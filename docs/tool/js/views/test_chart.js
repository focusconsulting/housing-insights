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

var demoValueChart = new BarChart('.demoValueChart')
            .width(400)
            .height(200)
            .margin({top: 20, right: 20, bottom: 20, left: 50})
            .data(apiData['items'])
            .field('matching')
            .label('group')
            .percentMode(false)
            .create()


var demoPercentChart = new BarChart('.demoPercentChart')
            .width(300)
            .height(200)
            .margin({top: 20, right: 20, bottom: 20, left: 50})
            .data(apiData['items'])
            .field('percent')
            .label('group')
            .percentMode(true)
            .create()

setTimeout(function(){
        //Change some data to demonstrate animation, both swapping and stretching
        //Important - when updating data, need a new object not a modified object to ensure object constancy (i.e. bars move if needed)
        newApiData = JSON.parse(JSON.stringify(apiData))    //make deep copy
        newApiData.items[0].group = "Ward 4";
        newApiData.items[3].group = "Ward 1";

        newApiData.items[0].matching = 350;
        newApiData.items[1].matching = 300;
        newApiData.items[2].matching = 250;
        newApiData.items[3].matching = 200;
        newApiData.items[4].matching = 150;
        newApiData.items[5].matching = 100
        newApiData.items[6].matching = 50
        newApiData.items[7].matching = 10;
        calculatePercents(newApiData.items);
        

        demoValueChart.update(newApiData.items);
        demoPercentChart.update(newApiData.items);

    }, 4000);

setTimeout(function(){
        demoValueChart.width(200)
            .height(200)
            .resize();

     }, 2000);