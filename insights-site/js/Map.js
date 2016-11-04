//Map projection
var projection = d3.geo.mercator()
    .scale(87238.56343084128)
    .center([-77.0144701798118, 38.89920210515231]) //projection center
    .translate([$('#mapView').width() / 2,
        $('#mapView').height() / 2]); //translate to center the map in view
  
//Generate paths based on projection
var path = d3.geo.path()
    .projection(projection);
  
//Define icons for detailView
var iconOpaq = d3.scale.ordinal()
    .domain(["Beer", "Wine", "Liquor"])
    .range(["M23,1L22.5,5H7.5L7,1H5L8,29H22L25,1H23Z",
        "M26.82,18H3.06C3,19,3,19.32,3,20c0,6.13,6.92,9,6.92,9H20s6.92-2.87,6.92-9C26.88,19.32,26.86,18.65,26.82,18Z",
        "M25,1V15H5V1H3V29H27V1H25ZM7.57,27.69L5.31,22.26,10.74,20,13,25.43Zm4.37-5.82,2.47-5.34L19.75,19l-2.47,5.34ZM25,28H19V22h6v6Z"]);

var iconTrans = d3.scale.ordinal()
    .domain(["Beer", "Wine", "Liquor"])
    .range(["M7,1L7.5,5h15L23,1H7Z",
        "M21.4,1H8.48A34.84,34.84,0,0,0,3.06,18H26.82A34.84,34.84,0,0,0,21.4,1Z",
        "M5,1V25c0,1,0,3,2,3H25V1H5Z"]);
          
//Define zipcode neighborhood names
var neighborhoodName = d3.scale.ordinal()
    .domain(["Washington, DC",
        "National Mall",
        "20009",
        "20007",
        "20002",
        "20016",
        "20008",
        "20010",
        "20036",
        "20005",
        "20037",
        "20003",
        "20032",
        "20020",
        "20019",
        "20024",
        "20004",
        "20006",
        "20001",
        "20018",
        "20017",
        "20011",
        "20012",
        "20015"])
    .range(["Washington, DC",
        "National Mall",
        "Adams Morgan, N.Dupont, U Street",
        "Georgetown, Glover Park",
        "Eckington, H Street, N.Capitol Hill",
        "Tenleytown, The Palisades",
        "Van Ness, Woodley Park",
        "Columbia Heights, Mount Pleasant",
        "S.Dupont",
        "Logan Circle",
        "West End, W.Foggy Bottom, ",
        "Armory, Navy Yard, S.Capitol Hill",
        "Bellevue, Congress Heights",
        "Anacostia, Buena Vista, Fairlawn",
        "Deanwood, Marshall Heights",
        "Southwest Waterfront",
        "Penn Quarter",
        "Farragut Square, E.Foggy Bottom",
        "Bloomingdale, Chinatown, Shaw",
        "Brentwood, E.Brookland, Langdon",
        "Michigan Park, W.Brookland",
        "Crestwood, Fort Totten, Petworth",
        "Brightwood, Takokma",
        "Chevy Chase, Friendship Heights", ]);  
            
//Initial population of detailView    
detailView("Washington, DC");
  
//Define Colorscales for mapView
var colorScaleMap = d3.scale.ordinal()
    .domain(["T", "F"])
    .range(["#0097FF", "#c8c8c8"]);

var colorScaleActiveMap = d3.scale.ordinal()
    .domain(["T", "F"])
    .range(["#FF9700", "#c8c8c8"]);
  
//Define tooltip
var tooltip = d3.select("body").append("div").attr("class", "tooltip");
  
//Define position of the tooltip relative to the cursor
var tooltipOffset = { x: 5, y: -25 };
   
//Define function for populating detail view
function detailView(location) {
    
    d3.csv("MapData.csv", function(data){

    //Filter to only those observations that match the current location
    dataSubset = data.filter(function(locID) {
        return locID.location == location;
    });
    
    //If there's actually an data for the select location...
    if (dataSubset.length > 1) {
    
        //Clear detailView
        $('#detailView').html('');
        
        //Select detailView   
        var detailView = d3.select("#detailView")
        
        //Add location text to top of detailView
        detailView.append("text")
            .attr("text-anchor", "middle")
            .attr("x", "160px")
            .attr("y", "18px")
            .attr("font-size", "18px")
            .attr("font-weight", "Bold")
            .text("Top 10 brands in...");

        detailView.append("text")
            .attr("text-anchor", "middle")
            .attr("x", "160px")
            .attr("y", "38px")
            .attr("font-size", "16px")
            .text(neighborhoodName(location));

        //Append Text labels to detailView
        detailView.append("g").selectAll("preferenceText")
            .data(dataSubset)
            .enter()
            .append("text")
            .classed("preferenceText", true)
            .text(function (d, i) {
                return d.item;
            })

            .attr("x", 50)
            .attr("y", function (d, i) {
                var yTemp = ($('#detailView').height() - 85) / 9 * i + 70
                return yTemp + 4;
            });
            
        //Append category icon to detailView     
        var prefIcon = detailView.selectAll("prefIcon") //Create the group
            .data(dataSubset)
            .enter()
            .append("g")
            .attr("class", function (d, i) {
                return d.itemCategory;
            });

        prefIcon.append("path") //Create and position the opaque portion of the icon
            .attr("d", function (d, i) {
                return iconOpaq(d.itemCategory);
            })
            .attr("transform", function (d, i) {
                var yTemp = ($('#detailView').height() - 85) / 9 * i + 53;
                return "translate(" + 0 + "," + yTemp + ")";
            });

        prefIcon.append("path") //Create and position the transparant portion of the icon
            .attr("d", function (d, i) {
                return iconTrans(d.itemCategory);
            })
            .attr("opacity", ".5") //Set the level of transparency
            .attr("transform", function (d, i) {
                var yTemp = ($('#detailView').height() - 85) / 9 * i + 53;
                return "translate(" + 0 + "," + yTemp + ")";
            });
            
        //Append rank order labels to detailView
        detailView.append("g").selectAll("preferenceRank")
            .data(dataSubset)
            .enter()
            .append("text")
            .classed("preferenceRank", true)
            .text(function (d, i) {
                return i + 1;
            })
            .attr("x", 15)
            .attr("y", function (d, i) {
                return ($('#detailView').height() - 85) / 9 * i + 73;
            })
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .attr("font-size", "15px")
            .attr("font-weight", "bold");
    };
    });
};
     
//Define function for populating mapView 

  d3.json("DCzipcodes.geojson", function (geodata) {
var map = d3.select("#mapView").append("g").classed("DC", true)

map.selectAll("path")
    .data(geodata.features)
    .enter()
    .append("path")
    .classed("zipcodes", true)
    .attr("d", path)
    .attr("fill", function (d, i) {
        return colorScaleMap(d.properties.haveData);
    })
    .on("click", enterDetail)
    .on("mouseover", enterTooltip)
    .on("mousemove", refreshTooltip)
    .on("mouseout", exitTooltip);
  });
    
//Define function to populate detailView
var selected // declare the centered variable globally
    
function enterDetail(d, i) {
    var loc;

    var x, y, k;

    if (d && selected !== d) {
        //var centroid = path.centroid(d);
        //x = centroid[0];
        //y = centroid[1];
        //k = 2.5;
        selected = d;
        loc = d.properties.zipcode
        
        d3.selectAll(".zipcodes").attr("fill", function (d, i) {
            return colorScaleMap(d.properties.haveData);
        });
        
        d3.select(this).attr("fill", function (d, i) {
            return colorScaleActiveMap(d.properties.haveData);
        });

    } else {
        //x = $("#mapView").width() / 2;
        //y = $("#mapView").height() / 2;
        //k = 1;
        selected = null;
        loc = "Washington, DC";
        
        d3.selectAll(".zipcodes").attr("fill", function (d, i) {
            return colorScaleMap(d.properties.haveData);
        });
    }

    d3.selectAll(".DC")
        .classed("active", selected && function (d) { return d === selected; });

    d3.selectAll(".DC").transition()
        .duration(750)
        .attr("transform", "translate(" + $('#mapView').width() / 2 + "," + $('#mapView').height() / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
        .style("stroke-width", 1.5 / k + "px");
    detailView(loc);
}

//Define function to reset detailView to Washington, DC   
function exitDetail(d, i) {
    detailView("Washington, DC");
        d3.selectAll(".zipcodes").attr("fill", function (d, i) {
            return colorScaleMap(d.properties.haveData);
        });
}
  
//Define functions to update tooltip location and map coloration
function enterTooltip(d, i) {
    tooltip.style("display", "block")
        .text(neighborhoodName(d.properties.zipcode));
    //.text(d.properties.zipcode);

    //d3.select(this).attr("fill", function (d, i) {
    //    return colorScaleActiveMap(d.properties.haveData);
    //});
}

function refreshTooltip() {
    tooltip.style("top", (d3.event.pageY + tooltipOffset.y) + "px")
        .style("left", (d3.event.pageX + tooltipOffset.x) + "px");
}

//Define function to remove tooltip on exit 
function exitTooltip() {
    tooltip.style("display", "none");

    //d3.select(this).attr("fill", function (d, i) {
    //    return colorScaleMap(d.properties.haveData);
    //});
}