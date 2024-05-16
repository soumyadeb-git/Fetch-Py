import os
import requests
import json
import asyncio
import random
import logging
from telegram import Bot
from datetime import datetime, timedelta
from time import sleep

# Set up logging
logging.basicConfig(filename='telegram_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

async def fetch_and_send_data():
    try:
        # Fetching JSON data from the GitHub link
        response = requests.get("https://raw.githubusercontent.com/soumyadeb-git/Fetch-Py/main/data/latest_articles.json")
        
        if response.status_code == 200:
            data = json.loads(response.text)
            
            # Your Telegram Bot token (retrieved from environment variable)
            bot_token = os.environ('TOKEN')
            
            # Your Telegram Channel ID
            channel_id = "@government_job_hunter"
            
            # Initialize the Telegram bot
            bot = Bot(token=bot_token)
            
            # Emojis and reactions for posts
            emojis = ["💼", "📝", "👩‍💼", "👨‍💼", "💻", "📅", "🏢", "👉", "🔍", "✅", "➡️"]
            reactions = ["Great opportunity!", "Thanks for sharing!", "Good luck to all applicants!", 
                         "Keep up the good work!", "Helpful information!", "Appreciate the update!",
                         "Exciting opportunity!", "Valuable insights!", "Fantastic news!",
                         "Impressive job listing!", "Informative post!", "Excellent find!"]
            
            # Sending messages one by one to the Telegram channel
            for article in data:
                if 'Title' in article and 'Category' in article and 'Last Date' in article and 'Link' in article:
                    # Randomly select an emoji and reaction
                    emoji = random.choice(emojis)
                    reaction = random.choice(reactions)
                    
                    message = f"{emoji} {article['Title']}\nCategory: {article['Category']}\nLast Date: {article['Last Date']}\nLink: {article['Link']}\n\n{reaction}"
                    await bot.send_message(chat_id=channel_id, text=message)
                    
                    # Introduce a delay between messages (optional)
                    await asyncio.sleep(1)  # Adjust the delay time as needed
                else:
                    logging.warning("Skipping article as it is missing required fields")
        else:
            logging.error("Failed to fetch data from GitHub")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    # Set up retry mechanism with exponential backoff
    retries = 3
    for attempt in range(retries):
        try:
            asyncio.run(fetch_and_send_data())
            break
        except Exception as e:
            logging.error(f"Error in attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                delay = 2 ** attempt
                logging.info(f"Retrying in {delay} seconds...")
                sleep(delay)
            else:
                logging.error("Maximum retries reached. Exiting...")
