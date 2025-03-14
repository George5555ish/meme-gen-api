import sys
sys.path.append('/opt/python')

import time
from openai import OpenAI  
from flask import Flask, jsonify 
import pymongo
from serpapi import GoogleSearch
import os
from bson import ObjectId

app = Flask(__name__)


# 🔥 MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client["meme_generator_db"]  # Database
trends_collection = db["trending_topics"]  # Collection
memes_collection = db["memes"]  # Collection

# 🔥 API Keys
SERPAPI_KEY = os.getenv("SERPAPI_KEY") 

# ########################## TYPES  ###########################
 
source_dict = {
    "serpapi": "Google Trends",
    "google_news": "Google News"
 }
 
def serialize_objectid(obj):
    print("Serializing ObjectID")
    print(obj)
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError("Type not serializable")

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
        trends = [{"topic": trend["query"],"timestamp":time.time(),"categories":trend["categories"],"trend_breakdown":None, "isGenerated": False} for trend in trending_searches]
        print(f"Google Trends at {time.time()}: {trends[:2]}")
        return trends

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

@app.route("/api/fetch_google_trends", methods=["POST"])
def fetch_google_trends():
    # Your Google Trends logic here
    google_trends = get_google_trends_from_serpapi()
    save_trends_to_mongo(google_trends, source_dict["serpapi"])
    if len(google_trends) < 1:
        print(f"❌ No {source_dict["serpapi"]} trends fetched.") 
        return jsonify({"message": "Google Trends not found",'data': None, "python_version": sys.version})
    return jsonify({"message": "Google Trends fetched!",'data': google_trends[:5]})

if __name__ == "__main__":
    app.run(debug=True)