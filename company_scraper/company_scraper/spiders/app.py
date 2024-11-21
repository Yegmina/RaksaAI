from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import csv
import os
import json

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

@app.route('/scrape', methods=['GET'])
def scrape():
    # Get CSV file path from query or default
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
            domain = url.split("//")[-1].split("/")[0]
            data_by_domain[domain] = {
                'url': url,
                'mainBusinessLine': row['mainBusinessLine.descriptions'],
                'pages': []
            }

    # Scrape each website
    for domain, details in data_by_domain.items():
        try:
            response = requests.get(details['url'], timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = ' '.join(soup.body.get_text().split())
            details['pages'].append({
                'page_url': details['url'],
                'content': content
            })
        except Exception as e:
            details['pages'].append({
                'page_url': details['url'],
                'content': f"Error fetching content: {str(e)}"
            })

    # Save to JSON file
    output_file = 'grouped_scraped_data.json'
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data_by_domain, json_file, ensure_ascii=False, indent=4)

    return jsonify({"message": f"Scraped data saved to {output_file}"})

if __name__ == '__main__':
    app.run(debug=True)
