$(function () {
    // let's hit the JSON endpoint
    var containerDivId = "datasource-table";
    $.ajax({
        dataType: "json",
        url: "http://housinginsights.us-east-1.elasticbeanstalk.com/api/meta",
        success: function (data) {
            console.log(data);
            // This is the ID (accessed from a hidden div in the template)
            var id = document.getElementById(containerDivId).childNodes[0].id;
            console.log(id);
            if (!data[id]) {
                console.log("There is no data for this datasource! Please add some.");
                return false;
            }

            // from https://stackoverflow.com/questions/15164655/generate-html-table-from-2d-javascript-array
            var table = document.createElement('table');
            var tableBody = document.createElement('tbody');

            // Create the headers
            var headerRow = document.createElement('tr');

            var headerDisplayName = document.createElement('th');
            headerDisplayName.appendChild(document.createTextNode("Display Name"));
            headerRow.appendChild(headerDisplayName);

            var headerDisplayText = document.createElement('th');
            headerDisplayText.appendChild(document.createTextNode("Display Text"));
            headerRow.appendChild(headerDisplayText);
            tableBody.appendChild(headerRow);

            data[id].fields.forEach(function(rowData) {
              var row = document.createElement('tr');

              var displayName = document.createElement('td');
              displayName.appendChild(document.createTextNode(rowData.display_name));
              row.appendChild(displayName);

              var displayText = document.createElement('td');
              displayText.appendChild(document.createTextNode(rowData.display_text));
              row.appendChild(displayText);

              tableBody.appendChild(row);
            });

            table.appendChild(tableBody);
            document.getElementById(containerDivId).appendChild(table);
        }
    });
});
