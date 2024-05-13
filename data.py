import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json


def fetch_latest_articles(sitemap_url):
    # Fetching the sitemap XML file
    response = requests.get(sitemap_url)

    if response.status_code == 200:
        # Parsing the XML
        root = ET.fromstring(response.content)
        articles = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")

        latest_articles_data = []
        for article in articles[:30]:  # Get the latest 10 articles
            loc = article.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            response = requests.get(loc)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Find last updated information using CSS selector or any other method
                last_updated = soup.find(class_='posted-on').find('time').text.strip()
                # Fetch and analyze post title
                post_title = fetch_and_analyze_post_title(soup)
                if post_title:
                    category = determine_category(post_title)
                else:
                    category = "Other"
                article_data = {
                    'Last Updated': last_updated,
                    'Category': category
                }
                if post_title:
                    article_data['Title'] = post_title

                latest_articles_data.append(article_data)

        # Path to output JSON file
        output_file = 'latest_articles.json'

        # Check if output file exists
        if os.path.exists(output_file):
            # Load existing data
            with open(output_file, 'r') as json_file:
                existing_data = json.load(json_file)
            # Extend existing data with new data
            existing_data.extend(latest_articles_data)
            # Remove duplicates
            existing_data = [dict(t) for t in {tuple(d.items()) for d in existing_data}]
            latest_articles_data = existing_data

        # Storing data in the JSON file
        with open(output_file, 'w') as json_file:
            json.dump(latest_articles_data, json_file, indent=4)

        print("Latest articles data updated in 'latest_articles.json' file.")
    else:
        print("Failed to fetch sitemap XML.")


def fetch_and_analyze_post_title(soup):
    # Find and analyze post title
    post_title_tag = soup.find('h1', class_='entry-title')
    if post_title_tag:
        post_title = post_title_tag.text.strip()
        # Extract specific sections from the title
        keywords = ['Recruitment 2024', 'Notification', 'Admit Card 2024', 'Result']
        for keyword in keywords:
            if keyword in post_title:
                return post_title.split(keyword)[0] + keyword
    return None


def determine_category(title):
    # Determine category based on title content
    if "Recruitment 2024" in title:
        return "Recruitment"
    elif "Notification" in title:
        return "Notification"
    elif "Admit Card 2024" in title:
        return "Admit Card"
    elif "Result" in title:
        return "Result"
    else:
        return "Other"


# Get the sitemap URL from GitHub repository secrets
sitemap_url = os.environ.get('geturlid')

# Calling the function
fetch_latest_articles(sitemap_url)
