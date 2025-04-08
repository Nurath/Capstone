from RAG.vector_store import get_text_embedding
from RAG.config import client
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Retrieve Text and Images
# Function to retrieve relevant data
def retrieve_data(query, top_k=5):
    query_vector = get_text_embedding(query)
    
    response = client.query.get(
        class_name="MultimodalData",
        properties=["text", "image_url"]
    ).with_near_vector({
        "vector": query_vector.tolist(),
        "certainty": 0.8
    }).with_limit(top_k).do()

    results = []
    for obj in response["data"]["Get"]["MultimodalData"]:
        if "text" in obj:
            results.append({"type": "text", "content": obj["text"]})
        if "image_url" in obj:
            results.append({"type": "image", "content": obj["image_url"]})

    return results
