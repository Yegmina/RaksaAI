from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yaml
import json
from gemini import GeminiModel
import time

app = Flask(__name__)
CORS(app)

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")  # Serve index.html from the current directory

@app.route("/<path:filename>")
def serve_static_files(filename):
    return send_from_directory(".", filename)  # Serve other static files like main.js

@app.route("/process", methods=["POST"])
def process_data():
    try:
        data = request.json
        prompts = load_prompts("prompts.yaml")
        gemini_model = GeminiModel(model_name="gemini-1.5-flash")

        results = []
        for company_name, company_info in data.items():
            time.sleep(3)
            scraped_data = f"""
            Company Name: {company_name}
            Industry: {company_info.get('mainBusinessLine', 'N/A')}
            Website: {company_info.get('url', 'N/A')}
            """
            pages = company_info.get("pages", [])
            if pages:
                scraped_data += "\nPages:\n"
                for page in pages:
                    scraped_data += f"- {page['page_url']}: {page['content'][:100]}...\n"

            analysis, sales_leads = process_company(scraped_data, gemini_model, prompts)
            results.append({
                "company_name": company_name,
                "analysis": analysis,
                "sales_leads": sales_leads
            })

        return jsonify({"status": "success", "results": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def load_prompts(prompt_file="prompts.yaml"):
    with open(prompt_file, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def process_company(scraped_data, gemini_model, prompts):
    interpret_system = prompts['interpret_scraping']['system_prompt']
    interpret_user = prompts['interpret_scraping']['user_prompt'].replace("{{scraped_data}}", scraped_data)
    analysis = gemini_model.call_model(user_prompt=interpret_user, system_prompt=interpret_system)

    leads_system = prompts['generate_leads']['system_prompt']
    leads_user = prompts['generate_leads']['user_prompt'].replace("{{analysis}}", analysis)
    sales_leads = gemini_model.call_model(user_prompt=leads_user, system_prompt=leads_system)

    return analysis, sales_leads

if __name__ == "__main__":
    app.run(debug=True)
