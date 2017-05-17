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
	totalUnitsMax: 5000,
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
				(filterOptions.subsidyStartBefore ? d['subsidy_start_date'] <= filterOptions.subsidyStartBefore : true) &&
				(filterOptions.subsidyStartafter ? d['subsidy_start_date'] >= filterOptions.subsidyStartafter : true) &&
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
	filter();
	filtered.forEach(function(arg){
		document.getElementById('result').textContent += arg['nlihc_id'] + ', '
	})
	console.log(filterOptions)
	console.log(filtered)

})