

import os
import tempfile
import shutil
import json
import base64
from PIL import Image
from io import BytesIO

from extract_pdf_content import extract_pdf_content
from create_chunks import create_chunks_with_references
from embed_chunks import embed_chunks
from store_faiss import store_faiss_index

def create_output_folder(filename):
    """Create an output folder based on PDF name."""
    base_name = os.path.splitext(filename)[0]
    folder_path = os.path.join("output", base_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path, base_name

def process_uploaded_pdf(_uploaded_file, filename):
    """Process the uploaded PDF: extract, chunk, embed, store."""
    folder_path, base_name = create_output_folder(filename)

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(_uploaded_file.read())
        pdf_path = tmp_file.name

    # Extract blocks
    blocks = extract_pdf_content(pdf_path)

    # Create chunks
    chunks = create_chunks_with_references(blocks)

    # Handle images inside chunks
    for chunk in chunks:
        image_paths = chunk.get("metadata", {}).get("images", [])
        images_base64 = []
        for path in image_paths:
            image_output_dir = os.path.join(folder_path, "images")
            os.makedirs(image_output_dir, exist_ok=True)
            image_name = os.path.basename(path)
            manual_image_path = os.path.join(image_output_dir, image_name)

            try:
                shutil.copy2(path, manual_image_path)
            except Exception:
                continue

            if os.path.exists(manual_image_path):
                with Image.open(manual_image_path) as img:
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    images_base64.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
        
        if images_base64:
            chunk.setdefault("metadata", {})["images_base64"] = images_base64

    # Save chunks
    with open(os.path.join(folder_path, "chunks.json"), "w") as f:
        json.dump(chunks, f, indent=2)

    # Generate embeddings
    embeddings, texts = embed_chunks(chunks)
    if embeddings is None or len(embeddings) == 0 or len(embeddings.shape) < 2:
        raise ValueError("Embedding failed or returned invalid shape.")

    # Store FAISS index
    store_faiss_index(embeddings, dim=embeddings.shape[1], path=os.path.join(folder_path, "faiss_index.index"))

    return base_name
