# agent/pdf_processor.py
import logging
import uuid
import os
from typing import Dict, List, Any, Optional
from .extract_pdf_content import extract_pdf_content
from .create_chunks import create_chunks_with_references
from .embed_chunks import embed_chunks
from .store_faiss import store_faiss_index, load_faiss_index
from sentence_transformers import SentenceTransformer
from .query_engine import retrieve_relevant_chunks
import tempfile
import shutil
import json
from PIL import Image
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Processes PDF files for information extraction and querying
    """
    
    def __init__(self):
        """Initialize the PDF processor"""
        self.processed_pdfs = {}
        self.chunk_size = 1000  # Default chunk size for text splitting
        
    def process_pdf(self, file_path: str, conversation_id: str = None) -> str:
        """
        Process a PDF file to extract text and prepare for querying
        
        Args:
            file_path: Path to the PDF file
            conversation_id: Optional conversation ID for context
            
        Returns:
            str: Unique document ID for the processed PDF
        """
        try:
            # Generate a unique ID for this document
            doc_id = str(uuid.uuid4())
            
            # Extract text from PDF
            text_chunks, metadata = self._extract_text_from_pdf(file_path)
            
            # Store the processed data
            self.processed_pdfs[doc_id] = {
                "file_path": file_path,
                "text_chunks": text_chunks,
                "metadata": metadata,
                "conversation_id": conversation_id,
                "processed_at": os.path.getmtime(file_path)
            }
            
            logger.info(f"Processed PDF {file_path} with doc_id {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise

    @staticmethod
    def create_output_folder(filename):
        base_name = os.path.splitext(filename)[0]
        folder_path = os.path.join("output", base_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path, base_name

    def process_pdf_for_rag(self, pdf_path):
        """
        Process a PDF file for RAG by extracting content, creating chunks, and storing them.
        Args:
            pdf_path (str): Path to the PDF file
        Returns:
            tuple: (base_name, folder_path) where base_name is the name of the processed PDF
                   and folder_path is the directory containing the processed files
        """
        # Create output folder structure
        filename = os.path.basename(pdf_path)
        folder_path, base_name = self.create_output_folder(filename)
        # Extract content from PDF
        blocks = extract_pdf_content(pdf_path)
        # Create chunks with references
        chunks = create_chunks_with_references(blocks)
        # Process images in chunks
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
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        buf = BytesIO()
                        img.save(buf, format="JPEG")
                        images_base64.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
            if images_base64:
                chunk.setdefault("metadata", {})["images_base64"] = images_base64
        # Save chunks to JSON
        with open(os.path.join(folder_path, "chunks.json"), "w") as f:
            json.dump(chunks, f, indent=2)
        # Create and store embeddings
        embeddings, texts = embed_chunks(chunks)
        if embeddings is None or len(embeddings) == 0 or len(embeddings.shape) < 2:
            raise ValueError("Embedding failed or returned invalid shape.")
        # Store FAISS index
        store_faiss_index(
            embeddings, 
            dim=embeddings.shape[1], 
            path=os.path.join(folder_path, "faiss_index.index")
        )
        return base_name, folder_path

    def get_rag_context(self, input_query, folder_path, base_name, top_k=3):
        """
        Retrieve relevant context from a processed RAG system.
        Args:
            input_query (str): The query to search for relevant context
            folder_path (str): Path to the folder containing processed RAG files
            base_name (str): Base name of the processed PDF
            top_k (int, optional): Number of most relevant chunks to retrieve. Defaults to 3.
        Returns:
            dict: A dictionary containing:
                - 'context': List of relevant text chunks
                - 'metadata': List of metadata for each chunk
                - 'images': List of base64 encoded images if available
        """
        try:
            # Load the chunks
            chunks_path = os.path.join(folder_path, "chunks.json")
            with open(chunks_path, 'r') as f:
                chunks = json.load(f)
            # Load the FAISS index
            faiss_index_path = os.path.join(folder_path, "faiss_index.index")
            faiss_index = load_faiss_index(faiss_index_path)
            # Initialize the model for embeddings
            model = SentenceTransformer("all-MiniLM-L6-v2")
            # Retrieve relevant chunks
            retrieved_chunks = retrieve_relevant_chunks(
                input_query, 
                chunks, 
                faiss_index, 
                model=model, 
                top_k=top_k
            )
            # Process the retrieved chunks
            context_list = []
            metadata_list = []
            images_list = []
            for chunk in retrieved_chunks:
                # Add text context
                context_list.append(chunk["text"])
                # Add metadata if available
                if "metadata" in chunk:
                    metadata_list.append(chunk["metadata"])
                    # Add images if available
                    if "images_base64" in chunk["metadata"]:
                        images_list.extend(chunk["metadata"]["images_base64"])
            return {
                "context": context_list,
                "metadata": metadata_list,
                "images": images_list
            }
        except Exception as e:
            raise Exception(f"Error retrieving RAG context: {str(e)}")

    def _extract_text_from_pdf(self, file_path: str) -> tuple:
        """
        Extract text and metadata from a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            tuple: (List of text chunks, Metadata dictionary)
        """
        try:
            # In a real implementation, you'd use libraries like PyPDF2, pdfplumber, or pymupdf
            # For this sample, we'll simulate successful extraction
            
            # Simulate metadata extraction
            metadata = {
                "title": os.path.basename(file_path),
                "pages": 10,  # Simulated page count
                "author": "Unknown",
                "creation_date": os.path.getctime(file_path)
            }
            
            # Simulate text extraction with chunking
            # In a real implementation, you'd read the actual content
            text_chunks = [
                f"This is simulated text from chunk {i} of the PDF {os.path.basename(file_path)}."
                for i in range(10)  # Simulate 10 chunks
            ]
            
            return text_chunks, metadata
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            # Return minimal data in case of error
            return [f"Error extracting text: {str(e)}"], {"title": os.path.basename(file_path)}
    
    def search_pdf(self, doc_id: str, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search a processed PDF for relevant content
        
        Args:
            doc_id: Document ID of the processed PDF
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict]: List of relevant chunks with metadata
        """
        try:
            # Check if document exists
            if doc_id not in self.processed_pdfs:
                logger.warning(f"Attempted to search non-existent document {doc_id}")
                return []
            
            # Get document data
            doc_data = self.processed_pdfs[doc_id]
            text_chunks = doc_data["text_chunks"]
            
            # In a real implementation, you'd use a vector database or text search
            # For this sample, we'll simulate search
            
            # Simulate finding relevant chunks
            # In real implementation, use semantic search or keyword matching
            results = []
            for i, chunk in enumerate(text_chunks):
                # Simple simulation - check if any word in query appears in chunk
                relevance = 0
                for word in query.lower().split():
                    if word in chunk.lower():
                        relevance += 1
                
                if relevance > 0:
                    results.append({
                        "chunk_id": i,
                        "text": chunk,
                        "relevance": relevance,
                        "page": (i % 10) + 1  # Simulate page numbers
                    })
            
            # Sort by relevance and limit results
            results.sort(key=lambda x: x["relevance"], reverse=True)
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching PDF {doc_id}: {str(e)}")
            return []
    
    def get_pdf_summary(self, doc_id: str, max_length: int = 1000) -> Dict:
        """
        Generate or retrieve a summary of the PDF
        
        Args:
            doc_id: Document ID of the processed PDF
            max_length: Maximum length of the summary
            
        Returns:
            Dict: Summary data for the PDF
        """
        try:
            # Check if document exists
            if doc_id not in self.processed_pdfs:
                logger.warning(f"Attempted to summarize non-existent document {doc_id}")
                return {"error": "Document not found"}
            
            # Get document data
            doc_data = self.processed_pdfs[doc_id]
            
            # In a real implementation, you'd generate a summary using an LLM
            # For this sample, we'll return a simulated summary
            
            metadata = doc_data["metadata"]
            filename = os.path.basename(doc_data["file_path"])
            
            # Simulate a summary
            summary = f"""
            Summary of document '{filename}':
            
            This document appears to be {metadata.get('pages', 'unknown')} pages long.
            It covers various topics and contains detailed information that would be 
            analyzed more thoroughly in a real implementation.
            
            The document was created on {metadata.get('creation_date', 'unknown date')}.
            
            This is a simulated summary for demonstration purposes.
            """
            
            # Clean up whitespace and limit length
            summary = ' '.join(summary.split())
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return {
                "doc_id": doc_id,
                "title": metadata.get("title", filename),
                "summary": summary,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error generating summary for PDF {doc_id}: {str(e)}")
            return {"error": f"Error generating summary: {str(e)}"}
    
    def get_document_metadata(self, doc_id: str) -> Dict:
        """
        Get metadata about a processed document
        
        Args:
            doc_id: Document ID of the processed PDF
            
        Returns:
            Dict: Metadata for the document
        """
        if doc_id not in self.processed_pdfs:
            return {"error": "Document not found"}
        
        doc_data = self.processed_pdfs[doc_id]
        return {
            "doc_id": doc_id,
            "filename": os.path.basename(doc_data["file_path"]),
            "metadata": doc_data["metadata"],
            "chunk_count": len(doc_data["text_chunks"]),
            "processed_at": doc_data["processed_at"]
        }