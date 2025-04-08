import sys
import os

import weaviate
from weaviate.classes.init import Auth
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate.vectorstores import WeaviateVectorStore
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import numpy as np
import fitz
from weaviate.classes.config import Property, DataType, Configure

# from RAG.config import WEAVIATE_URL, WEAVIATE_API_KEY

from RAG.config import client

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# # Load CLIP model
# clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
# clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def store_documents(docs):
    """Stores documents in Weaviate."""
    embeddings = OpenAIEmbeddings()
    vector_store = WeaviateVectorStore.from_documents(docs, embeddings, client=client)
    return vector_store
