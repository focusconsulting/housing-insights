"use strict"; 

var SubsidyTimelineChart = function(DATA_FILE, dataName, el, field, sortField, asc, readableField, width, height, building) {};
SubsidyTimelineChart.prototype = Object.create(Chart.prototype);

var subsidyTimelineExtension = { // Final step of inheriting from Chart, defines the object with which to extend the prototype
                             // as called in this.extendPrototype(...) above 
  setup: function(dataName, el, field, sortField, asc, readableField) {
    chart.svg;
    chart.minTime;
    chart.maxTime;
    chart.xScale;
    chart.yScale = function(i){};
    
    // 'append' calls to add text, lines and decorations to the chart
  }, 

  timeParser: {   
    month: function(string) { },
    day: function(string){ },
    year: function(string){ },
    toUTC: function(string){ },
    parsedDate: function(string){ }
  }

};

var DATA_FILE = './data/Subsidy.csv';

new SubsidyTimelineChart(DATA_FILE,'projectCSV','#subsidy-timeline-chart','Proj_Units_Tot','Proj_Zip',false,'Total Units',1000,300,buildingID); 

