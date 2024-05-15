import requests
import json
import asyncio
import random
from telegram import Bot

async def fetch_and_send_data():
    try:
        # Fetching JSON data from the GitHub link
        response = requests.get("https://raw.githubusercontent.com/soumyadeb-git/Fetch-Py/main/data/latest_articles.json")
        
        if response.status_code == 200:
            data = json.loads(response.text)
            
            # Your Telegram Bot token
            bot_token = "${{ secret.TOKEN }}"
            
            # Your Telegram Channel ID
            channel_id = "@government_job_hunter"
            
            # Initialize the Telegram bot
            bot = Bot(token=bot_token)
            
            # Emojis and reactions for posts
            emojis = ["💼", "📝", "👩‍💼", "👨‍💼", "💻", "📅", "🏢", "👉", "🔍", "✅", "➡️"]
            reactions = ["Great opportunity!", "Thanks for sharing!", "Good luck to all applicants!", "Keep up the good work!", "Helpful information!", "Appreciate the update!"]
            
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
                    print("Skipping article as it is missing required fields")
        else:
            print("Failed to fetch data from GitHub")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_and_send_data())
