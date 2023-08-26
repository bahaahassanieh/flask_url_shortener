document.addEventListener("DOMContentLoaded", function() {
    // Assuming the short code is passed in the URL as a query parameter, e.g., ?code=abc123
    const urlParams = new URLSearchParams(window.location.search);
    const shortCode = urlParams.get('code');

    if (shortCode) {
        document.getElementById("shortCode").innerText = shortCode;

        // Fetch analytics data from the Flask API
        fetch(`/analytics/${shortCode}`)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.getElementById("analyticsData");

                // Clear existing data
                tableBody.innerHTML = "";

                // Populate the table with fetched data
                data.forEach(row => {
                    const tr = document.createElement("tr");

                    const dateTd = document.createElement("td");
                    dateTd.innerText = row.click_date;

                    const clicksTd = document.createElement("td");
                    clicksTd.innerText = row.daily_clicks;

                    const urlTd = document.createElement("td");
                    urlTd.innerText = row.original_url;

                    tr.appendChild(dateTd);
                    tr.appendChild(clicksTd);
                    tr.appendChild(urlTd);

                    tableBody.appendChild(tr);
                });
            })
            .catch(error => {
                console.error("Error fetching analytics data:", error);
            });
    }
});
