import os
from pymongo import MongoClient
from gridfs import GridFS
from dotenv import load_dotenv
from bson import ObjectId
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client["equipment_manuals"]
gfs = GridFS(db)

# 🔍 Replace this with an actual image ObjectId from your DB
example_image_id = "68084e89289e9b62585a4f12"  # <-- Change this!

def test_image_retrieval(image_id):
    try:
        image_data = gfs.get(ObjectId(image_id)).read()
        image = Image.open(BytesIO(image_data))
        image.show()  # Opens the image using the default image viewer
        print("✅ Image successfully retrieved and opened.")
    except Exception as e:
        print(f"❌ Error retrieving image: {e}")

if __name__ == "__main__":
    test_image_retrieval(example_image_id)
