var filterUtil = {
	
	init: function(){
		setSubs([
			['filterValues', filterUtil.publishFilteredData],
		]);

        // dataRequest is an object {name:<String>, url: <String>[,callback:<Function>]]}
        controller.getData({
                    name: 'filterData',
                    url: model.URLS.filterData, 
                    callback: filterUtil.publishFilteredData
                }) 

	},

	filteredData: [],
	
    getFilterValues: function(){
        var state = getState();

        //Extract just the filterValues stuff from our state
        //state is stored as filterValues.data_id with period as part of the object's key. 
        //TODO this only works w/ one level of dot notation nesting (probably all we need).
        var filterValues = {};
        for (key in state) {
            splitKey = key.split(".");
            if (splitKey[0]=='filterValues') {
                var currentState = state[key]
                filterValues[splitKey[1]] = currentState
            };
        };
        return filterValues
    },

	filterData: function(data){ 	
        
		var workingData = model.dataCollection['filterData'].items; 
		var filterValues = filterUtil.getFilterValues();

		for (key in filterValues) { // iterate through registered filters
			
            //need to get the matching component out of a list of objects
            var component = filterView.components.filter(function(obj) {
              return obj.source == key;
            });
            component = component[0] //the most recent filter (current and previous are returned in a list)
                        
			if (component['component_type'] == 'continuous') { //filter data for a 'continuous' filter
                
                if (filterValues[key][0].length == 0){
                    //don't filter because the filter has been removed
                } else {
                    //javascript rounding is weird
                    var decimalPlaces = component['data_type'] == 'integer' ? 0 : 2 //ternary operator
                    var min = Number(Math.round(filterValues[key][0][0]+'e'+decimalPlaces) +'e-'+decimalPlaces);
                    var max =Number(Math.round(filterValues[key][0][1]+'e'+decimalPlaces)+'e-'+decimalPlaces);

                    //filter it
                    workingData = workingData.filter(function(d){
    					return (d[key] >= min && d[key] <= max);
    				});
                };
			}

			if (component['component_type']== 'date') {
                
                workingData = workingData.filter(function(d){
                    // If the filter has returned to the original min/max values,
                    // reveal everything.
                    if(filterValues[key][0][0] == component.min && filterValues[key][0][1] == component.max){
                        return true;
                    }

                    // Projects with 'null' date values are not shown.
                    // TODO: Change this once we implement a toggle switch for showing
                    // null values
                    if(d[key] === null){
                         return false;
                    }

                    return d[key].getFullYear() > filterValues[key][0][0] && d[key].getFullYear() < filterValues[key][0][1];
                });

			}

			if (component['component_type'] == 'categorical') {
				workingData = workingData.filter(function(d){
                    //If all items are removed from filter list, assume they want all items
                    if (filterValues[key][0].length == 0 ) {
                        return true;
                    }
                    //otherwise use the list of chosen categories
					return filterValues[key][0].includes(d[key]);
				})
			}
		}

        //Convert the workingData to a list of ids to be published
        var ids = []
        for (key in workingData) {
            ids.push(workingData[key]['nlihc_id']);
        };
        filterUtil.filteredData = ids;
	},
	
	deduplicate: function(){
		var result = [];
		for (var i = 0; i < this.filteredData.length; i++) {
			if(!result.includes(this.filteredData[i])){
				result.push(this.filteredData[i]);
			}
		}
		filterUtil.filteredData = result;
	},
	
	publishFilteredData: function(){
        filterUtil.filterData();
		filterUtil.deduplicate();
		setState('filteredData', filterUtil.filteredData);
	}

};