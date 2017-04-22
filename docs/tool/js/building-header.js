

var buildingID = app.getParameterByName('building');

var DATA_FILE ='data/Project.csv';

var DataOnly = function(DATA_FILE){  // set up kind of dummy constructor that inherits from Chart but does nothing else.
                                     // just to get the data from DATA_FILE and put it in the dataCollection
 Chart.call(this, DATA_FILE);
 this.setup = function(){ // to avoid error of this.setup being called by Chart prototype
    var data = this.data;
    var d = data.filter(function(obj){
        
        return obj.Nlihc_id === buildingID;
    });
    d = d[0];
    document.getElementById('building-name').innerText = d.Proj_Name;
    document.getElementById('building-street').innerText = d.Proj_Addre;
    document.getElementById('building-ward').innerText = d.Ward2012;
    document.getElementById('building-cluster').innerText = d.Cluster_tr2000;
    document.getElementById('owner-name').innerText = d.Hud_Own_Name == 0 ? 'not in data file' : d.Hud_Own_Name;
    document.getElementById('owner-phone').innerText = 'for placement only (need join other data)';
    document.getElementById('tax-assessment-amount').innerText = 'for placement only (need join other data)';

    prepareBuildingMaps(d.Proj_lat,d.Proj_lon)

 };


};

DataOnly.prototype = Object.create(Chart.prototype); 

new DataOnly(DATA_FILE);