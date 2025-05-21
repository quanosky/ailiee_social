import os
import time
import requests
import certifi
import ssl
import snscrape.modules.twitter as sntwitter
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv

# Fix SSL issue for Railway and similar environments
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")

last_tweet_id = None
last_instagram_shortcode = None
last_instagram_check_time = 0

def post_to_discord(content):
    print(f"[Discord] {content}")
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": content})
    except Exception as e:
        print(f"Discord post failed: {e}")

def check_twitter():
    global last_tweet_id
    try:
        tweet = next(sntwitter.TwitterUserScraper(TWITTER_USERNAME).get_items(), None)
        if tweet and (last_tweet_id is None or tweet.id != last_tweet_id):
            last_tweet_id = tweet.id
            tweet_url = f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet.id}"
            post_to_discord(f"🐦 New tweet from @{TWITTER_USERNAME}:\n{tweet_url}")
    except Exception as e:
        print(f"Twitter error: {e}")

def check_instagram():
    global last_instagram_shortcode
    try:
        url = f"https://www.instagram.com/{INSTAGRAM_USERNAME}/"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Look for script with JSON data
        scripts = soup.find_all("script", type="text/javascript")
        json_script = next(script for script in scripts if "window._sharedData" in script.text)
        json_str = json_script.string.split(" = ", 1)[1].rstrip(";")
        data = json.loads(json_str)

        # Get first post
        edges = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
        if edges:
            shortcode = edges[0]["node"]["shortcode"]
            if shortcode != last_instagram_shortcode:
                last_instagram_shortcode = shortcode
                post_url = f"https://www.instagram.com/p/{shortcode}/"
                post_to_discord(f"📸 New Instagram post from @{INSTAGRAM_USERNAME}:\n{post_url}")
    except Exception as e:
        print(f"Instagram scrape error: {e}")

if __name__ == "__main__":
    print("🚀 Twitter + Instagram to Discord bot started!")
    while True:
        # Check Twitter every 90 sec
        check_twitter()

        # Check Instagram every 600 sec (10 min)
        current_time = time.time()
        if current_time - last_instagram_check_time >= 600:
            check_instagram()
            last_instagram_check_time = current_time

        time.sleep(90)
