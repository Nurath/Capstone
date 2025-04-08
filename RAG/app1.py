import streamlit as st
import hashlib
import os
from RAG.pdf_processor import process_pdf
from RAG.query_handler import handle_query

IMAGES_DIR = "images"
PROCESSED_PDF_RECORDS = "processed_pdfs.txt"
os.makedirs(IMAGES_DIR, exist_ok=True)  # Ensure directory exists

def get_pdf_hash(pdf_file):
    """Compute SHA256 hash of the uploaded PDF."""
    hasher = hashlib.sha256()
    for chunk in iter(lambda: pdf_file.read(4096), b""):
        hasher.update(chunk)
    pdf_file.seek(0)  # Reset file pointer after reading
    return hasher.hexdigest()

def is_pdf_processed(pdf_hash):
    """Check if the PDF hash is in the record file or the images directory."""
    image_path = os.path.join(IMAGES_DIR, f"{pdf_hash}.png")
    
    # Check if image exists OR hash is in the processed file
    if os.path.exists(image_path):
        return True

    if os.path.exists(PROCESSED_PDF_RECORDS):
        with open(PROCESSED_PDF_RECORDS, "r") as f:
            processed_hashes = f.read().splitlines()
        return pdf_hash in processed_hashes
    
    return False

def save_pdf_hash(pdf_hash):
    """Save new PDF hash to the record file."""
    with open(PROCESSED_PDF_RECORDS, "a") as f:
        f.write(pdf_hash + "\n")

st.title("PDF RAG System")

# PDF Upload
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    pdf_hash = get_pdf_hash(uploaded_file)

    if is_pdf_processed(pdf_hash):
        st.success("This PDF has already been processed.")
    else:
        with st.spinner("Processing PDF..."):
            process_pdf(uploaded_file)  # Ensure this function saves an image as {pdf_hash}.png
        save_pdf_hash(pdf_hash)
        st.success("PDF processed and stored in vector database.")

# Query Input
query = st.text_input("Enter your query:")

if st.button("Search"):
    if query:
        with st.spinner("Retrieving and generating response..."):
            response, images = handle_query(query)
        st.write("**Response:**", response)
        st.write("**Relevant Images:**")
        for img_path in images:
            st.image(img_path, width=200)
    else:
        st.warning("Please enter a query.")
