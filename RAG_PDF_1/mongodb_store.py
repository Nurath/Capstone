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

def delete_manual_data(manual_name):
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["manuals_db"]
    collection = db["manual_chunks"]
    result = collection.delete_many({"manual": manual_name})
# from pymongo import MongoClient
# import os, pprint

# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client["equipment_manuals"]
# collection = db["Datex-Ohmeda_7100_Service_manual.pdf"]

# manual_name = "Datex-Ohmeda_7100_Service_manual.pdf"
# chunks = list(collection.find({"manual": manual_name}))

# print(f"✅ Retrieved {len(chunks)} chunks for: {manual_name}")
# for i, chunk in enumerate(chunks[:3]):
#     print(f"\nChunk {i+1} image_urls:")
#     pprint.pprint(chunk.get("image_urls", []))
