from sentence_transformers import SentenceTransformer
import numpy as np

def embed_chunks(chunks, embedding_model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(embedding_model_name)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return np.array(embeddings), texts