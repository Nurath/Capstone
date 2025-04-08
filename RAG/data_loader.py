import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import CharacterTextSplitter
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))



def load_and_split_pdf(file_path):
    """Loads and splits a PDF into text chunks."""
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)

    return split_docs
