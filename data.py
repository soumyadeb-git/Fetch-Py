import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def fetch_variable_value():
    # URL of the file containing the variable value in the other repository
    file_url = "https://raw.githubusercontent.com/soumyadeb-git/government-job-portal-sites/4102341f16057ef96af5947a36d2b1a96879d436/All%20State/a.txt"
    response = requests.get(file_url)
    if response.status_code == 200:
        # Extracting the variable value from the response
        sitemap_url = response.text.strip()
        return sitemap_url
    else:
        print("Failed to fetch variable value.")
        return None

def fetch_latest_articles():
    # Fetching the variable value
    sitemap_url = fetch_variable_value()
    if not sitemap_url:
        return

    # Fetching the sitemap XML file
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        # Parsing the XML
        root = ET.fromstring(response.content)
        articles = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")

        latest_articles_data = []
        for article in articles[:30]:
            loc = article.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            response = requests.get(loc)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Find last updated information using CSS selector or any other method
                last_updated = soup.find(class_='posted-on').find('time').text.strip()
                # Fetch and analyze post title
                post_title = fetch_and_analyze_post_title(soup)
                category = determine_category(post_title) if post_title else "Other"
                article_data = {
                    'Last Updated': last_updated,
                    'Category': category
                }
                if post_title:
                    article_data['Title'] = post_title

                latest_articles_data.append(article_data)

        # Output folder path
        output_folder = 'data/'
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, 'latest_articles.json')

        # Adding main tag for last update time
        main_tag = {'Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        latest_articles_data.insert(0, main_tag)

        # Storing data in a JSON file
        with open(output_path, 'w') as json_file:
            json.dump(latest_articles_data, json_file, indent=4)

        print("Latest articles data stored in 'latest_articles.json' file.")

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
    if title:
        if "Recruitment 2024" in title:
            return "Recruitment"
        elif "Notification" in title:
            return "Notification"
        elif "Admit Card 2024" in title:
            return "Admit Card"
        elif "Result" in title:
            return "Result"
    return "Other"

# Calling the function
fetch_latest_articles()
