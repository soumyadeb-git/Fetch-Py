import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

# Function to fetch and parse the sitemap
def fetch_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    response.raise_for_status()  # Raise an error for bad status codes
    root = ET.fromstring(response.content)
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [url.find('ns:loc', namespaces).text for url in root.findall('ns:url', namespaces)]
    return urls[:15]  # Get the latest 10 URLs

# Function to scrape data from a post URL
def scrape_post(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {}
    
    # Scrape the table with id="tablemeta"
    tablemeta = soup.find('table', id='tablemeta')
    if tablemeta:
        rows = tablemeta.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if key == "Department":
                    data['Title'] = value
                elif key == "Total Vacancies":
                    data['Vacancies'] = value
                elif key == "Notification No.":
                    data['Avdt. No.'] = value
                elif key == "Deadlines":
                    # Extract only the date from the cell
                    date_match = re.search(r'\d{2}/\d{2}/\d{4}', value)
                    if date_match:
                        data['Last Date'] = date_match.group(0)
                elif key == "Notification Published on":
                    data['Notification Published on'] = value

    # Scrape the table with id="tablelinks"
    tablelinks = soup.find('table', id='tablelinks')
    if tablelinks:
        rows = tablelinks.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 2 and ("Apply Online" in cells[0].get_text(strip=True) or "Online Registration Portal" in cells[0].get_text(strip=True)):
                data['Link'] = cells[1].find('a')['href']
                break
    
    return data

# Function to prioritize URLs
def prioritize_urls(urls):
    priorities = ['.gov.in', '.nic.in', '.ac.in', '.org.in', '.in']
    return sorted(urls, key=lambda url: next((i for i, domain in enumerate(priorities) if domain in url), len(priorities)))

# Function to check if title already exists in data
def check_existing_title(title, data):
    for entry in data:
        if 'Title' in entry and entry['Title'] == title:
            return True
    return False

# Main function to execute the scraping and saving process
def main():
    # Fetching URL from environment variable
    sitemap_url = os.getenv('SIURL')
    post_urls = fetch_sitemap(sitemap_url)
    prioritized_urls = prioritize_urls(post_urls)
    scraped_data = []
    for url in prioritized_urls:
        print(f"Scraping {url}")
        post_data = scrape_post(url)
        if post_data:
            # Check if title already exists in data
            if 'Title' in post_data and not check_existing_title(post_data['Title'], scraped_data):
                scraped_data.append(post_data)
    
    # Output folder path
    output_folder = 'data/'
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, 'data2.json')
    
    # Reading existing data from the file
    existing_data = []
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:  # Check if file exists and not empty
        try:
            with open(output_path, 'r') as json_file:
                existing_data = json.load(json_file)
        except json.JSONDecodeError:
            print("Existing JSON file is empty or malformed.")
    
    # Update existing data for specific entries
    for new_article in scraped_data:
        for existing_article in existing_data:
            if 'Title' in new_article and 'Title' in existing_article:
                if new_article['Title'] == existing_article['Title']:
                    existing_article.update(new_article)
                    break
        else:
            existing_data.append(new_article)
    
    # Adding main tag for last update time
    main_tag = {'Last Fetch Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    existing_data.insert(0, main_tag)
    
    # Storing updated data in the JSON file
    with open(output_path, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)
    
    print("Latest articles data stored in 'data2.json' file.")

if __name__ == "__main__":
    main()
