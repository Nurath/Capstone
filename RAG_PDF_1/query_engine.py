import faiss
import json
import numpy as np
import openai
import os

# def load_chunks_and_index(chunks_path="output/chunks.json", index_path="output/faiss.index"):
#     with open(chunks_path, "r") as f:
#         chunks = json.load(f)

#     index = faiss.read_index(index_path)
#     return chunks, index

# def retrieve_relevant_chunks(query, chunks, index, model=None, top_k=3):
#     openai.api_key = os.getenv("OPENAI_API_KEY")
#     client = openai.OpenAI()

#     # Use OpenAI to embed the query
#     response = client.embeddings.create(
#         model="text-embedding-3-small",  # or text-embedding-ada-002
#         input=[query]
#     )
#     query_embedding = np.array([response.data[0].embedding]).astype("float32")

#     # Ensure dimensionality matches FAISS index
#     assert query_embedding.shape[1] == index.d, f"Query dim {query_embedding.shape[1]} != index dim {index.d}"

#     _, indices = index.search(query_embedding, top_k)
#     results = [chunks[i] for i in indices[0]]
#     return results


import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def retrieve_relevant_chunks(query, chunks, model, top_k=3):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    query_embedding = np.array([response.data[0].embedding])


    # Extract stored embeddings from MongoDB chunks
    stored_embeddings = np.array([c["embedding"] for c in chunks])

    if query_embedding.shape[1] != stored_embeddings.shape[1]:
        raise ValueError(f"Embedding dimension mismatch: query={query_embedding.shape[1]}, chunks={stored_embeddings.shape[1]}")

    similarities = cosine_similarity(query_embedding, stored_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    return [chunks[i] for i in top_indices]
