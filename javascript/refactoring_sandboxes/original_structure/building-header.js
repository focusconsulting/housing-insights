

var buildingID;

var DATA_FILE;

var DataOnly = function(DATA_FILE){};
DataOnly.prototype = Object.create(Chart.prototype); 

new DataOnly(DATA_FILE);