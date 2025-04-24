import streamlit as st
from PIL import Image
import os
import json
import tempfile
import base64
from io import BytesIO
from extract_pdf_content import extract_pdf_content
from create_chunks import create_chunks_with_references
from embed_chunks import embed_chunks
from mongodb_store import store_manual_data, retrieve_manual_chunks, delete_manual_data
from llm_response import generate_llm_response
from manualupload import download_manual_from_archive
from bson import ObjectId
from query_engine import retrieve_relevant_chunks
import speech_recognition as sr
from utility import NamedFile
import datetime
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import openai
from sentence_transformers import SentenceTransformer
from gridfs import GridFS
from pymongo import MongoClient
from dotenv import load_dotenv
import boto3
import re

# Streamlit setup
st.set_page_config(page_title="Equipment Manual Assistant", page_icon="🛠️")
st.title("🛠️ Equipment Manual Assistant")

# Environment setup
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client["equipment_manuals"]
gfs = GridFS(db)

# S3 setup
s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

def upload_image_to_s3(image_bytes, filename, bucket_name, s3_path):
    try:
        s3.upload_fileobj(BytesIO(image_bytes), bucket_name, s3_path)
        url = f"https://{bucket_name}.s3.amazonaws.com/{s3_path}"
        print("✅ Uploaded image URL:", url)
        return url
    except Exception as e:
        print(f"❌ Failed to upload {filename} to S3: {e}")
        return None

def list_manual_collections():
    return [name for name in db.list_collection_names() if not name.startswith("fs.")]

@st.cache_resource(show_spinner=False)
def process_uploaded_pdf(_uploaded_file, filename):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(_uploaded_file.read())
        pdf_path = tmp_file.name

    blocks = extract_pdf_content(pdf_path)

    for block in blocks:
        for img in block["images"]:
            s3_key = f"manuals/{filename}/images/{img['filename']}"
            url = upload_image_to_s3(img["bytes"], img["filename"], S3_BUCKET_NAME, s3_key)
            print(f"Uploaded image {img['filename']} to {url}")

            img["s3_url"] = url if url else ""

    chunks = create_chunks_with_references(blocks, filename)

    with open(pdf_path, "rb") as f:
        pdf_binary = f.read()
    pdf_id = gfs.put(pdf_binary, filename=filename, content_type="application/pdf")
    timestamp = datetime.datetime.now().isoformat()

    embeddings, filtered_chunks = embed_chunks(chunks)

    if embeddings is None or len(embeddings) == 0 or len(embeddings.shape) < 2:
        raise ValueError("Embedding failed or returned invalid shape.")

    store_manual_data(filename, filtered_chunks, embeddings.tolist(), timestamp)
    return filename

st.markdown("### 🔍 Search Archive.org for Equipment Manual")
search_query = st.text_input("Enter equipment name or model:", "")
manual_file = None

if st.button("Search and Download Manual"):
    if search_query:
        with st.spinner("Searching archive.org..."):
            downloaded_path = download_manual_from_archive(search_query)
            if downloaded_path and os.path.exists(downloaded_path):
                st.success(f"Downloaded: {os.path.basename(downloaded_path)}")
                manual_file = NamedFile(open(downloaded_path, "rb"), os.path.basename(downloaded_path))
            else:
                st.warning("No matching manual found online. Please upload it manually below.")

if not manual_file:
    uploaded_file = st.file_uploader("📄 Upload manual manually (PDF)", type=["pdf"])
    if uploaded_file:
        manual_file = uploaded_file

if manual_file:
    with st.spinner("Processing the uploaded manual..."):
        manual_filename = getattr(manual_file, "name", "uploaded_manual.pdf")
        processed_pdf_name = process_uploaded_pdf(manual_file, manual_filename)
        st.success(f"Processed and added: {processed_pdf_name}")

available_manuals = list_manual_collections()
selected_manual = st.selectbox("Choose a manual to ask questions from:", available_manuals)

if selected_manual:
    chunks = retrieve_manual_chunks(selected_manual)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    def recognize_speech():
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            st.info("Listening...")
            audio = recognizer.listen(source, timeout=5)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

    user_input = st.chat_input("Ask about the equipment manual...")

    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("🎤"):
            voice_text = recognize_speech()
            if voice_text:
                st.session_state.chat_input = voice_text

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        retrieved_chunks = retrieve_relevant_chunks(user_input, chunks, model, top_k=1)
        
        chunk = retrieved_chunks[0]
        context = chunk["text"]

        prompt = f"""Using the following manual content, answer the question clearly and step-by-step.
If any image references (like [Image: path]) are included, mention them appropriately only if user asks for images.

Context:
{context}

Question: {user_input}"""

        llm_answer = generate_llm_response(prompt, model_name="deepseek-chat")

        image_urls = []
        if "image" in user_input.lower() or "illustration" in user_input.lower():
            image_refs = re.findall(r"\[Image: (.*?)\]", context)
            image_refs = [ref.strip() for ref in image_refs]
            all_urls = chunk.get("image_urls", [])
            image_urls = [
            url for url in all_urls
            if os.path.basename(url).strip().lower() in [ref.lower().strip() for ref in image_refs]
        ]

        # print("🔍 Retrieved Image URLs:", image_urls)
        # print("🔎 image_refs from text:", image_refs)
        # print("📦 image_urls in metadata:", all_urls)

        st.session_state.messages.append({
            "role": "assistant",
            "content": llm_answer,
            "image_urls": image_urls
        })

    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        image_urls = msg.get("image_urls", [])

        with st.chat_message(role):
            st.markdown(content)

        if role == "assistant" and image_urls:
            for url in image_urls:
                try:
                    st.image(url, use_container_width=True)
                    st.markdown(f"🔗 **Image URL:** {url}")
                    print("🖼️ Image Displayed URL:", url)
                except Exception as e:
                    st.warning(f"⚠️ Couldn't render image: {e}")
