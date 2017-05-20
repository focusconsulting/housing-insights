var filter = {
	init: function(){
		setSubs([
			['filterChange', filter.publishFilteredData]
		]);
	},
	options: { // TODO replace with a function that populates this according
				// to data from the API
		ward: '',
		anc: '',
		censusTract: '',
		neighborhoodCluster: '',
		zip: '',
		totalUnitsMin: '',
		totalUnitsMax: '',
		totalSubsidizedUnits: '',
		ownershipType: '',
		subsidyType: '',
		subsidyStartBefore: '',
		subsidyStartAfter: '',
		subsidyEndBefore: '',
		subsidyEndAfter: ''
	},
	filteredData: [],
	filterData: function(data){
		this.filteredData = data.filter(function(d){ 
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
	},
	deduplicate: function(){
		var result = [];
		for (var i = 0; i < this.filteredData.length; i++) {
			if(!result.includes(this.filteredData[i])){
				result.push(this.filteredData[i]);
			}
		}
		this.filteredData = result;
	},
	publishFilteredData: function(msg,options){
		this.options[options.key] = options.value;
		this.filterData();
		this.deduplicate();
		setState('filteredData', this.filteredData);
	}
}