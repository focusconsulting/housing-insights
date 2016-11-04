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
        ['Cluster 10', 605],
        ['DE.NW', 237],
        ['DE.BW', 157],
        ['DE.HE', 134],
        ['DE.NI', 136],
        ['DE.TH', 704],
        ['DE.', 361]
    ];

    jsonPath = '/static/Neighborhood_Clusters.geojson'
    $.getJSON(jsonPath, function (geojson) {

        // Initiate the chart
        Highcharts.mapChart('container', {

            title: {
                text: 'GeoJSON in Highmaps'
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
                data: data,
                mapData: geojson,
                joinBy: ['NAME', 0],
                keys: ['NAME', 'value'],
                name: 'Random data',
                states: {
                    hover: {
                        color: '#BADA55'
                    }
                },
                dataLabels: {
                    enabled: true,
                    format: '{point.properties.postal}'
                }
            }]
        });
    });
});
