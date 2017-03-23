/* function to get parameter value from query string in url */

function getParameterByName(name, url) { // HT http://stackoverflow.com/a/901144/5701184
    if (!url) {
      url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

var buildingID = getParameterByName('building');

var DATA_FILE ='data/Project.csv';

var DataOnly = function(DATA_FILE){  // set up kind of dummy constructor that inherits from Chart but does nothing else.
                                     // just to get the data from DATA_FILE and put it in the dataCollection
 Chart.call(this, DATA_FILE);
 this.setup = function(){ // to avoid error of this.setup being called by Chart prototype
    console.log(this.data);
    var data = this.data;
    var d = data.filter(function(obj){
        
        return obj.Proj_address_id === parseInt(buildingID);
    });
    console.log(d);
    d = d[0];
    document.getElementById('building-name').innerText = d.Proj_Name;
    document.getElementById('building-street').innerText = d.Proj_Addre;
    document.getElementById('building-ward').innerText = d.Ward2012;
    document.getElementById('building-cluster').innerText = d.Cluster_tr2000;
    document.getElementById('owner-name').innerText = d.Hud_Own_Name == 0 ? 'not in data file' : d.Hud_Own_Name;
    document.getElementById('owner-phone').innerText = 'for placement only (need join other data)';
    document.getElementById('tax-assessment-amount').innerText = 'for placement only (need join other data)';


 };


};

DataOnly.prototype = Object.create(Chart.prototype); 

new DataOnly(DATA_FILE);