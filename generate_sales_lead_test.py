import yaml
from gemini import GeminiModel 
import json

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
    with open("company_scraper/grouped_scraped_data.json", "r", encoding="utf-8") as file:
        company_data = json.load(file)

    prompts = load_prompts("prompts.yaml")
    if not prompts:
        exit("Failed to load prompts. Exiting.")

    gemini_model = GeminiModel(model_name="gemini-1.5-flash")

    for company_name, company_info in company_data.items():
        print(f"Processing company: {company_name}")

        # Format scraped data
        scraped_data = f"""
        Company Name: {company_name}
        Industry: {company_info.get('mainBusinessLine', 'N/A')}
        Website: {company_info.get('url', 'N/A')}
        """

        # Include page content if available
        pages = company_info.get("pages", [])
        if pages:
            scraped_data += "\nPages:\n"
            for page in pages:
                scraped_data += f"- {page['page_url']}: {page['content'][:100]}...\n"

        # Call LLM
        analysis, sales_leads = process_company(scraped_data, gemini_model, prompts)

        # Print results
        print("Analysis:")
        print(analysis)
        print("\nSales Leads:")
        print(sales_leads)
        print("-" * 40)