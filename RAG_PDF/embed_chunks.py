from sentence_transformers import SentenceTransformer
import openai
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()

# def embed_chunks(chunks, embedding_model_name="all-MiniLM-L6-v2"):
#     model = SentenceTransformer(embedding_model_name)
#     texts = [chunk["text"] for chunk in chunks]
#     embeddings = model.encode(texts, show_progress_bar=True)
#     return np.array(embeddings), texts


def embed_chunks(chunks, model_name="text-embedding-3-small"):
    texts = [chunk["text"] for chunk in chunks if chunk.get("text")]

    if not texts:
        return np.array([]), []
    
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.embeddings.create(
        model=model_name,
        input=texts
    )
    embeddings = [r.embedding for r in response.data]
    return np.array(embeddings), texts

# import numpy as np
# import openai
# import os

# def embed_chunks(chunks, model_name="text-embedding-3-small", batch_size=20):
#     openai.api_key = os.getenv("OPENAI_API_KEY")

#     texts = [chunk["text"] for chunk in chunks if chunk.get("text")]
#     all_embeddings = []

#     for i in range(0, len(texts), batch_size):
#         batch = texts[i:i+batch_size]
#         response = openai.embeddings.create(
#             model=model_name,
#             input=batch
#         )
#         batch_embeddings = [r.embedding for r in response.data]
#         all_embeddings.extend(batch_embeddings)

#     return np.array(all_embeddings), texts
