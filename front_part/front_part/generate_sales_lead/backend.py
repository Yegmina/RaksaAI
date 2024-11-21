from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
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

        def generate_responses():
            yield '{"status": "success", "results": ['
            first = True
            for company_name, company_info in data.items():
                if not first:
                    yield ','
                first = False
                
                time.sleep(3)  # Simulate delay
                
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
                result = {
                    "company_name": company_name,
                    "analysis": analysis,
                    "sales_leads": sales_leads
                }
                yield json.dumps(result)
            yield ']}'

        return Response(stream_with_context(generate_responses()), content_type="application/json")

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

    # Format the analysis and sales leads for proper HTML rendering
    def format_to_html(text):
        lines = text.splitlines()
        html_lines = []
        for line in lines:
            line = line.strip()  # Trim leading/trailing spaces
            if not line:  # Skip empty lines
                continue
            
            # Handle bold formatting
            if line.startswith("**") and line.endswith("**"):
                line = f"<b>{line[2:-2]}</b>"
            elif "**" in line:  # Bold key-value pairs like "**Key:** Value"
                line = line.replace("**", "<b>", 1).replace("**", "</b>", 1)
            
            # Identify list hierarchy
            if line.startswith("I."):  # Main numbered list
                html_lines.append(f"<li><b>{line}</b></li>")
            elif line.startswith("* **"):  # Nested bold list item
                html_lines.append(f"<ul><li>{line}</li></ul>")
            elif line.startswith("* "):  # Simple bullet list
                html_lines.append(f"<li>{line[2:]}</li>")
            else:  # Plain text
                html_lines.append(f"<p>{line}</p>")
        
        return f"<ul>{''.join(html_lines)}</ul>"
        
        

    analysis_html = f"<b>Analysis:</b>{format_to_html(analysis)}"
    sales_leads_html = f"<b>Sales Leads:</b>{format_to_html(sales_leads)}"

    return analysis_html, sales_leads_html



if __name__ == "__main__":
    app.run(debug=True)
