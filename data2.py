import requests
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

def fetch_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()  # Raise an error for bad status codes
        root = ET.fromstring(response.content)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Extract URLs for sub-sitemaps
        sub_sitemaps = [url.find('ns:loc', namespaces).text for url in root.findall('ns:sitemap', namespaces)]

        # Debugging line: print sub-sitemaps found
        print("Sub-sitemaps found:", sub_sitemaps)  
        
        return sub_sitemaps
    except requests.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        return []

def get_latest_jobs_sitemap(sitemaps):
    # Filter sitemaps that follow the 'jobs-sitemap[number].xml' pattern
    jobs_sitemaps = sorted([sitemap for sitemap in sitemaps if 'jobs-sitemap' in sitemap], reverse=True)
    
    # Debugging line: print filtered jobs sitemaps
    print("Filtered jobs sitemaps:", jobs_sitemaps)  
    
    return jobs_sitemaps[0] if jobs_sitemaps else None

def fetch_jobs_from_sitemap(jobs_sitemap):
    try:
        response = requests.get(jobs_sitemap)
        response.raise_for_status()  # Raise an error for bad status codes
        root = ET.fromstring(response.content)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        jobs = []
        for url in root.findall('ns:url', namespaces):
            job_url = url.find('ns:loc', namespaces).text
            last_modified = url.find('ns:lastmod', namespaces).text
            
            # Parse the last modified date
            last_modified_date = datetime.fromisoformat(last_modified[:-1])  # Remove the timezone part
            
            # Store job information in a dictionary
            jobs.append({
                'url': job_url,
                'last_modified': last_modified_date.isoformat()  # Store in ISO format
            })

        # Debugging line: print jobs fetched
        print(f"Fetched {len(jobs)} jobs from {jobs_sitemap}")
        
        return jobs
    except requests.RequestException as e:
        print(f"Error fetching jobs from sitemap: {e}")
        return []

def save_to_json(data, filepath):
    try:
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data successfully saved to {filepath}")
    except IOError as e:
        print(f"Error saving data to JSON: {e}")

def main():
    # Fetching URL from environment variable
    sitemap_url = os.getenv('SIURL', 'https://govtjobguru.in/sitemap.xml')
    
    # Debugging line: print SIURL
    print("Using SIURL:", sitemap_url)  
    
    # Fetch sub-sitemaps from the main sitemap
    sub_sitemaps = fetch_sitemap(sitemap_url)
    
    # Get the latest jobs sitemap
    latest_jobs_sitemap = get_latest_jobs_sitemap(sub_sitemaps)
    
    if latest_jobs_sitemap:
        # Fetch jobs from the latest jobs sitemap
        jobs = fetch_jobs_from_sitemap(latest_jobs_sitemap)
        
        # Save the jobs data to a JSON file
        save_to_json(jobs, 'data/data2.json')
    else:
        print("No jobs sitemap found.")

if __name__ == "__main__":
    main()
