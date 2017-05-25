"use strict";

var sideBar = {
    init: function() {
        setSubs([
            ['firstPieReady', sideBar.setDropdownOptions],
            ['mapLayer',sideBar.changeZoneType],
            ['pieZone', sideBar.changeZoneType]
        ]);
        sideBar.charts = [];
        var instances = ['subsidized','cat_expiring','cat_failing_insp','cat_at_risk'];
        instances.forEach(function(instance, i){
            sideBar.charts[i] = new DonutChart({
                dataRequest: {
                    name: 'raw_project',
                    url: model.dataCollection.metaData.project.api.raw_endpoint
                },
                field: instance,
                container: '#pie-' + i,
                width: 75,
                height: 95,
                zoneType: 'ward',
                zoneName: 'All',
                index: i,
                margin: {
                    top:0,
                    right:0,
                    bottom:20,
                    left:0
                }
            })
        });
    },
    zoneMapping: { // object to map mapLayer names (the keys) to the field in the data
                  // later code adds an array of all the values for each type to the objects
                  // for populating the dropdown list
        ward: {
          name: 'ward'
          
        },
        tract: {
          name: 'census_tract'
          
        },
        zip: {
          name: 'zip'
        },
        neighborhood_cluster: {
          name: 'neighborhood_cluster_desc'
        }
    },
    setDropdownOptions: function() {
               
            var activeLayer = getState().mapLayer[0];            
            if ( sideBar.zoneMapping[activeLayer].values === undefined ) { // i.e. the  zones withing the zoneType have not been 
                                                                       // enumerated yet
                sideBar.zoneMapping[activeLayer].values = [];
                sideBar.charts[0].nested.forEach(function(obj) {
                    sideBar.zoneMapping[activeLayer].values.push(obj.key)
                });                                    
            }
            var selector = document.getElementById('zone-selector');
            selector.onchange = function(e){
                setState('pieZone', e.target.selectedOptions[0].value);                 
            };
            selector.innerHTML = '';
            sideBar.zoneMapping[activeLayer].values.forEach(function(zone,i){
                var option = document.createElement('option');
                if ( i === 0 ) { option.setAttribute('selected','selected'); }
                option.setAttribute('class',activeLayer);
                option.setAttribute('value',zone);
                option.id = zone.toLowerCase().replace(/ /g,'-');
                option.innerHTML = zone;
                selector.appendChild(option);
            });

    },
    changeZoneType: function(msg){
        var zoneType = getState().mapLayer[0];
        document.getElementById('zone-drilldown-instructions').innerHTML = 'Choose a ' + zoneType;
        if (getState().firstPieReady) { 
            if (msg === 'mapLayer') {
                setState('pieZone', 'All');
            }
            var zoneName = getState().pieZone[0];                
            sideBar.charts.forEach(function(chart){
                chart.pieVariable = chart.returnPieVariable(chart.field,zoneType,zoneName);
                chart.update();
            });
            if ( msg === 'mapLayer' ) { // if fn was called by changing mapLayer state. if not, leave dropdown
                                        // menu alone
                sideBar.setDropdownOptions();
            }
        } else { // if this function was called suring initial setup, before pies were ready
            setState('pieZone', 'All');
        }
    }

};