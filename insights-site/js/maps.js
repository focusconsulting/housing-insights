$(function () {

    // Prepare random data
    var data = [
        ['Cluster 1', 728],
        ['Cluster 2', 710],
        ['Cluster 3', 963],
        ['Cluster 4', 541],
        ['Cluster 5', 622],
        ['Cluster 6', 866],
        ['Cluster 7', 398],
        ['Cluster 8', 785],
        ['Cluster 9', 223],
        ['Cluster 10', 605]
   
    ]; 

// Highcharts needs data sorted beforehand for the bar chart to be in order of value. It has no sorting function as far as I know. 
    
function sortFunction(a, b) {
    if (a[1] === b[1]) {
        return 0;
    }
    else {
        return (a[1] < b[1]) ? 1 : -1;
    }
}
    
data.sort(sortFunction);

// end sort
    
    jsonPath = '/static/Neighborhood_Clusters.geojson'
    $.getJSON(jsonPath, function (geojson) {
        
                //Initiate the chart
        // for some reason `data` only seems to share well if the chart renders before the map
       Highcharts.chart('container-2', {  // bar chart renders to #container-2
            title: {
              style: {
                  'display':'none'
              }  
            },
           xAxis: {
             type: 'category'  
           },
            series:[{
                data: data,
                keys: ['name', 'y'],
                type: 'bar',
                showInLegend: false,
                states: {
                    hover: {
                        color: '#BADA55'
                    }
                },
                point: {  //mouse events trigger function (define below) to highlight corresponding point in other container
                    events: {
                        mouseOver: function(point) {  
                            highlightOther(point);
                        },
                        mouseOut: function(point) {
                            highlightOther(point);
                        }
                    }
                }
            }],
          
        });

        // Initiate the map
        Highcharts.mapChart('container-1', {  // rendering to #container-1

            title: {
                text: 'Total Tax Assesed Land Value of all Affordable Properties by Neighborhood Cluster'
            },

            mapNavigation: {
                enabled: true,
                buttonOptions: {
                    verticalAlign: 'bottom'
                }
            },

            colorAxis: {
            },
                        
            series: [{
                type:'map',
                data: data,
                mapData: geojson,
                joinBy: ['NAME'],
                keys: ['NAME', 'value'],
                name: 'Land value',
                states: {
                    hover: {
                        color: '#BADA55'
                    }
                },
                dataLabels: {
                    enabled: true,
                    format: '{point.properties.postal}'
                },
                point: { //same events as above in bar chart
                    events: {
                        mouseOver: function(point) {
                            highlightOther(point);
                        },
                        mouseOut: function(point) {
                            highlightOther(point);
                        }
                    }
                }
            
            }]
        });
        
        // function to link hovering on one chart to highlighting on the other
        
        function highlightOther(point){
            for (i = 0; i < Highcharts.charts.length; i++) {
                if (point.type === 'mouseOver'){
                    Highcharts.charts[i].series[0].data[point.target.index].setState('hover');
                } else {
                    Highcharts.charts[i].series[0].data[point.target.index].setState();
                }
            }
        }
    });
});
