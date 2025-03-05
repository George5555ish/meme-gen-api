from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["meme_generator_db"]  # Database
trends_collection = db["trending_topics"]  # Collection
memes_collection = db["memes"]  # Collection

@app.route("/memes", methods=["GET"])
def get_memes():
    """Fetch all generated memes from the database."""
    memes = list(memes_collection.find({}, {"_id": 0}))
    return jsonify(memes)

if __name__ == "__main__":
    app.run(debug=True)
