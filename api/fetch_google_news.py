import sys
sys.path.append('/opt/python')

import time
from openai import OpenAI 
import feedparser  # Parses RSS feeds
from flask import Flask, jsonify 
import pymongo   
import os
from bson import ObjectId
app = Flask(__name__)

# ########################## KEYS  ###########################
# OpenAI API Key 

# 🔥 MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client["meme_generator_db"]  # Database
trends_collection = db["trending_topics"]  # Collection
memes_collection = db["memes"]  # Collection

# 🔥 API Keys
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

source_dict = {
    "serpapi": "Google Trends",
    "google_news": "Google News"
 }

# Meme template paths (local storage)
MEME_LIBRARY = {
    "drake.jpg": {
        "captions": 2,
        "positions": [{"x": 300, "y": 160}, {"x": 350, "y": 560}],
        "font_size": 24,
        "order": ["top_right", "bottom_right"],
        "meme_name": "drake hotline bling"
    },
    "i_fear_no_man.jpg": {
        "captions": 1,
        "positions": [{"x": 200, "y": 450}],
        "order": ["bottom", ],
          "font_size": 12,
        "meme_name": "i fear no man"
    },
    "distracted_boyfriend.jpg": {
        "captions": 1,
        "positions": [{"x": 30, "y": 350},{"x": 130, "y": 350},{"x": 180, "y": 350}],
        "order": ["left_bottom", "center_bottom", "right_bottom"],
        "font_size": 16,
        "meme_name": "distracted boyfriend"
    },
     "crying_wojak.webp": {
        "captions": 1,
        "positions": [{"x": 55, "y": 700}, ],
        "order": ["bottom"],
        "meme_name": "crying wojak",
         "font_size": 25,
    }
} 
def serialize_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError("Type not serializable")

def get_google_news():
    print("Fetching Google News...")
    url = "https://news.google.com/rss"
    feed = feedparser.parse(url)

    if not feed.entries:
        print("No news found.")
        return []

    news = [{"topic":entry.title,"timestamp":time.time(),"isGenerated": False} for entry in feed.entries][:10]
    print(f"Google News at {time.time()}: {news}")
    return news 

def save_trends_to_mongo(trends, source):
    if not trends:
        print(f"❌ No {source} trends to save.")
        return

    count = 0
    for trend in trends:
        if not trends_collection.find_one({"topic": trend["topic"]}):
            trend["source"] = source
            trend["timestamp"] = time.time()
            trends_collection.insert_one(trend)
            count += 1

    print(f"✅ {count} {source} trends saved to MongoDB.")

@app.route("/api/fetch_google_news", methods=["POST"])
def fetch_google_news():
    # Your Google Trends logic here
    google_news = get_google_news()
    save_trends_to_mongo(google_news, source_dict["google_news"])
    if len(google_news) < 1:
        print(f"❌ No {source_dict["serpapi"]} trends fetched.") 
        return jsonify({"message": "Google news not found",'data': None, "python_version": sys.version})
    return jsonify({"message": "Google News fetched!", "data": [news["topic"] for news in google_news]})

if __name__ == "__main__":
    app.run(debug=True)
     