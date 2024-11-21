import os
import csv
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CompanySpider(CrawlSpider): #run command for testing: scrapy crawl company_spider -a company_limit=3
    name = 'company_spider'

    def __init__(self, company_limit=None, *args, **kwargs):
        super(CompanySpider, self).__init__(*args, **kwargs)

        # Convert company_limit to an integer if provided
        self.company_limit = int(company_limit) if company_limit else None

        # Construct the path to the CSV file
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        csv_path = os.path.join(project_root, 'relevant_companies_last_search.csv')

        # Ensure the file exists
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")

        # Load start URLs
        self.start_urls = []
        self.data_by_domain = {}
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if self.company_limit and i >= self.company_limit:
                    break  # Stop reading when the limit is reached
                url = row['website.url']
                if not url.startswith('http'):
                    url = 'http://' + url
                self.start_urls.append(url)
                domain = url.split("//")[-1].split("/")[0]
                self.data_by_domain[domain] = {
                    'url': url,
                    'mainBusinessLine': row['mainBusinessLine.descriptions'],
                    'pages': []
                }

    # Define rules for crawling
    rules = (
        Rule(
            LinkExtractor(allow=(), deny=(), unique=True),
            callback='parse_item',
            follow=True
        ),
    )

    def parse_item(self, response):
        domain = response.url.split("//")[-1].split("/")[0]
        text_content = ' '.join(response.xpath('//body//text()').getall())
        text_content = ' '.join(text_content.split())
        self.data_by_domain[domain]['pages'].append({
            'page_url': response.url,
            'content': text_content
        })

    def closed(self, reason):
        output_file = 'grouped_scraped_data.json'
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data_by_domain, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Scraped data saved to {output_file}")
