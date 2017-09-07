"use strict";

var resultsView = {

   
    init: function(msg, data) {
        console.log(msg,data);
        //msg and data are from the pubsub module that this init is subscribed to. 
        // changed Jun 8 to be called by filteredData
        

        resultsView.charts = [];
        var instances = ['Projects','Units'];

        instances.forEach(function(instance, i){
            console.log("trying to add donuts")
            resultsView.charts[i] = new DonutChartOld({
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
          ['filteredData', DonutChartOld.prototype.updateSubscriber], //TODO - refactor donuts to use new chart proto, and then the update function should subscribe to 'filteredProjectsAvailable' instead, which put data on resultsView.filteredProjects
          ['filteredData',resultsView.updateFilteredProjects],
          ['filteredProjectsAvailable', resultsView.updateFilteredStats],
          ['filteredStatsAvailable',resultsView.makeBarChart]
        ]);

    },

    filteredProjects: [],
    updateFilteredProjects: function(msg, data){
        var runFilter = function(raw_projects){
            var filteredIds = getState()['filteredData'][0]
            resultsView.filteredProjects = raw_projects.objects.filter(function(d){
                return filteredIds.indexOf(d.nlihc_id) !== -1;
            });
            setState('filteredProjectsAvailable',resultsView.filteredProjects);         //Needed to make sure this fires every time. TODO is there a way we can setState that triggers even if the value is the same (i.e. true)?
        }

        controller.getData({name: 'raw_project',url: model.URLS.project, callback: runFilter})
    },


    filteredStats: {},
    updateFilteredStats: function(msg,data){
        //Updates statistics used by the right sidebar graphs
        //TODO we will probably want to replace this with an API call that can do this with SQL queries when provided a list of nlihc_ids. 
        //TODO we should probably also get this data from the filter data set (which has duplicate entries for each subsidy) as this will already be joined to extra data not available int he projects table. 

        //TODO hacky way to initialize this variable, should make it dynamically created - just for demo purposes for now. 
        resultsView.filteredStats['ward'] = [
                {"projects": 0, "total_projects": 0, "percent_projects": 0,  "proj_units_assist_max": 0, "total_proj_units_assist_max": 0, "percent_proj_units_assist_max": 0, "group": "Ward 1"}, 
                {"projects": 0, "total_projects": 0, "percent_projects": 0,  "proj_units_assist_max": 0, "total_proj_units_assist_max": 0, "percent_proj_units_assist_max": 0, "group": "Ward 2"}, 
                {"projects": 0, "total_projects": 0, "percent_projects": 0,  "proj_units_assist_max": 0, "total_proj_units_assist_max": 0, "percent_proj_units_assist_max": 0, "group": "Ward 3"}, 
                {"projects": 0, "total_projects": 0, "percent_projects": 0,  "proj_units_assist_max": 0, "total_proj_units_assist_max": 0, "percent_proj_units_assist_max": 0, "group": "Ward 4"}, 
                {"projects": 0, "total_projects": 0, "percent_projects": 0,  "proj_units_assist_max": 0, "total_proj_units_assist_max": 0, "percent_proj_units_assist_max": 0, "group": "Ward 5"}, 
                {"projects": 0, "total_projects": 0, "percent_projects": 0,  "proj_units_assist_max": 0, "total_proj_units_assist_max": 0, "percent_proj_units_assist_max": 0, "group": "Ward 6"}, 
                {"projects": 0, "total_projects": 0, "percent_projects": 0,  "proj_units_assist_max": 0, "total_proj_units_assist_max": 0, "percent_proj_units_assist_max": 0, "group": "Ward 7"}, 
                {"projects": 0, "total_projects": 0, "percent_projects": 0,  "proj_units_assist_max": 0, "total_proj_units_assist_max": 0, "percent_proj_units_assist_max": 0, "group": "Ward 8"}
        ]

        //Note, accessing data collection directly to avoid aysnc nature of callback - we know this data set has been loaded because it's required for this function to be called
        var raw_projects = model.dataCollection['raw_project'].objects; 
        console.log(raw_projects.length); // 1034
        //Update totals. TODO we only need to do this once, so we should move this elsewhere when we refactor this so it runs only on load. 
        for (var i = 0; i < raw_projects.length; i++) {
            if ( raw_projects[i]['ward'] !== null ) {
                var ward = raw_projects[i]['ward']
                var proj_units_assist_max = raw_projects[i]['proj_units_assist_max']

                var statEntry = resultsView.filteredStats['ward'].find(x => x.group === ward)
                    statEntry.total_projects++
                    statEntry.total_proj_units_assist_max = !isNaN(+proj_units_assist_max) ? statEntry.total_proj_units_assist_max + proj_units_assist_max : statEntry.total_proj_units_assist_max;
                
            } // total of total.projects = 931 i.e.  103 projects have null ward
        }


        //Update stats for each filtered project
        for (var i = 0; i < resultsView.filteredProjects.length; i++) {
                var ward = resultsView.filteredProjects[i]['ward']
                if ( ward !== null ){
                    var proj_units_assist_max = resultsView.filteredProjects[i]['proj_units_assist_max']

                    var statEntry = resultsView.filteredStats['ward'].find(x => x.group === ward)
                        statEntry.projects++
                        statEntry.proj_units_assist_max = statEntry.proj_units_assist_max + proj_units_assist_max
                }
        }

        //Calculate percents
        for (var i = 0; i < resultsView.filteredStats['ward'].length; i++) {
                var d = resultsView.filteredStats['ward'][i]
                console.log(d);
                d.percent_projects = d['projects'] / d['total_projects']  //TODO protect against div0 error?
                d.percent_proj_units_assist_max = d['proj_units_assist_max'] / d['total_proj_units_assist_max']
            };  

        setState('filteredStatsAvailable',resultsView.filteredStats['ward']);
        
    },
    makeBarChart:function(){

        //Percent of project
        if (!resultsView.projectBarChart){
            resultsView.projectBarChart = new BarChart('#projectPercentChart')
                .width(300)
                .height(200)
                .margin({top: 0, right: 20, bottom: 20, left: 50})
                .data(resultsView.filteredStats['ward'])
                .field('percent_projects')
                .label('group')
                .percentMode(true)
                .create()
        } else {
            resultsView.projectBarChart.update(resultsView.filteredStats['ward']);
        }

        //Percent of units
        if (!resultsView.unitBarChart){
            resultsView.unitBarChart = new BarChart('#unitPercentChart')
                .width(300)
                .height(200)
                .margin({top: 0, right: 20, bottom: 20, left: 50})
                .data(resultsView.filteredStats['ward'])
                .field('percent_proj_units_assist_max')
                .label('group')
                .percentMode(true)
                .create()
        } else {
            resultsView.unitBarChart.update(resultsView.filteredStats['ward']);
        }

    }
};