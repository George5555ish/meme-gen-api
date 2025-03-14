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

    # Fetch existing topics to avoid duplicate inserts
    existing_topics = set(trends_collection.distinct("topic"))
    
    # Filter trends that are not already in the collection
    new_trends = [
        {**trend, "source": source, "timestamp": time.time()} 
        for trend in trends if trend["topic"] not in existing_topics
    ]
    
    if new_trends:
        trends_collection.insert_many(new_trends)
        print(f"✅ {len(new_trends)} {source} trends saved to MongoDB.")
    else:
        print(f"ℹ️ No new {source} trends to save.")

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
     