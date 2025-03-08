import sys
sys.path.append('/opt/python')

import time
from openai import OpenAI 
import feedparser  # Parses RSS feeds
from flask import Flask, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import random 
import requests
import schedule
from io import BytesIO 
import pymongo
from serpapi import GoogleSearch
from datetime import datetime
import base64
import os
app = Flask(__name__)


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

# ########################## TYPES  ###########################
 
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

def get_google_trends_from_serpapi():
    print("Fetching Google Trends from SerpAPI...")
    # google_trends_cat_dict = [
    #     {"title": "Politics", "cat_id": 396},
    #     {"title": "Entertainment Industry", "cat_id": 612},
    #     {"title": "Movie Listings & Theater Showtimes", "cat_id": 1085},
    #     {"title": "Ticket Sales", "cat_id": 614},
    #     {"title": "Visual Art & Design", "cat_id": 24},
    # ]
    try:
        params = {
        "engine": "google_trends_trending_now",
        "geo": "GB",
        "api_key": SERPAPI_KEY,
        "output": "json"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        trending_searches = results["trending_searches"] 
        trends = [{"topic": trend["query"],"timestamp":time.time(),"categories":trend["categories"],"trend_breakdown":trend["trend_breakdown"], "isGenerated": False} for trend in trending_searches]
        return  trends

    except Exception as e:
        print("SerpAPI failed:", e)
        return []
    
def testing_mongo():
    """Testing MongoDB connection and insertion."""

    # Fetch all documents
    all_trends = list(trends_collection.find())
    print("All Trends:", all_trends)

    # Fetch specific document
    python_trend = trends_collection.find_one({"topic": "AI Memes"})
    print("Python Trend:", python_trend)

def save_trends_to_mongo(trends, source):
    if not trends:
        print(f"❌ No {source} trends to save.")
        return

    count = 0
    for trend in trends:
        if not trends_collection.find_one({"topic": trend["topic"]}):
            trend["source"] = source
            trend["timestamp"] = datetime.utcnow() 
            trends_collection.insert_one(trend)
            count += 1

    print(f"✅ {count} {source} trends saved to MongoDB.")

@app.route("/", methods=["POST"])
def fetch_google_trends():
    # Your Google Trends logic here
    google_trends = get_google_trends_from_serpapi()
    save_trends_to_mongo(google_trends, source_dict["serpapi"])
    return jsonify({"message": "Google Trends fetched!",'data':google_trends})

if __name__ == "__main__":
    app.run()