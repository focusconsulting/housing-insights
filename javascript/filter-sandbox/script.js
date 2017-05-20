// var data = d3.json('./data.json', function(json){
// 	json.forEach(function(obj){
// 		for (var key in obj) {   
// 		            if (obj.hasOwnProperty(key)) {  // hasOwnProperty limits to own, nonprototypical properties.
		                                            
// 		                obj[key] = isNaN(+obj[key]) ? obj[key] : +obj[key]; // + operator converts to number unless result would be NaN
// 		            }
// 		        }
// 		// console.log(obj[key])
// 	})
// })



filterOptions = {
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

}

console.log(data);
var filtered = [];
filter = function(){
	filtered = data.filter(function(d){ 
		return (
			( //geography
				(filterOptions.ward ? d['ward'] === filterOptions.ward : true) &&
				(filterOptions.anc ? d['anc'] === filterOptions.anc : true) &&
				(filterOptions.censusTract ? d['census_tract'] === filterOptions.censusTract : true) &&
				(filterOptions.neighborhoodCluster ? d['neighborhood_id'] === filterOptions.neighborhoodCluster : true) &&
				(filterOptions.zip ? d['zip_code'] === filterOptions.zip : true)
			) && 
			( //subsidy start/end
				(filterOptions.subsidyStartBefore ? 
					(d['subsidy_start_date'] ? Date.UTC(d['subsidy_start_date'].split('-')[0],d['subsidy_start_date'].split('-')[1],d['subsidy_start_date'].split('-')[2]) <= Date.UTC(filterOptions.subsidyStartBefore.split('-')[0],filterOptions.subsidyStartBefore.split('-')[1],filterOptions.subsidyStartBefore.split('-')[2]) : false)
					: true) &&
				(filterOptions.subsidyEndBefore ? 
					(d['subsidy_end_date'] ? Date.UTC(d['subsidy_end_date'].split('-')[0],d['subsidy_end_date'].split('-')[1],d['subsidy_end_date'].split('-')[2]) >= Date.UTC(filterOptions.subsidyEndBefore.split('-')[0],filterOptions.subsidyEndBefore.split('-')[1],filterOptions.subsidyEndBefore.split('-')[2]) : false)
					: true) &&
				(filterOptions.subsidyendBefore ? d['subsidy_end_date'] <= filterOptions.subsidyendBefore : true) &&
				(filterOptions.subsidyendAfter ? d['subsidy_end_date'] >= filterOptions.subsidyendAfter : true)
			) && 
			( //number of units
				(filterOptions.totalUnitsMin ? parseInt(d['total_units_in_building']) >= filterOptions.totalUnitsMin : true) &&
				(filterOptions.totalUnitsMax ? parseInt(d['total_units_in_building']) <= filterOptions.totalUnitsMax : true) &&
				(filterOptions.totalSubsidizedUnitsMin ? parseInt(d['total_subsidized_units_in_building']) >= filterOptions.totalSubsidizedUnitsMin : true) &&
				(filterOptions.totalSubsidizedUnitsMax ? parseInt(d['total_subsidized_units_in_building']) <= filterOptions.totalSubsidizedUnitsMax : true)
			) &&
			(filterOptions.ownershipType ? d['building_ownership_type'] === filterOptions.ownershipType : true) &&
			(filterOptions.subsidyType ? d['subsidy_program'] === filterOptions.subsidyType : true)
		)
	});
}


filtered.forEach(function(obj){
	console.log(obj['total_units_in_building']);
})

document.getElementById('filter').addEventListener('click', function(){
	document.getElementById('result').textContent = "";
	console.log('blah')
	filterOptions.totalUnitsMin = document.getElementById('min').value;
	filterOptions.totalUnitsMax = document.getElementById('max').value;
	filterOptions.subsidyStartBefore = document.getElementById('date-start').value;
	filterOptions.subsidyEndBefore = document.getElementById('date-end').value;
	filter();
	filtered.forEach(function(arg){
		// console.log(Date.UTC(arg['subsidy_start_date'].split('-')[0],arg['subsidy_start_date'].split('-')[1],arg['subsidy_start_date'].split('-')[2]))
		// console.log(Date.UTC(filterOptions.subsidyStartBefore.split('-')[0],filterOptions.subsidyStartBefore.split('-')[1],filterOptions.subsidyStartBefore.split('-')[2]))
		document.getElementById('result').textContent += arg['nlihc_id'] + ', '
	})
	console.log(filtered.length)

})