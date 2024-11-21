document.getElementById("process-button").addEventListener("click", async () => {
    const fileInput = document.getElementById("file-input");
    const resultsDiv = document.getElementById("results");
    const loadingDiv = document.getElementById("loading");

    if (!fileInput.files.length) {
        alert("Please upload a JSON file.");
        return;
    }

    loadingDiv.style.display = "block"; // Show loading indicator

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = async (event) => {
        try {
            const data = JSON.parse(event.target.result);

            const response = await fetch("http://127.0.0.1:5000/process", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            loadingDiv.style.display = "none"; // Hide loading indicator

            if (result.status === "success") {
                resultsDiv.innerHTML = ""; // Clear old results
                result.results.forEach((item) => {
                    const companyDiv = document.createElement("div");
                    companyDiv.innerHTML = `
                        <h2>${item.company_name}</h2>
                        <p><strong>Analysis:</strong> ${item.analysis}</p>
                        <p><strong>Sales Leads:</strong> ${item.sales_leads}</p>
                    `;
                    resultsDiv.appendChild(companyDiv);
                });
            } else {
                alert("Error: " + result.message);
            }
        } catch (err) {
            loadingDiv.style.display = "none"; // Hide loading indicator
            console.error("Failed to process the data.", err);
            alert("Failed to process the data. Check the console for details.");
        }
    };

    reader.readAsText(file);
});
