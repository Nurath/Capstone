# import os
# import json
# from extract_pdf_content import extract_pdf_content
# from create_chunks import create_chunks_with_references
# from embed_chunks import embed_chunks
# from store_faiss import store_faiss_index

# PDF_PATH = "C:/Users/Niranjan kumar/Desktop/SPRING 2025/Predictive Maintenance/Capstone/Dataset/RAG_data/wmnano.pdf"
# OUTPUT_CHUNKS = "output/chunks.json"
# os.makedirs("output", exist_ok=True)

# # Step 1: Extract from PDF
# blocks = extract_pdf_content(PDF_PATH)

# # Step 2: Create Chunks
# chunks = create_chunks_with_references(blocks)
# with open(OUTPUT_CHUNKS, "w") as f:
#     json.dump(chunks, f, indent=2)

# # Step 3: Embed and store index
# embeddings, texts = embed_chunks(chunks)
# faiss_index = store_faiss_index(embeddings, dim=embeddings.shape[1])


from extract_pdf_content import extract_pdf_content
from create_chunks import create_chunks_with_references
from embed_chunks import embed_chunks
from mongodb_store import store_manual_data

manual_name = "GE_Dash_3000-4000-5000_Service_Manual"
pdf_path = "C:/Users/Niranjan kumar/Desktop/SPRING 2025/Predictive Maintenance/Capstone/manuals/GE_Dash_3000-4000-5000_Service_Manual.pdf"


# Step 1: Extract
blocks = extract_pdf_content(pdf_path)

# Step 2: Chunk
chunks = create_chunks_with_references(blocks)

# Step 3: Embed
import numpy as np
embeddings, _ = embed_chunks(chunks)

# Step 4: Store to MongoDB
store_manual_data(manual_name, chunks, embeddings.tolist())  # convert to list for BSON
