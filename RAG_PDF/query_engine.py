import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

def load_chunks_and_index(chunks_path="output/chunks.json", index_path="output/faiss.index", model_name="all-MiniLM-L6-v2"):
    with open(chunks_path, "r") as f:
        chunks = json.load(f)

    index = faiss.read_index(index_path)
    model = SentenceTransformer(model_name)

    return chunks, index, model

def retrieve_relevant_chunks(query, chunks, index, model, top_k=3):
    query_embedding = model.encode([query])
    _, indices = index.search(np.array(query_embedding), top_k)
    results = [chunks[i] for i in indices[0]]
    return results