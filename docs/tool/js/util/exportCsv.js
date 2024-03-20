"use strict";

var exportCsv = {
  init: function () {
    setSubs([
      ["exportJsonAsCsv", exportCsv.exportJsonAsCsv],
      ["exportAllData", exportCsv.exportAllData],
    ]);
  },

  exportJsonAsCsv: function (headerKeys, jsonContent, filename) {
    var csvContent = "data:text/csv;charset=utf-8,";
    csvContent += Papa.unparse({
      fields: headerKeys,
      data: jsonContent,
    });

    // //Create a csv from the data manually
    // var csvContent = "data:text/csv;charset=utf-8,";
    // var keys = "matches_filters,";
    // Object.keys(allData.objects[0]).forEach(function(key){
    //   if ( key !== "matches_filters"){
    //     keys += key + ",";
    //   }
    // })
    // csvContent += keys + '\n';
    // matchesData.forEach( function(project){
    //   csvContent += String(project['matches_filters']) + ",";
    //   Object.keys(project).forEach( function(key){
    //     if ( key !== "matches_filters"){
    //       csvContent += String(project[key]).replace(/,/g,' ') + ",";
    //     }
    //   })
    //   csvContent += '\n';
    // })
    // notMatchesData.forEach( function(project){
    //   csvContent += String(project['matches_filters']) + ",";
    //   Object.keys(project).forEach( function(key){
    //     if ( key !== "matches_filters"){
    //       csvContent += String(project[key]).replace(/,/g,' ') + ",";
    //     }
    //   })
    //   csvContent += '\n';
    // })
    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link); // Required for FF

    link.click(); // This will download the data file named "projects.csv".
  },

  exportAllData: function () {
    console.log("INFO Exporting sorted all data");

    var allData = mapView.convertedProjects.features.map(function (feature) {
      return feature.properties;
    });
    var matchesData = allData.filter(function (feature) {
      return feature.matches_filters === true;
    });
    var notMatchesData = allData.filter(function (feature) {
      return feature.matches_filters === false;
    });
    var orderedData = matchesData.concat(notMatchesData);
    console.log(orderedData[0]);
    var keys = ["matches_filters"];
    Object.keys(orderedData[0]).forEach(function (key) {
      if (key !== "matches_filters") {
        keys.push(key);
      }
    });

    exportCsv.exportJsonAsCsv(keys, orderedData, "projects.csv");
  },
};
