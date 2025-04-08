import fitz  # PyMuPDF
from PIL import Image
import os
from transformers import CLIPProcessor, CLIPModel
import torch
import weaviate
from weaviate.classes.config import Property, DataType, Configure
from RAG.config import client

# Initialize CLIP
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Ensure schema exists (run once or check if it exists)
if not client.collections.exists("PDFData"):
    client.collections.create(
        name="PDFData",
        properties=[
            weaviate.classes.config.Property(name="type", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="page_number", data_type=weaviate.classes.config.DataType.INT),
            weaviate.classes.config.Property(name="content", data_type=weaviate.classes.config.DataType.TEXT),
        ],
        vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none()  # Adjust vectorizer as needed
    )

def get_text_embedding(text):
    inputs = clip_processor(text=text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        embedding = clip_model.get_text_features(**inputs)
    return embedding[0].tolist()  # Extract the 1D embedding and convert to list

def get_image_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        embedding = clip_model.get_image_features(**inputs)
    return embedding[0].tolist()  # Extract the 1D embedding and convert to list

def process_pdf(uploaded_file):
    # Save uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    doc = fitz.open("temp.pdf")
    os.makedirs("images", exist_ok=True)
    
    # Get the "PDFData" collection
    collection = client.collections.get("PDFData")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text
        text = page.get_text("text")
        if text.strip():
            text_embedding = get_text_embedding(text)
            collection.data.insert(
                properties={
                    "type": "text",
                    "page_number": page_num,
                    "content": text
                },
                vector=text_embedding
            )
        
        # Extract images
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_path = f"images/page_{page_num}_img_{img_index}.png"
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            image_embedding = get_image_embedding(image_path)
            collection.data.insert(
                properties={
                    "type": "image",
                    "page_number": page_num,
                    "content": image_path
                },
                vector=image_embedding
            )
    
    doc.close()
    os.remove("temp.pdf")  # Clean up