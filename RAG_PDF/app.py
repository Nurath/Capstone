import streamlit as st
from PIL import Image
import os
import json
import tempfile
import base64
from io import BytesIO
from sentence_transformers import SentenceTransformer
from extract_pdf_content import extract_pdf_content
from create_chunks import create_chunks_with_references
from embed_chunks import embed_chunks
from store_faiss import store_faiss_index, load_faiss_index
from query_engine import retrieve_relevant_chunks
from llm_response import generate_llm_response
from manualupload import download_manual_from_archive
import speech_recognition as sr
from utility import NamedFile
import shutil

openai_api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Equipment Manual Assistant", page_icon="🛠️")
st.title("🛠️ Equipment Manual Assistant")

# Helper function to create folder per PDF
def create_output_folder(filename):
    base_name = os.path.splitext(filename)[0]
    folder_path = os.path.join("output", base_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path, base_name


@st.cache_resource(show_spinner=False)
def process_uploaded_pdf(_uploaded_file, filename):
    folder_path, base_name = create_output_folder(filename)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(_uploaded_file.read())
        pdf_path = tmp_file.name

    blocks = extract_pdf_content(pdf_path)
    chunks = create_chunks_with_references(blocks)

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
                full_path = manual_image_path
            except Exception as e:
                continue

            if os.path.exists(full_path):
                with Image.open(full_path) as img:
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    images_base64.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
        if images_base64:
            chunk.setdefault("metadata", {})["images_base64"] = images_base64

    with open(os.path.join(folder_path, "chunks.json"), "w") as f:
        json.dump(chunks, f, indent=2)

    embeddings, texts = embed_chunks(chunks)
    store_faiss_index(embeddings, dim=embeddings.shape[1], path=os.path.join(folder_path, "faiss_index.index"))

    return base_name

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

# 📄 Manual Upload Fallback
if not manual_file:
    uploaded_file = st.file_uploader("📄 Upload manual manually (PDF)", type=["pdf"])
    if uploaded_file:
        manual_file = uploaded_file

# 🚀 Process the manual
if manual_file:
    with st.spinner("Processing the uploaded manual..."):
        processed_pdf_name = process_uploaded_pdf(manual_file, os.path.basename(downloaded_path))

        st.success(f"Processed and added: {processed_pdf_name}")

available_manuals = [d for d in os.listdir("output") if os.path.isdir(os.path.join("output", d))]
selected_manual = st.selectbox("Choose a manual to ask questions from:", available_manuals)

if selected_manual:
    folder_path = os.path.join("output", selected_manual)
    with open(os.path.join(folder_path, "chunks.json")) as f:
        chunks = json.load(f)

    faiss_index = load_faiss_index(os.path.join(folder_path, "faiss_index.index"))
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

    st.chat_message("system").markdown("You can ask questions about your uploaded equipment manual. Click the mic 🎤 to speak or type below.")

    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("🎤"):
            voice_text = recognize_speech()
            if voice_text:
                st.session_state.chat_input = voice_text

    user_input = st.chat_input("Ask about the equipment manual...", key="chat_input")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        retrieved_chunks = retrieve_relevant_chunks(user_input, chunks, faiss_index, model=model, top_k=1)
        chunk = retrieved_chunks[0]
        context = chunk["text"]

        prompt = f"""Using the following manual content, answer the question clearly and step-by-step.
If any image references (like [Image: path]) are included, mention them appropriately only if user asks for images.

Context:
{context}

Question: {user_input}"""

        llm_answer = generate_llm_response(prompt, openai_api_key=openai_api_key)

        include_images = any(word in user_input.lower() for word in ["image", "diagram", "drawing", "picture", "figure"])
        images_to_send = chunk.get("metadata", {}).get("images_base64", []) if include_images else []

        st.session_state.messages.append({
            "role": "assistant",
            "content": llm_answer,
            "images": images_to_send
        })

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "images" in msg:
                for encoded_image in msg["images"]:
                    try:
                        image_data = base64.b64decode(encoded_image)
                        st.image(BytesIO(image_data), use_column_width=True)
                    except Exception as e:
                        st.warning(f"Image could not be displayed: {e}")
