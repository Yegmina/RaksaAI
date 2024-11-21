document.getElementById("process-button").addEventListener("click", async () => {
    const fileInput = document.getElementById("file-input");
    const resultsDiv = document.getElementById("results");
    const loadingDiv = document.getElementById("loading");

    if (!fileInput.files.length) {
        alert("Please upload a JSON file.");
        return;
    }

    loadingDiv.style.display = "block"; // Show loading indicator
    resultsDiv.innerHTML = ""; // Clear previous results

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

            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let receivedText = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                receivedText += decoder.decode(value, { stream: true });

                try {
                    // Parse partial JSON as it is received
                    const partialData = JSON.parse(receivedText);
                    resultsDiv.innerHTML = ""; // Clear existing results
                    partialData.results.forEach((item) => {
                        const companyDiv = document.createElement("div");
                        companyDiv.innerHTML = `
                            <h2>${item.company_name}</h2>
                            <p><strong>Analysis:</strong> ${item.analysis}</p>
                            <p><strong>Sales Leads:</strong> ${item.sales_leads}</p>
                        `;
                        resultsDiv.appendChild(companyDiv);
                    });
                } catch (err) {
                    // Ignore errors until JSON is complete
                }
            }

            loadingDiv.style.display = "none"; // Hide loading indicator
        } catch (err) {
            loadingDiv.style.display = "none"; // Hide loading indicator
            console.error("Failed to process the data.", err);
            alert("Failed to process the data. Check the console for details.");
        }
    };

    reader.readAsText(file);
});
