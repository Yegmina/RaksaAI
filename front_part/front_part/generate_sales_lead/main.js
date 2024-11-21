document.getElementById("process-button").addEventListener("click", async () => {
    const fileInput = document.getElementById("file-input");
    const resultsDiv = document.getElementById("results");
    const loadingDiv = document.getElementById("loading");

    console.debug("DEBUG: Process button clicked");

    if (!fileInput.files.length) {
        alert("Please upload a JSON file.");
        console.debug("DEBUG: No file uploaded");
        return;
    }

    loadingDiv.style.display = "block"; // Show loading indicator
    resultsDiv.innerHTML = ""; // Clear previous results
    console.debug("DEBUG: Cleared previous results and displayed loading indicator");

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = async (event) => {
        try {
            console.debug("DEBUG: File loaded, starting JSON parsing");
            const data = JSON.parse(event.target.result);
            console.debug("DEBUG: Parsed JSON data successfully", data);

            const response = await fetch("http://127.0.0.1:5000/process", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });
            console.debug("DEBUG: Fetch request sent to server");

            if (!response.body) {
                console.error("DEBUG: No response body from server");
                throw new Error("No response body");
            }

            console.debug("DEBUG: Server response received, starting to read response body stream");
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let receivedText = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) {
                    console.debug("DEBUG: Stream reading completed");
                    break;
                }

                const chunk = decoder.decode(value, { stream: true });
                console.debug("DEBUG: Chunk received from server:", chunk);

                receivedText += chunk;

                try {
                    // Parse partial JSON as it is received
                    console.debug("DEBUG: Attempting to parse receivedText");
                    const partialData = JSON.parse(receivedText);
                    console.debug("DEBUG: Parsed partial data:", partialData);

                    resultsDiv.innerHTML = ""; // Clear existing results
                    console.debug("DEBUG: Cleared existing resultsDiv content");

                    partialData.results.forEach((item) => {
                        console.debug("DEBUG: Appending company data to resultsDiv", item);

                        const companyDiv = document.createElement("div");
                        companyDiv.innerHTML = `
                            <h2>${item.company_name}</h2>
                            <p><strong>Analysis:</strong> ${item.analysis}</p>
                            <p><strong>Sales Leads:</strong> ${item.sales_leads}</p>
                        `;
                        resultsDiv.appendChild(companyDiv);
                    });
                } catch (err) {
                    console.debug("DEBUG: JSON parse error or incomplete data, skipping to next chunk", err);
                }
            }

            loadingDiv.style.display = "none"; // Hide loading indicator
            console.debug("DEBUG: Loading indicator hidden, process completed");
        } catch (err) {
            loadingDiv.style.display = "none"; // Hide loading indicator
            console.error("DEBUG: Error during processing", err);
            alert("Failed to process the data. Check the console for details.");
        }
    };

    reader.readAsText(file);
    console.debug("DEBUG: File reading started");
});
