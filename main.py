import os
import time
import requests
from dotenv import load_dotenv
import snscrape.modules.twitter as sntwitter
import instaloader
import certifi
import os
import ssl

# Ensure system uses proper SSL certs
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")

last_tweet_id = None
last_instagram_post = None

def post_to_discord(content):
    data = {"username": "Social Bot", "content": content}
    requests.post(DISCORD_WEBHOOK, json=data)

def check_twitter():
    global last_tweet_id
    tweet = next(sntwitter.TwitterUserScraper(TWITTER_USERNAME).get_items(), None)
    if tweet and (last_tweet_id is None or tweet.id != last_tweet_id):
        url = f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet.id}"
        post_to_discord(f"🐦 New tweet from @{TWITTER_USERNAME}:\n{url}")
        last_tweet_id = tweet.id

def check_instagram():
    global last_instagram_post
    loader = instaloader.Instaloader()
    posts = instaloader.Profile.from_username(loader.context, INSTAGRAM_USERNAME).get_posts()
    latest_post = next(posts, None)
    if latest_post:
        shortcode = latest_post.shortcode
        url = f"https://www.instagram.com/p/{shortcode}/"
        if last_instagram_post != shortcode:
            post_to_discord(f"📸 New Instagram post from @{INSTAGRAM_USERNAME}:\n{url}")
            last_instagram_post = shortcode

if __name__ == "__main__":
    while True:
        try:
            check_twitter()
            check_instagram()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)  # check every 60 seconds
