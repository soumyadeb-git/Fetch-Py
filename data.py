import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re

def fetch_latest_articles():
    # URL of the sitemap XML file
    sitemap_url = os.environ.get('KARM_URL')  # Accessing GitHub Actions secret variable

    response = requests.get(sitemap_url)
    if response.status_code != 200:
        print("Failed to fetch sitemap XML.")
        return

    try:
        # Try parsing as XML
        root = ET.fromstring(response.content)
        articles = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
    except ET.ParseError:
        print("Response is not valid XML. Parsing as HTML.")
        return

    latest_articles_data = []

    # Processing each article found
    for article in articles[:25]:
        loc = article.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        
        # Only process links that are valid URLs
        if not loc.startswith('http'):
            continue
            
        response = requests.get(loc)
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        last_updated_tag = soup.find(class_='posted-on')

        if last_updated_tag and last_updated_tag.find('time'):
            last_updated = last_updated_tag.find('time')['datetime']
            last_updated_date_only = format_last_updated(last_updated)
            post_title = fetch_and_analyze_post_title(soup)
            category = determine_category(post_title) if post_title else "Other"

            article_content = soup.find('div', class_='entry-content')
            extracted_data = extract_job_details(article_content.get_text(separator=' '), article_content, soup) if article_content else {}

            # Ensure consistent JSON output format
            article_data = {
                'Updated On': last_updated_date_only,
                'Category': category,
                'Title': post_title,
                'Application Link': extracted_data.get('Application Link', None),
                'Summary': extracted_data.get('Summary', 'N/A'),
                'Last Date': extracted_data.get('Last Date/Application Deadlines', 'Not Mentioned and Will be Updated Soon')
            }

            latest_articles_data.append(article_data)

    # Save the data to a JSON file
    output_folder = 'Fetch/data/'
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, 'data1.json')

    with open(output_path, 'w') as json_file:
        json.dump(latest_articles_data, json_file, indent=4)

    print("Latest articles data stored in 'data1.json' file.")

def extract_job_details(content, article_content, soup):
    text = content
    job_details = {
        'Application Link': fetch_third_party_link(soup),
        'Summary': generate_short_summary(text),
        'Last Date/Application Deadlines': extract_application_deadlines(article_content)  # Capture date details
    }
    return job_details

def fetch_third_party_link(soup):
    entry_content = soup.find('div', class_='entry-content')
    if entry_content:
        link_pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href=(["\'])(.*?)\1')
        matches = link_pattern.findall(str(entry_content))
        priority_links = []
        other_links = []

        for match in matches:
            link = match[1]
            if ("karmasandhan" not in link and 
                "whatsapp.com" not in link and 
                "t.me" not in link and 
                "x.com" not in link and 
                "facebook.com" not in link):
                if any(domain in link for domain in ['.gov.in', '.res.in', '.nic.in', '.edu.in', '.res.in']):
                    priority_links.append(link)
                else:
                    other_links.append(link)

        if priority_links:
            return priority_links[0]
        elif other_links:
            return other_links[0]

    return None

def generate_short_summary(text):
    # Split the text into sentences and filter out any sentence containing URLs
    sentences = text.split('.')
    summary_points = []
    
    for sentence in sentences:
        cleaned_sentence = sentence.strip()
        
        # Skip any sentence that contains a URL (http, https, www)
        if 'http' in cleaned_sentence or 'www' in cleaned_sentence:
            continue

        if cleaned_sentence:  # Check for non-empty sentences
            summary_points.append(f"- {cleaned_sentence}")  # Adding bullet points for formatting
        if len(summary_points) >= 3:  # Limit to three points
            break

    return '\n'.join(summary_points) if summary_points else 'N/A'  # Join the points or return 'N/A'

def extract_application_deadlines(article_content):
    # Get all text from the article content
    text = article_content.get_text(separator=' ', strip=True)

    # Define a regex pattern to capture various date formats
    date_patterns = [
        r'(?:(?:Walk-In-Interview Date|Last Date|Application Deadline|Deadline):?\s*([\w\s,.-]+?\d{1,2}[/-]\d{1,2}[/-]\d{2,4}))',  # dd/mm/yyyy or dd-mm-yyyy
        r'(?:(?:Walk-In-Interview Date|Last Date|Application Deadline|Deadline):?\s*([\w\s,.-]*\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}))',  # dd Month yyyy
        r'(?:(?:by|within|before)\s*([\w\s,.-]*\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}))',  # By/within dd Month yyyy
        r'(?:(?:submit|applications must be submitted)\s*(?:before|within)\s*([\w\s,.-]*\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}))',  # Submit before dd Month yyyy
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # dd/mm/yyyy or dd-mm-yyyy
        r'(\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4})',  # dd Month yyyy
        r'(\d{1,2}\s+\w+\s+\d{4})'  # dd Month yyyy with space
    ]

    # Collect matches
    matched_dates = []

    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        matched_dates.extend([match.strip() for match in matches if match.strip()])

    # Process matched dates to convert to date objects and format them
    formatted_dates = []
    today = datetime.now().date()  # Get today's date

    for date_str in matched_dates:
        try:
            # Attempt to parse various formats
            if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', date_str):
                date_obj = datetime.strptime(date_str, '%d/%m/%Y') if '/' in date_str else datetime.strptime(date_str, '%d-%m-%Y')
            elif re.search(r'\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}', date_str):
                date_obj = datetime.strptime(date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '').strip(), '%d %B %Y')
            else:
                date_obj = datetime.strptime(date_str.strip(), '%d %B %Y')  # e.g., "21 October 2024"

            # Check if the date is not today's date
            if date_obj.date() != today:
                formatted_dates.append(date_obj.strftime('%Y-%m-%d'))
        except ValueError:
            continue  # Skip invalid date formats

    # Ensure uniqueness and sort the formatted dates
    unique_dates = sorted(set(formatted_dates))

    # Return formatted dates or default message if none found
    return ', '.join(unique_dates) if unique_dates else 'Not Mentioned and Will be Updated Soon'

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

# Calling the function
fetch_latest_articles
