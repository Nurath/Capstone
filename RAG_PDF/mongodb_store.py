import os
from dotenv import load_dotenv
import base64
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from bson import ObjectId

load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']

# Create a new client and connect to the server
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))



db = client["equipment_manuals"]

def store_manual_data(manual_name, chunks, embeddings, timestamp):
    collection = db[manual_name]
    collection.drop()  # remove duplicates

    for i, chunk in enumerate(chunks):
        doc = {
            "manual": manual_name,
            "timestamp": timestamp,
            "page": chunk.get("metadata", {}).get("page"),
            "text": chunk["text"],
            "embedding": embeddings[i],
            "image_urls": chunk.get("metadata", {}).get("image_urls", [])
        }
        collection.insert_one(doc)

def retrieve_manual_chunks(manual_name):
    collection = db[manual_name]
    return list(collection.find({}))

def list_manual_collections():
    return [name for name in db.list_collection_names() if not name.startswith("fs.")]