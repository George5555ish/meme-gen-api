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
api_key = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=api_key)

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

@app.route("/")
def testing_mongo():
    """Testing MongoDB connection and insertion."""

    # Fetch all documents
    all_trends = list(trends_collection.find())
    print("All Trends:", all_trends)

    # Fetch specific document
    python_trend = trends_collection.find_one({"topic": "AI Memes"})
    print("Python Trend:", python_trend)
    return jsonify({"message": "Mongo Data fetched!", "data": all_trends})

if __name__ == "__main__":
    app.run()