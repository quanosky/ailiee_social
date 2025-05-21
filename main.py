import os
import time
import requests
import certifi
import ssl
import snscrape.modules.twitter as sntwitter
from instascrape import Profile
from dotenv import load_dotenv

# Fix SSL issue for Railway
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")

last_tweet_id = None
last_instagram_shortcode = None

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
        profile = Profile.from_username(INSTAGRAM_USERNAME)
        profile.scrape()
        latest_post = profile.latest_posts[0]
        if latest_post.shortcode != last_instagram_shortcode:
            last_instagram_shortcode = latest_post.shortcode
            post_url = f"https://www.instagram.com/p/{latest_post.shortcode}/"
            post_to_discord(f"📸 New Instagram post from @{INSTAGRAM_USERNAME}:\n{post_url}")
    except Exception as e:
        print(f"Instagram error: {e}")

if __name__ == "__main__":
    print("🔁 Twitter + Instagram to Discord bot running...")
    while True:
        check_twitter()
        check_instagram()
        time.sleep(120)
