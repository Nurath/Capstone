import streamlit as st
from RAG.data_loader import load_and_split_pdf
from RAG.vector_store import store_pdf, setup_weaviate_schema
import os
from RAG.rag_pipeline import create_rag_chain

# Setup Weaviate Schema
setup_weaviate_schema()

os.makedirs("temp", exist_ok=True)

# st.title("🔍 RAG-based ")
# st.sidebar.header("Upload a PDF")

# # File Upload
# uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
# if uploaded_file is not None:
#     file_path = os.path.join("temp", uploaded_file.name)  # Save file to 'temp' folder

#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())  # Write uploaded file to disk

#     # Load and Split PDF
#     docs = load_and_split_pdf(file_path)
    
#     # Store in Weaviate
#     vector_store = store_documents(docs)
#     retriever = vector_store.as_retriever()

#     # Create RAG Chain
#     rag_chain = create_rag_chain(retriever)

#     # Input Box for Queries
#     query = st.text_input("Ask a question:")
#     if query:
#         response = rag_chain.invoke(query)
#         st.write("### 📌 Answer:")
#         st.write(response)


# import streamlit as st

# st.title("Test Streamlit App")
# st.write("If you see this, Streamlit is working!")

# if st.button("Click me"):
#     st.write("Button clicked!")

# Setup Weaviate Schema
setup_weaviate_schema()

st.title("📕 PDF-Based Multimodal RAG")

# Upload PDF File
uploaded_file = st.file_uploader("Upload a PDF Manual", type=["pdf"])
if uploaded_file:
    file_path = f"temp/{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    store_pdf(file_path)
    st.success("✅ PDF processed and stored in vector database!")

# Search Query
query = st.text_input("Enter search query:")
if st.button("Search"):
    response, retrieved_data = create_rag_chain(query)
    
    st.subheader("📝 LLM Response")
    st.write(response)

    st.subheader("🔍 Retrieved Data")
    for item in retrieved_data:
        if item["type"] == "text":
            st.write(f"📄 {item['content']}")
        elif item["type"] == "image":
            st.image(item["content"], caption="Retrieved Image")