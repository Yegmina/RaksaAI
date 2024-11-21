document.getElementById('start-scraping').addEventListener('click', async () => {
    const fileInput = document.getElementById('csv-file');
    const statusElement = document.getElementById('status');
    const downloadLink = document.getElementById('download-link');

    if (!fileInput.files.length) {
        alert('Please upload a CSV file!');
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    // Upload CSV to the backend
    try {
        const uploadResponse = await fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData,
        });
        if (!uploadResponse.ok) throw new Error('Error uploading CSV file');

        // Start scraping
        const scrapeResponse = await fetch('http://127.0.0.1:5000/scrape');
        const scrapeResult = await scrapeResponse.json();

        if (scrapeResponse.ok) {
            statusElement.textContent = scrapeResult.message;
            downloadLink.href = 'grouped_scraped_data.json';
            downloadLink.style.display = 'block';
            downloadLink.textContent = 'Download Grouped JSON';
        } else {
            throw new Error(scrapeResult.error);
        }
    } catch (error) {
        statusElement.textContent = `Error: ${error.message}`;
    }
});
