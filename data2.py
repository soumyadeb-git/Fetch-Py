import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

# Function to fetch and parse the main sitemap
def fetch_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    response.raise_for_status()  # Raise an error for bad status codes
    root = ET.fromstring(response.content)
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    # Extract URLs for sub-sitemaps
    sub_sitemaps = [url.find('ns:loc', namespaces).text for url in root.findall('ns:sitemap', namespaces)]
    return sub_sitemaps

# Function to get the latest jobs sitemap URL
def get_latest_jobs_sitemap(sitemaps):
    # Filter sitemaps that follow the 'jobs-sitemap[number].xml' pattern
    jobs_sitemaps = sorted([sitemap for sitemap in sitemaps if 'jobs-sitemap' in sitemap], reverse=True)
    return jobs_sitemaps[0] if jobs_sitemaps else None

# Function to fetch and parse the latest jobs sitemap
def fetch_jobs_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    response.raise_for_status()  # Raise an error for bad status codes
    root = ET.fromstring(response.content)
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [url.find('ns:loc', namespaces).text for url in root.findall('ns:url', namespaces)]
    return urls

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
                    date_match = re.search(r'\d{2}/\d{2}/\d{4}', value)
                    if date_match:
                        data['Last Date'] = date_match.group(0)
                elif key == "Notification Published on":
                    data['Updated On'] = value

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

# Main function to execute the scraping and saving process
def main():
    # Fetching URL from environment variable
    sitemap_url = os.getenv('SIURL', 'https://govtjobguru.in/sitemap.xml')
    
    # Step 1: Fetch all sub-sitemaps from the main sitemap
    sub_sitemaps = fetch_sitemap(sitemap_url)
    
    # Step 2: Identify the latest jobs sitemap (e.g., jobs-sitemap4.xml)
    latest_jobs_sitemap = get_latest_jobs_sitemap(sub_sitemaps)
    
    if latest_jobs_sitemap:
        # Step 3: Fetch the URLs from the latest jobs sitemap
        post_urls = fetch_jobs_sitemap(latest_jobs_sitemap)
        
        # The most recent posts are at the bottom, so we reverse the list
        post_urls = post_urls[::-1]
        scraped_data = []
        
        # Step 4: Scrape each post starting from the bottom
        for url in post_urls:
            print(f"Scraping {url}")
            post_data = scrape_post(url)
            print("Post data:", post_data)  # Debugging line
            if post_data:
                scraped_data.append(post_data)
        
        # Step 5: Save the scraped data
        output_folder = 'data/'
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, 'data2.json')
        print("Output path:", output_path)  # Debugging line
        
        # Reading existing data from the file
        existing_data = []
        if os.path.exists(output_path):  
            with open(output_path, 'r') as json_file:
                existing_data = json.load(json_file)
        
        # Update existing data for specific entries
        for new_article in scraped_data:
            for existing_article in existing_data:
                if 'Title' in new_article and 'Title' in existing_article:
                    if new_article['Title'] == existing_article['Title']:
                        existing_article.update(new_article)
                        break
            else:
                existing_data.append(new_article)
        
        # Storing updated data in the JSON file
        with open(output_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
        print("Latest articles data stored in 'data2.json' file.")
    else:
        print("No jobs sitemap found.")

if __name__ == "__main__":
    main()
