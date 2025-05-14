# agent/memory.py
from typing import Dict, List, Any, Optional
import json
import logging
import time

logger = logging.getLogger(__name__)

class ConversationMemory:
    """
    Memory component to store and retrieve conversation history and context
    """
    
    def __init__(self):
        """Initialize the memory storage"""
        # In-memory storage - in production, use a database
        self.conversations = {}
        self.documents = {}
        self.state_data = {}
    
    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """
        Add a message to the conversation history
        
        Args:
            conversation_id: Unique identifier for the conversation
            role: Role of the message sender (e.g., 'user', 'assistant')
            content: Content of the message
        """
        # Create conversation if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "messages": [],
                "documents": [],
                "created_at": time.time()
            }
        
        # Add the message with timestamp
        self.conversations[conversation_id]["messages"].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        
        # Log for debugging
        logger.debug(f"Added message to conversation {conversation_id}: {role}: {content[:50]}...")
    
    def add_file_context(self, conversation_id: str, doc_id: str, filename: str) -> None:
        """
        Associate a document with a conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
            doc_id: Unique identifier for the document
            filename: Original filename of the document
        """
        # Create conversation if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "messages": [],
                "documents": [],
                "created_at": time.time()
            }
        
        # Check if this document is already associated
        for doc in self.conversations[conversation_id]["documents"]:
            if doc["doc_id"] == doc_id:
                return  # Already associated
        
        # Add the document association
        self.conversations[conversation_id]["documents"].append({
            "doc_id": doc_id,
            "filename": filename,
            "added_at": time.time()
        })
        
        # Also add system message about the uploaded document
        system_message = f"[System] File uploaded: {filename}"
        self.add_message(conversation_id, "system", system_message)
        
        logger.info(f"Added document {doc_id} ({filename}) to conversation {conversation_id}")
    
    def get_context(self, conversation_id: str) -> Dict:
        """
        Get the full context for a conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dict containing conversation history and associated documents
        """
        if conversation_id not in self.conversations:
            # Return empty context if conversation doesn't exist
            logger.info(f"No conversation found for ID {conversation_id}")
            return {
                "conversation_id": conversation_id,
                "messages": [],
                "documents": []
            }
        
        # Get the base conversation data
        context = self.conversations[conversation_id].copy()
        context["conversation_id"] = conversation_id
        
        # Expand document information with metadata
        expanded_docs = []
        for doc_ref in context["documents"]:
            doc_id = doc_ref["doc_id"]
            if doc_id in self.documents:
                # Add document metadata and file path
                doc_info = {
                    "doc_id": doc_id,
                    "filename": doc_ref["filename"],
                    "metadata": self.documents[doc_id].get("metadata", {}),
                    "file_path": self.documents[doc_id].get("file_path"),  # Include file path if it exists
                    "file_type": self.documents[doc_id].get("metadata", {}).get("file_type")  # Include file type
                }
                logger.info(f"Expanded document info for {doc_id}: {doc_info}")
                expanded_docs.append(doc_info)
            else:
                logger.warning(f"Document {doc_id} not found in memory")
        
        context["documents"] = expanded_docs
        logger.info(f"Returning context for conversation {conversation_id}: {context}")
        return context
    
    def add_document(self, doc_id: str, metadata: Dict, rag_context: Dict = None) -> None:
        """
        Store document metadata and optional RAG context
        Args:
            doc_id: Unique identifier for the document
            metadata: Metadata about the document (title, page count, etc.)
            rag_context: Optional dict with RAG context (e.g., folder_path, base_name)
        """
        # Ensure file_path is included in metadata if it exists
        if 'file_path' in metadata:
            logger.info(f"Adding document {doc_id} with file_path: {metadata['file_path']}")
            self.documents[doc_id] = {
                "metadata": metadata,
                "added_at": time.time(),
                "rag_context": rag_context or {},
                "file_path": metadata['file_path']  # Store file_path at the top level for easy access
            }
        else:
            logger.info(f"Adding document {doc_id} without file_path")
            self.documents[doc_id] = {
                "metadata": metadata,
                "added_at": time.time(),
                "rag_context": rag_context or {}
            }
    
    def add_state_data(self, conversation_id: str, state: str, data: Dict) -> None:
        """
        Store state data for debugging and monitoring
        
        Args:
            conversation_id: Unique identifier for the conversation
            state: The current state (reasoning, acting, talking)
            data: The data associated with this state
        """
        if conversation_id not in self.state_data:
            self.state_data[conversation_id] = []
        
        self.state_data[conversation_id].append({
            "state": state,
            "data": data,
            "timestamp": time.time()
        })
    
    def get_state_history(self, conversation_id: str) -> List[Dict]:
        """
        Get the state history for a conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of state data entries
        """
        return self.state_data.get(conversation_id, [])
    
    def reset_conversation(self, conversation_id: str) -> None:
        """
        Reset a conversation (clear messages but keep document associations)
        
        Args:
            conversation_id: Unique identifier for the conversation
        """
        if conversation_id in self.conversations:
            # Keep document associations but clear messages
            documents = self.conversations[conversation_id]["documents"]
            self.conversations[conversation_id] = {
                "messages": [],
                "documents": documents,
                "created_at": time.time()  # Reset creation time
            }
            
            # Clear state data for this conversation
            if conversation_id in self.state_data:
                self.state_data[conversation_id] = []
            
            logger.info(f"Reset conversation {conversation_id}")
        else:
            logger.warning(f"Tried to reset non-existent conversation {conversation_id}")