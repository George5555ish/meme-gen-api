import sys
sys.path.append('/opt/python')

import time
from openai import OpenAI  
from flask import Flask, jsonify 
from PIL import Image, ImageDraw, ImageFont
import random  
from io import BytesIO 
import pymongo  
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
        "captions": 3,
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
    },
    "black-guy-behind-tree.webp": {
        "captions": 1,
        "positions": [{"x": 55, "y": 700}, ],
        "order": ["bottom"],
        "meme_name": "black guy behind tree",
         "font_size": 25,
    }
}


def generate_meme_captions(meme_name, num_captions, trend_topic, source):
    """Generates meme captions using OpenAI based on a trending topic."""

    # Generate captions based on the source
    if source == source_dict["google_news"]:
        prompt = f"Generate {num_captions} short, funny meme captions for {meme_name}, inspired by the latest news: {trend_topic}."
    else:
        prompt = f"Generate {num_captions} short, funny meme captions for {meme_name}, inspired by the trending topic: {trend_topic}.  The meme should be lighthearted, humorous, and safe for all audiences."

 

    # prompt = f"Generate {num_captions} short, funny meme captions for {meme_name}, inspired by the trending topic: {trend_topic}."

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a meme creator. Generate funny meme captions.  The meme should be lighthearted, humorous, and safe for all audiences."},
                  {"role": "user", "content": prompt}]
    )

    captions = response.choices[0].message.content.strip().split("\n")
    return captions[:num_captions]  # Return only the needed captions

def select_meme():
    """Randomly selects a meme template from the library."""
    meme_name = random.choice(list(MEME_LIBRARY.keys()))
    return MEME_LIBRARY[meme_name]['meme_name'], MEME_LIBRARY[meme_name], meme_name
    # 
# Step 4: AI Image Generation (if no template fits)
# Not sure if we're still doing this #
# def generate_ai_image(prompt):
#     """Uses OpenAI's DALL·E to generate an image."""
#     print('generating a new meme')
#     response = openai.Image.create(
#         model="dall-e-3",
#         prompt=prompt,
#         size="512x512",
#         response_format="url"
#     )
#     return response["data"][0]["url"]

def get_text_position(img, text, font, position_type):
    """Calculate text position based on predefined meme type."""
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)  # Get text width & height
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    center_x = (img.width - text_width) // 2  # Centers text horizontally
    center_y = (img.height - text_height) // 2  # Centers text vertically

    if position_type == "top":
        return (center_x, 20)  # 20px from top
    elif position_type == "center":
        return (center_x, center_y)  # Center of image
    else:  # Default = Bottom
        return (center_x, img.height - text_height - 20)  # 20px from bottom
def getCaptionColorFromMeme(meme_name):
    """Returns the caption color based on the meme template."""
    meme_colors = {
        "crying wojak": (115, 115, 115),
        "i fear no man": (123, 123, 123),
        "drake hotline bling": (123, 123, 123)
    }
    return meme_colors.get(meme_name, (255, 255, 255))  # Default to white

def wrap_text(draw, text, font, max_width):
    """Wraps text to fit within max_width of the image."""
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and draw.textlength(line + words[0], font=font) < max_width:
            line += (words.pop(0) + ' ')
        lines.append(line.strip())
    return lines

def add_captions_to_image(meme_filename, captions):
    """Adds captions to a meme based on predefined positions, with dynamic font scaling and text wrapping."""
    meme_template = MEME_LIBRARY.get(meme_filename)
    
    if not meme_template:
        print(f"❌ Meme template '{meme_filename}' not found.")
        return None

    img = Image.open(f"templates/{meme_filename}")
    draw = ImageDraw.Draw(img)
    captions = captions[:meme_template["captions"]]  # Limit to expected caption count

    # Set base font size (adjustable)
    base_font_size = meme_template.get("font_size", 40)
    caption_color = getCaptionColorFromMeme(meme_template["meme_name"])
    
    for i, caption in enumerate(captions):
        if i >= len(meme_template["positions"]):  
            continue  # Skip extra captions
        
        x, y = meme_template["positions"][i]["x"], meme_template["positions"][i]["y"]

        # Adjust font size based on caption length
        word_count = len(caption.split())
        font_size = max(16, base_font_size - (word_count * 2))  # Reduce font size for longer captions
        
        try:
            font = ImageFont.truetype("impact.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Wrap text if needed
        max_width = img.width - 50  # Ensure padding on both sides
        wrapped_lines = wrap_text(draw, caption, font, max_width)

        # Draw each line, adjusting Y position for multi-line captions
        line_spacing = font_size + 5
        for line in wrapped_lines:
            draw.text((x, y), line, caption_color, font=font)
            y += line_spacing  # Move down for the next line

    # Save generated meme
    # os.makedirs("generated_memes", exist_ok=True)  # Ensure folder exists
    meme_filepath = f"generated_memes/meme_{int(time.time())}.jpg"
    # img.save(meme_filepath)

    # Save as base64
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    meme_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return meme_filepath, meme_base64


@app.route("/api/generate_meme",  methods=["POST"])
def generate_meme():
    """Full pipeline: Fetch trends, select a meme, generate captions, and overlay text."""
    print("📡 Fetching trending topics...") 

    # Get the first unused Google Trend (isGenerated=False) 
    google_trend = trends_collection.find_one(
    {"source": source_dict["serpapi"], "isGenerated": False}, 
    sort=[("timestamp", -1)]  # Sort by timestamp in descending order (latest first)
    )
    # If no unused Google Trend is available, fall back to Google News
    if not google_trend:
        google_trend = trends_collection.find_one(
            {"source": source_dict["google_news"], "isGenerated": False},
            sort=[("timestamp", -1)]
        )

    if not google_trend:
        print("❌ No trends available for meme generation.")
        return jsonify({"error": "No trends available for meme generation."})


    # Select a meme template
    selected_meme, meme_data, meme_name = select_meme()
    print(f"🎭 Using Meme Template: {selected_meme}")
    print(f"🎭 Using meme_data: {meme_data}")

    # # Generate captions
    # captions = generate_meme_captions(selected_meme, meme_data["captions"], selected_trend)
    # print(f"📝 Generated Captions: {captions}")
    # (meme_name, num_captions, trend_topic, source):
    captions = generate_meme_captions(meme_name,meme_data["captions"], google_trend["topic"], google_trend["source"])
    # fake_captions = ["This is a fake caption", "This is another fake caption", "This is the third fake caption", "This is the fourth fake caption"]
    print(f"📝 Generated Captions: {captions}")
    meme_image_base64 = add_captions_to_image(meme_name, captions)

    memes_collection.insert_one({
        "topic": google_trend["topic"],
        "captions": captions,
        "meme_template": meme_name,
        "source": google_trend["source"],
        "timestamp": time.time(),
        "image_base64": meme_image_base64
    })

    print(f"✅ Meme created for {google_trend['source']}: {google_trend['topic']} -> {meme_name}")

    # If the trend is from Google Trends, mark it as generated
    trends_collection.update_one(
            {"_id": google_trend["_id"]},
            {"$set": {"isGenerated": True}}
        )
    return jsonify({"message": "Meme generated!", "meme": meme_name})
 

if __name__ == "__main__":
    app.run(debug=True)