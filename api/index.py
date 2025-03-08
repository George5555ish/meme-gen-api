from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
