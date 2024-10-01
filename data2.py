import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

# Function to fetch and parse the sitemap
def fetch_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()  # Raise an error for bad status codes
        root = ET.fromstring(response.content)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [url.find('ns:loc', namespaces).text for url in root.findall('ns:url', namespaces)]
        return urls[:20]  # Get the latest 20 URLs
    except requests.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        return []

# Function to scrape data from a post URL
def scrape_post(url):
    try:
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
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return {}

# Function to prioritize URLs based on domain
def prioritize_urls(urls):
    priorities = ['.gov.in', '.nic.in', '.ac.in', '.org.in', '.in']
    return sorted(urls, key=lambda url: next((i for i, domain in enumerate(priorities) if domain in url), len(priorities)))

# Main function to execute the scraping and saving process
def main():
    # Fetching URL from environment variable
    sitemap_url = os.getenv('SIURL')
    if not sitemap_url:
        print("Sitemap URL not provided. Please set the 'SIURL' environment variable.")
        return

    post_urls = fetch_sitemap(sitemap_url)
    if not post_urls:
        print("No URLs found in the sitemap.")
        return

    prioritized_urls = prioritize_urls(post_urls)
    scraped_data = []

    for url in prioritized_urls:
        print(f"Scraping {url}")
        post_data = scrape_post(url)
        print("Post data:", post_data)  # Debugging information
        if post_data:
            scraped_data.append(post_data)

    if not scraped_data:
        print("No data scraped.")
        return

    # Output folder path
    output_folder = 'data/'
    try:
        os.makedirs(output_folder, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {output_folder}: {e}")
        return
    output_path = os.path.join(output_folder, 'data2.json')
    print("Output path:", output_path)  # Debugging information

    # Reading existing data from the file
    existing_data = []
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r') as json_file:
                existing_data = json.load(json_file)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {output_path}. Starting with an empty list.")

    # Update existing data for specific entries
    for new_article in scraped_data:
        matched = False
        for existing_article in existing_data:
            if 'Title' in new_article and 'Title' in existing_article:
                if new_article['Title'] == existing_article['Title']:
                    existing_article.update(new_article)  # Update existing entry
                    matched = True
                    break
        if not matched:
            existing_data.append(new_article)  # Append new article if no match

    # Storing updated data in the JSON file
    try:
        with open(output_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
        print(f"Latest articles data stored in '{output_path}' file.")
    except IOError as e:
        print(f"Error writing to {output_path}: {e}")

if __name__ == "__main__":
    main()
