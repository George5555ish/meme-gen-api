from bson import ObjectId
from flask import Flask, jsonify,Response
from pymongo import MongoClient
from flask_cors import CORS
import os
import base64
import io

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
    memes = list(memes_collection.find().sort("timestamp", -1).limit(10))
    result = []

    for meme in memes:
        meme["_id"] = str(meme["_id"])  # Convert ObjectId to string
        result.append(meme)
    return jsonify(memes)

@app.route("/recent_trends", methods=["GET"])
def get_recent_trends():
    """Fetch the top 5 most recent trends and their timestamps."""
    db = get_db_connection() 
    trends_collection = db["trending_topics"]
    trends = list(
        trends_collection.find({})
        .sort("timestamp", -1)  # Sort by most recent
        .limit(5)  # Get top 5
    )
    return jsonify(trends)

@app.route("/meme/<meme_id>", methods=["GET"])
def get_meme_details(meme_id):
    # Fetch image from MongoDB

    if not meme_id:
        return "meme ID not found", 404
    db = get_db_connection() 
    memes_collection = db["memes"]  
    single_meme = memes_collection.find_one({"_id": ObjectId(meme_id)}) 
    if not single_meme:
          return jsonify({"error": "Meme not found"}), 404 
    single_meme["_id"] = str(single_meme["_id"])  # Convert ObjectId to string
    # Return as image response
    response_data = {
        "topic": single_meme.get("topic"),
        "captions": single_meme.get("captions"),
        "meme_template": single_meme.get("meme_template"),
        "timestamp": single_meme.get("timestamp"),
        "source": single_meme.get("source"),
        "_id": single_meme.get("_id"),
        # Add other fields as needed
    }
    return jsonify({"meme": response_data })

@app.route("/image/<meme_id>", methods=["GET"])
def get_image(meme_id):
    # Fetch image from MongoDB

    if not meme_id:
        return "Image ID not found", 404
    db = get_db_connection() 
    memes_collection = db["memes"] 
    print(meme_id)
    single_meme = memes_collection.find_one({"_id": ObjectId(meme_id)})
    print(single_meme)
    if not single_meme['image_base64']:
          return jsonify({"error": "Meme not found"}), 404 

    # Decode Base64 to binary
    image_binary = base64.b64decode(single_meme["image_base64"][1] if isinstance(single_meme["image_base64"], list) else single_meme["image_base64"])

    # Return as image response
    return Response(io.BytesIO(image_binary), mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
