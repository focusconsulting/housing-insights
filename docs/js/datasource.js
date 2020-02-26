$(function() {
  // let's hit the JSON endpoint
  var containerDivId = 'datasource-table';
  $.ajax({
    dataType: 'json',
    url: 'http://localhost:5000/api/meta',
    success: function(data) {
      // This is the ID (accessed from a hidden div in the template)
      var id = document.getElementById(containerDivId).childNodes[0].id;
      if (!data[id]) {
        console.log('There is no data for this datasource! Please add some.');
        return false;
      }

      // from https://stackoverflow.com/questions/15164655/generate-html-table-from-2d-javascript-array
      var table = document.createElement('table');

      // Create the headers
      var tableHead = document.createElement('thead');
      var headerRow = document.createElement('tr');

      var headerDisplayName = document.createElement('th');
      headerDisplayName.appendChild(document.createTextNode('Display Name'));
      headerRow.appendChild(headerDisplayName);

      var headerDisplayText = document.createElement('th');
      headerDisplayText.appendChild(document.createTextNode('Display Text'));
      headerRow.appendChild(headerDisplayText);

      tableHead.appendChild(headerRow);
      table.appendChild(tableHead);

      var tableBody = document.createElement('tbody');
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
