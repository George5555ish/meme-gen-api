from flask import Flask, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")

def get_db_connection():
    """Create a fresh MongoDB connection each request"""
    client = MongoClient(MONGO_URI)
    return client["meme_generator_db"] 

@app.route("/memes", methods=["GET"])
def get_memes():
    """Fetch all generated memes from the database."""

    db = get_db_connection()
    memes_collection = db["memes"] 
    memes = list(memes_collection.find({}, {"_id": 0}))
    return jsonify(memes)

@app.route("/recent_trends", methods=["GET"])
def get_recent_trends():
    """Fetch the top 5 most recent trends and their timestamps."""
    db = get_db_connection() 
    trends_collection = db["trending_topics"]
    trends = list(
        trends_collection.find({}, {"_id": 0})
        .sort("timestamp", -1)  # Sort by most recent
        .limit(5)  # Get top 5
    )
    return jsonify(trends)

if __name__ == "__main__":
    app.run(debug=True)
