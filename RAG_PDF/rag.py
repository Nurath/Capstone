import json
import numpy as np
from query_engine import retrieve_relevant_chunks
from llm_response import generate_answer_from_context
from store_faiss import load_faiss_index
import os

class RAG:
    def __init__(self, manual_name):
        """
        manual_name: name of the processed manual folder (e.g., "GE_Dash_3000")
        Loads chunks and FAISS index internally.
        """
        folder_path = os.path.join("output", manual_name)

        # Load chunks
        with open(os.path.join(folder_path, "chunks.json")) as f:
            self.chunks = json.load(f)

        # Load FAISS index
        self.faiss_index = load_faiss_index(os.path.join(folder_path, "faiss_index.index"))

    def retrieve_context(self, query, top_k=3):
        """
        Retrieve top-k relevant chunks using FAISS.
        """
        retrieved_chunks = retrieve_relevant_chunks(
            query=query,
            chunks=self.chunks,
            index=self.faiss_index,
            top_k=top_k
        )
        return retrieved_chunks

    def build_context(self, retrieved_chunks):
        """
        Join retrieved chunks into a single context.
        """
        context_texts = [chunk["text"] for chunk in retrieved_chunks]
        return "\n\n".join(context_texts)

    def extract_images(self, retrieved_chunks):
        """
        Extract base64 images from retrieved chunks if available.
        """
        images = []
        for chunk in retrieved_chunks:
            images.extend(chunk.get("metadata", {}).get("images_base64", []))
        return images

    def generate_response(self, user_query, model_name="deepseek-chat", top_k=3):
        """
        Full RAG pipeline: Retrieve -> Context -> LLM Answer (+ Images if needed)
        """
        retrieved_chunks = self.retrieve_context(user_query, top_k=top_k)
        context = self.build_context(retrieved_chunks)

        # Generate LLM answer
        answer = generate_answer_from_context(
            context=context,
            user_query=user_query,
            model_name=model_name
        )

        # Extract images if asked
        include_images = any(word in user_query.lower() for word in ["image", "diagram", "drawing", "picture", "figure"])
        images = self.extract_images(retrieved_chunks) if include_images else []

        return answer, images
