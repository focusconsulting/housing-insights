var filterUtil = {
	
	init: function(){
		setSubs([
			['filterValues', filterUtil.publishFilteredData],
			// need to subscribe to data load and run a save the data
		]);
	},


	components: [
        //TODO this hard coded array of objects is just a temporary method. 
        //This should be served from the API, probably from meta.json
        //"source" is the column name from the filter table, which should match the table in the original database table. 
        //  For this approach to work, it will be cleanest if we never have duplicate column names in our sql tables unless the data has
        //  the same meaning in both places (e.g. 'ward' and 'ward' can appear in two tables but should have same name/format)

        {   source: 'proj_units_tot',
            display_name: 'Project unit count',
            component_type: 'continuous',
            data_type:'integer',
            min: 5,
            max: 200,
            num_decimals_displayed: 0 //0 if integer, 1 otherwise. Could also store data type instead. 
        },
        {   source: 'acs_rent_median',
            display_name: 'Neighborhood Rent (ACS median)',
            component_type: 'continuous',
            data_type:'decimal',
            min: 0,
            max: 2500,
            num_decimals_displayed: 0 //0 if integer, 1 otherwise. Could also store data type instead. 
        },
        {   source:'poa_start',
            component_type: 'date',
            data_type: 'timestamp',
            min: '1950-01-01', //just example, TODO change to date format
            max: 'now'         //dummy example
        },
        {   source:'ward',
            component_type: 'categorical',
            data_type: 'text',
            other: 'feel free to add other needed properties if they make sense'
        }
    ],

    componentsKey: {
    	'proj_units_tot': 0,
		'acs_rent_median': 1,
		'poa_start': 2,
		'ward': 3
    },


	options: {}, //this object acts as a registry for filters

	filteredData: [],
	
	filterData: function(data){ 

		//TODO dummy list with one duplicate to demonstrate publication of a list of filtered IDs
		filterUtil.filteredData = ['NL000001','NL000368','NL000008','NL000001']
		
		var workingData = data; // TODO bring data in from somewhere
		
		for (option in filterUtil.options) { // iterate through registered filters
			
			var component = filterUtil.components[filterUtil.componentKey[option]];
			
			if (component.component_type == 'continuous') { //filter data for a 'continuous' filter
				workingData = workingData.filter(function(d){
					return (d[option] >= filterUtil.options[option][0] && d[option] <= filterUtil.options[option][1]);
				})
			}

			if (component.component_type == 'date') {
				//TODO determine whether dates will always be published as [start, end], or, if
				// not, in what format
			}

			if (component.component_type == 'categorical') {
				workingData = workingData.filter(function(d){
					return filterUtil.options[option].includes(d[option]);
				})
			}
		}

		// filterUtil.filteredData = workingData;

		//TODO This will need to be rewritten using a structure based on the logic we used to create the filter elements in filter-view.js
		//For example, filter columns need to be named based on the 'source' name, and the logic structure should not be hard coded
		//in for the column names but rather be based on the 'component_type' i.e. continuous, date, etc. and 'data_type' (for example, 'integer' should
		//automatically round to 0 decimals and 'decimal' should round to 2 decimals)
		
		/*data.filter(function(d){ 
			return (
				( //geography
					(this.options.ward ? d['ward'] === this.options.ward : true) &&
					(this.options.anc ? d['anc'] === this.options.anc : true) &&
					(this.options.censusTract ? d['census_tract'] === this.options.censusTract : true) &&
					(this.options.neighborhoodCluster ? d['neighborhood_id'] === this.options.neighborhoodCluster : true) &&
					(this.options.zip ? d['zip_code'] === this.options.zip : true)
				) && 
				( //subsidy start/end
					(this.options.subsidyStartBefore ? 
						(d['subsidy_start_date'] ? Date.UTC(d['subsidy_start_date'].split('-')[0],d['subsidy_start_date'].split('-')[1],d['subsidy_start_date'].split('-')[2]) <= Date.UTC(this.options.subsidyStartBefore.split('-')[0],this.options.subsidyStartBefore.split('-')[1],this.options.subsidyStartBefore.split('-')[2]) : false)
						: true) &&
					(this.options.subsidyEndBefore ? 
						(d['subsidy_end_date'] ? Date.UTC(d['subsidy_end_date'].split('-')[0],d['subsidy_end_date'].split('-')[1],d['subsidy_end_date'].split('-')[2]) >= Date.UTC(this.options.subsidyEndBefore.split('-')[0],this.options.subsidyEndBefore.split('-')[1],this.options.subsidyEndBefore.split('-')[2]) : false)
						: true) &&
					(this.options.subsidyendBefore ? d['subsidy_end_date'] <= this.options.subsidyendBefore : true) &&
					(this.options.subsidyendAfter ? d['subsidy_end_date'] >= this.options.subsidyendAfter : true)
				) && 
				( //number of units
					(this.options.totalUnitsMin ? parseInt(d['total_units_in_building']) >= this.options.totalUnitsMin : true) &&
					(this.options.totalUnitsMax ? parseInt(d['total_units_in_building']) <= this.options.totalUnitsMax : true) &&
					(this.options.totalSubsidizedUnitsMin ? parseInt(d['total_subsidized_units_in_building']) >= this.options.totalSubsidizedUnitsMin : true) &&
					(this.options.totalSubsidizedUnitsMax ? parseInt(d['total_subsidized_units_in_building']) <= this.options.totalSubsidizedUnitsMax : true)
				) &&
				(this.options.ownershipType ? d['building_ownership_type'] === this.options.ownershipType : true) &&
				(this.options.subsidyType ? d['subsidy_program'] === this.options.subsidyType : true)
			)
		});
		*/
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
	
	publishFilteredData: function(msg,options){
		filterUtil.options[msg.split('.')[1]] = options; // register filter in the options object
		filterUtil.filterData();  // needs a data argument
		filterUtil.deduplicate();
		setState('filteredData', filterUtil.filteredData);
	}

};