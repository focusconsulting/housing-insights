$(function () {


    $.get('../data/summary_tax_values_plus_unit_counts.csv', function(csv) {

        var results = Papa.parse(csv, {dynamicTyping: true}); // using papaParse.js to parsce csv string to array, returns object
        console.log(results);
        data = results.data.slice(1); //removes first row (headers) from data; keys are set below

    // Highcharts needs data sorted beforehand for the bar chart to be in order of value. It has no sorting function as far as I know.

    function sortFunction(a, b) {
        if (a[9] === b[9]) {  // sorting by index 9: "sum_appraised_value_current_total"
            return 0;
        }
        else {
            return (a[9] < b[9]) ? 1 : -1;
        }
    }

    data.sort(sortFunction);

    console.log(data);

    // end sort

    jsonPath = '../data/Neighborhood_Clusters.geojson'
    /*$.getJSON(jsonPath, {data}, */
    $.ajax({
      dataType: "json",
      url: jsonPath,
      data: data,
      success: function (geojson) {
        console.log(geojson);

        //Initiate the chart
        // for some reason `data` only seems to share well if the chart renders before the map
       Highcharts.chart('container-2', {  // bar chart renders to #container-2
            title: {
              style: {
                  'display':'none'
              }
            },
     /*      xAxis: {
             type: 'category'
           },*/
           plotOptions: {
            series: {
                pointPadding: 0.05,
                groupPadding: 0.05,
                borderWidth: 0,
                shadow: false
              }
          },
            series:[{
                data: data,
                keys: ["NAME"
                        ,"project_count"
                        ,"ssl_distinct_count"
                        ,"ssl_count"
                        ,"appraised_value_count"
                        ,"missing_tax_count"
                        ,"sum_appraised_value_prior_land"
                        ,"sum_appraised_value_prior_total"
                        ,"sum_appraised_value_current_land"
                        ,"y"/*sum_appraised_value_current_total*/
                        ,"cluster_tr2000_name"
                        ,"percent_ssl_missing"
                        ,"average_land_appraisal"
                        ,"sum_assisted_units"
                        ,"avg_sum_appraised_value_prior_land"
                        ,"avg_sum_appraised_value_prior_total"
                        ,"avg_sum_appraised_value_current_land"
                        ,"avg_sum_appraised_value_current_total"
                      ], // from original header of the csv file, changing 0 index to "NAME" and index 9 sum_appraised_value_current_total to 'y'
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
           tooltip:{
               formatter: function(){
                 var num = '$' + this.point.y.toFixed(0).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,"); // converts number to currency string
                 return this.point.cluster_tr2000_name + '<br /><b>Total value:</b> ' + num;
               }
           }


        });

        // Initiate the map
        Highcharts.mapChart('container-1', {  // rendering to #container-1

            title: {
              style: {
                  'display':'none'
              }
            },

            mapNavigation: {
                enabled: true,
                buttonOptions: {
                    verticalAlign: 'bottom'
                }
            },

            /*trying to fix projection
            hc-transform: {
                default: {
                    crs: "+proj=merc"
                }
            }
            */
            colorAxis: {
            },

            series: [{
                type:'map',
                data: data,
                mapData: geojson,
                joinBy: ['NAME'],
                keys: ["NAME"
                        ,"project_count"
                        ,"ssl_distinct_count"
                        ,"ssl_count"
                        ,"appraised_value_count"
                        ,"missing_tax_count"
                        ,"sum_appraised_value_prior_land"
                        ,"sum_appraised_value_prior_total"
                        ,"sum_appraised_value_current_land"
                        ,"value"/*sum_appraised_value_current_total*/
                        ,"cluster_tr2000_name"
                        ,"percent_ssl_missing"
                        ,"average_land_appraisal"
                        ,"sum_assisted_units"
                        ,"avg_sum_appraised_value_prior_land"
                        ,"avg_sum_appraised_value_prior_total"
                        ,"avg_sum_appraised_value_current_land"
                        ,"avg_sum_appraised_value_current_total"
                      ], // from original header of the csv file, changing 0 index to "NAME" and index 9 sum_appraised_value_current_total to 'value'
                name: 'Land value',
                states: {
                    hover: {
                        color: '#BADA55'
                    }
                },
        /*        dataLabels: {
                    enabled: true,
                    format: '{point.properties.postal}'
                }, */

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

            }],
            tooltip:{
               formatter: function(){
                 var num = '$' + this.point.value.toFixed(0).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,"); // converts number to cuurency string
                 var average_value = '$' + this.point.avg_sum_appraised_value_current_total.toFixed(0).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
                 return this.point.cluster_tr2000_name
                        + '<br /><b>Total tax assesed value:</b> ' + num
                        + '<br/><b>Value Per affordable unit:</b> '+ average_value;
               }
            }
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
    }
});
});
});
