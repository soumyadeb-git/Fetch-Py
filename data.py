import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import random
import re

def fetch_latest_articles():
    # URL of the sitemap XML file
    sitemap_url = os.environ.get('KARM_URL')  # Accessing GitHub Actions secret variable

    if not sitemap_url:
        print("Error: KARM_URL secret variable is not set.")
        return
        
    response = requests.get(sitemap_url)
    if response.status_code != 200:
        print("Failed to fetch sitemap XML.")
        return

    # Parsing the XML
    root = ET.fromstring(response.content)
    articles = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")

    latest_articles_data = []
    for article in articles[:20]:
        loc = article.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        response = requests.get(loc)
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        last_updated = soup.find(class_='posted-on').find('time')['datetime']
        last_updated_date_only = format_last_updated(last_updated)
        post_title = fetch_and_analyze_post_title(soup)
        category = determine_category(post_title) if post_title else "Other"
        article_data = {
            'Updated On': last_updated_date_only,
            'Category': category,
            'Title': post_title
        }

        published_on_date = calculate_published_on_date(last_updated_date_only)
        article_data['Last Date'] = published_on_date

        link = fetch_third_party_link(soup)
        if link and "karmasandhan" not in link:
            article_data['Link'] = link

        latest_articles_data.append(article_data)

    output_folder = 'data/'
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, 'data1.json')

    existing_data = []
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        with open(output_path, 'r') as json_file:
            existing_data = json.load(json_file)

    updated_data = latest_articles_data + [item for item in existing_data if 'Title' not in latest_articles_data]

    with open(output_path, 'w') as json_file:
        json.dump(updated_data, json_file, indent=4)

    print("Latest articles data stored in 'data1.json' file.")

def format_last_updated(last_updated):
    date_object = datetime.fromisoformat(last_updated)
    formatted_date = date_object.strftime('%B %d, %Y')
    return formatted_date

def fetch_and_analyze_post_title(soup):
    post_title_tag = soup.find('h1', class_='entry-title')
    if post_title_tag:
        post_title = post_title_tag.text.strip()
        keywords = ['Recruitment 2024', 'Notification', 'Admit Card 2024', 'Result']
        for keyword in keywords:
            if keyword in post_title:
                return post_title.split(keyword)[0] + keyword
    return None

def determine_category(title):
    if "Recruitment 2024" in title:
        return "Recruitment"
    elif "Notification" in title:
        return "Notification"
    elif "Admit Card 2024" in title:
        return "Admit Card"
    elif "Result" in title:
        return "Result"
    return "Other"

def fetch_third_party_link(soup):
    entry_content = soup.find('div', class_='entry-content')
    if entry_content:
        link_pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href=(["\'])(.*?)\1')
        matches = link_pattern.findall(str(entry_content))
        priority_links = []
        other_links = []
        for match in matches:
            link = match[1]
            if "karmasandhan" not in link:
                if any(domain in link for domain in ['.gov.in', '.res.in', '.nic.in', '.edu.in']):
                    priority_links.append(link)
                else:
                    other_links.append(link)
        
        if priority_links:
            return priority_links[0]
        elif other_links:
            return other_links[0]

    return None

def calculate_published_on_date(last_updated_date):
    random_days = random.randint(18, 30)
    date_object = datetime.strptime(last_updated_date, '%B %d, %Y')
    published_on_date = date_object + timedelta(days=random_days)
    return published_on_date.strftime('%B %d, %Y')

# Calling the function
fetch_latest_articles()
