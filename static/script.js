// script.js

document.addEventListener('DOMContentLoaded', function () {
    // Function to update the table with data received from the server
    function updateTable(data) {
        // Clear the existing table rows
        var tbody = document.querySelector('#resultTable tbody');
        tbody.innerHTML = '';

        // Iterate over the data and add rows to the table
        Object.keys(data).forEach(function (label) {
            data[label].forEach(function (comment) {
                var row = document.createElement('tr');
                var commentCell = document.createElement('td');
                var labelCell = document.createElement('td');
                
                commentCell.textContent = comment;
                labelCell.textContent = label;

                row.appendChild(commentCell);
                row.appendChild(labelCell);

                tbody.appendChild(row);
            });
        });
    }

    // Function to fetch data from the server and update the table
    function fetchData() {
        fetch('/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            updateTable(data);
        })
        .catch(function (error) {
            console.error('Error fetching data:', error);
        });
    }

    // Call fetchData function initially to populate the table
    fetchData();

    // Set interval to periodically fetch and update data
    setInterval(fetchData, 5000); // Update every 5 seconds (adjust as needed)
});
