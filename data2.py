import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os

# Function to fetch the newest jobs sitemap URL
def fetch_newest_jobs_sitemap(main_sitemap_url):
    response = requests.get(main_sitemap_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')  # Changed from 'xml' to 'html.parser'
        # Finding all sub-sitemaps
        sitemaps = soup.find_all('sitemap')
        # Get all jobs-sitemap URLs
        jobs_sitemaps = []
        for sitemap in sitemaps:
            loc = sitemap.find('loc').text
            if "jobs-sitemap" in loc:
                match = re.search(r'jobs-sitemap(\d+)\.xml', loc)
                if match:
                    jobs_sitemaps.append(loc)
        # Sort the jobs sitemaps based on their order
        return jobs_sitemaps[-1] if jobs_sitemaps else None
    else:
        raise Exception("Failed to fetch the main sitemap")

# Function to fetch the last 5 post URLs from the newest jobs sitemap
def fetch_last_5_urls(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        urls = [url.loc.text for url in soup.find_all('url')]
        return urls[-20:]
    else:
        raise Exception(f"Failed to fetch the sitemap at {sitemap_url}")

# Function to fetch post data from each post URL
def fetch_post_data(post_url):
    response = requests.get(post_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extracting last modified date from the XML sitemap
        updated_on = response.headers.get('Last-Modified', 'Unknown')
        if updated_on != 'Unknown':
            # Convert to the desired format
            updated_on_date = datetime.strptime(updated_on, "%a, %d %b %Y %H:%M:%S %Z")
            updated_on_date = updated_on_date.strftime("%B %d, %Y")
        else:
            updated_on_date = 'Unknown'

        # Initialize data dictionary
        data = {
            "Department": None,
            "Total Vacancies": None,
            "Notification No.": None,
            "Deadlines": None,
            "Positions": None,
            "Location": None,
            "Qualification": None,
            "Application Procedure": None
        }

        # Extracting table data for main details
        table_meta = soup.find('table', {'id': 'tablemeta'})
        if table_meta:
            rows = table_meta.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = cols[0].get_text(strip=True).replace(":", "")
                    value = cols[1].get_text(strip=True)
                    if key in data:
                        data[key] = value

        # Extracting additional details from the second table
        additional_content = soup.find_all('div', class_='fl-col-content')
        for additional in additional_content:
            table_meta_additional = additional.find('table', {'id': 'tablemeta'})
            if table_meta_additional:
                rows = table_meta_additional.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 2:
                        key = cols[0].get_text(strip=True).replace(":", "")
                        value = cols[1].get_text(strip=True)
                        if key in data:
                            data[key] = value

        # Debug print for final data structure
        print(f"Post data fetched: {data}")
        
        # Structure data for JSON output
        json_data = {
            "Updated On": updated_on_date,
            "Category": "Recruitment",
            "Title": data.get("Department", "N/A"),
            "Link": "null",
            "Location": data.get("Location", "None"),
            "Summary": f"➡️Positions: {data.get('Positions', 'None')}\n" \
                       f"➡️Total Vacancies: {data.get('Total Vacancies', 'None')}\n" \
                       f"👉Notification No.: {data.get('Notification No.', 'None')}\n" \
                       f"👉Qualification: {data.get('Qualification', 'None')}\n" \
                       f"👉Application Procedure: {data.get('Application Procedure', 'None')}",
            "Last Date": "Not Disclose"
        }

        return json_data
    else:
        raise Exception(f"Failed to fetch post data at {post_url}")

# Function to update JSON file by removing old data and adding new data at the top
def update_json_file(json_file_path, new_data):
    # Check if the JSON file exists
    if os.path.exists(json_file_path):
        # Load existing data from JSON file
        with open(json_file_path, 'r') as json_file:
            existing_data = json.load(json_file)
        
        # Remove old data if the new data title already exists
        existing_data = [item for item in existing_data if item['Title'] != new_data['Title']]
    else:
        existing_data = []

    # Insert new data at the top
    existing_data.insert(0, new_data)

    # Save updated data back to JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

# Main function to execute the task
def main():
    main_sitemap_url = 'https://govtjobguru.in/sitemap.xml'
    json_file_path = 'data/data2.json'
    
    # Fetch newest jobs-sitemap
    newest_sitemap_url = fetch_newest_jobs_sitemap(main_sitemap_url)
    if newest_sitemap_url:
        print(f"Newest Sitemap URL: {newest_sitemap_url}")
        
        # Fetch last 5 post URLs from the newest sitemap
        last_5_urls = fetch_last_5_urls(newest_sitemap_url)
        
        # Fetch post data for each URL and update the JSON file
        for post_url in last_5_urls:
            print(f"Fetching data from: {post_url}")
            post_data = fetch_post_data(post_url)
            update_json_file(json_file_path, post_data)
        
        print(f"\nData updated in {json_file_path}")
    else:
        print("No valid jobs sitemap found.")

# Execute the main function
if __name__ == "__main__":
    main()
