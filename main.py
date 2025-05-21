import os
import time
import json
import requests
import certifi
import ssl
import subprocess
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Ensure correct SSL certs are used (for Railway and similar platforms)
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context

# Load environment variables
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
        response = requests.post(DISCORD_WEBHOOK, json={"content": content})
        response.raise_for_status()
    except Exception as e:
        print(f"[Error] Failed to send Discord message: {e}")

def check_twitter():
    global last_tweet_id
    try:
        result = subprocess.run(
            ["snscrape", "--jsonl", f"twitter-user {TWITTER_USERNAME}"],
            capture_output=True, text=True, check=True
        )
        tweets = result.stdout.strip().splitlines()
        if tweets:
            latest_tweet = json.loads(tweets[0])
            tweet_id = latest_tweet["id"]
            if last_tweet_id is None or tweet_id != last_tweet_id:
                last_tweet_id = tweet_id
                tweet_url = f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet_id}"
                post_to_discord(f"🐦 New tweet from @{TWITTER_USERNAME}:\n{tweet_url}")
    except Exception as e:
        print(f"[Twitter Error] {e}")

def check_instagram():
    global last_instagram_shortcode
    try:
        url = f"https://www.instagram.com/{INSTAGRAM_USERNAME}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find JSON data in page
        scripts = soup.find_all("script", type="text/javascript")
        json_script = next(script for script in scripts if "window._sharedData" in script.text)
        json_str = json_script.string.split(" = ", 1)[1].rstrip(";")
        data = json.loads(json_str)

        edges = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
        if edges:
            shortcode = edges[0]["node"]["shortcode"]
            if shortcode != last_instagram_shortcode:
                last_instagram_shortcode = shortcode
                post_url = f"https://www.instagram.com/p/{shortcode}/"
                post_to_discord(f"📸 New Instagram post from @{INSTAGRAM_USERNAME}:\n{post_url}")
    except Exception as e:
        print(f"[Instagram Error] {e}")

if __name__ == "__main__":
    print("🚀 Bot started: Watching Twitter and Instagram")
    while True:
        check_twitter()

        current_time = time.time()
        if current_time - last_instagram_check_time >= 600:
            check_instagram()
            last_instagram_check_time = current_time

        time.sleep(90)
