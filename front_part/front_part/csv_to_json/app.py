from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import csv
import os
import json
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

def is_same_domain(base_url, target_url):
    """Check if the target_url belongs to the same domain as base_url."""
    return urlparse(base_url).netloc == urlparse(target_url).netloc

def scrape_website(base_url, max_pages=10):
    """
    Recursively scrape pages from the base URL up to a maximum number of pages.
    """
    visited = set()
    pages = []

    def scrape_page(url):
        if url in visited or len(pages) >= max_pages:
            return
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract and clean the content
            content = ' '.join(soup.body.get_text().split())
            pages.append({"page_url": url, "content": content})
            visited.add(url)

            # Find all internal links
            for link in soup.find_all('a', href=True):
                next_url = urljoin(base_url, link['href'])
                if is_same_domain(base_url, next_url) and next_url not in visited:
                    scrape_page(next_url)  # Recursive call
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    scrape_page(base_url)
    return pages

@app.route('/scrape', methods=['GET'])
def scrape():
    csv_path = request.args.get('csv', 'relevant_companies_last_search.csv')

    # Ensure the CSV file exists
    if not os.path.exists(csv_path):
        return jsonify({"error": "CSV file not found"}), 404

    # Load company data from CSV
    data_by_domain = {}
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row['website.url']
            if not url.startswith('http'):
                url = f"http://{url}"
            domain = urlparse(url).netloc
            data_by_domain[domain] = {
                'url': url,
                'mainBusinessLine': row['mainBusinessLine.descriptions'],
                'pages': []
            }

    # Scrape each domain
    for domain, details in data_by_domain.items():
        details['pages'] = scrape_website(details['url'], max_pages=10)

    # Save to JSON file
    output_file = 'grouped_scraped_data.json'
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data_by_domain, json_file, ensure_ascii=False, indent=4)

    return jsonify({"message": f"Scraped data saved to {output_file}"})
    

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    file.save('relevant_companies_last_search.csv')
    return jsonify({"message": "File uploaded successfully"})

if __name__ == '__main__':
    app.run(debug=True)
