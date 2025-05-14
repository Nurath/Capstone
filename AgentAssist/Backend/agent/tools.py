# agent/tools.py
from typing import Dict, List, Any, Callable, Optional
import logging
import json
import re
import math
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for tools that can be used by the agent"""
    
    def __init__(self):
        """Initialize the tool registry"""
        self.tools = {}
    
    def register_tool(self, name: str, tool_fn: Callable) -> None:
        """
        Register a tool function
        
        Args:
            name: Name of the tool
            tool_fn: Function that implements the tool
        """
        self.tools[name] = tool_fn
        logger.info(f"Registered tool: {name}")
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """
        Get a tool function by name
        
        Args:
            name: Name of the tool
            
        Returns:
            Callable: The tool function or None if not found
        """
        return self.tools.get(name)
    
    def has_tool(self, name: str) -> bool:
        """
        Check if a tool exists
        
        Args:
            name: Name of the tool
            
        Returns:
            bool: True if the tool exists, False otherwise
        """
        return name in self.tools
    
    def list_tools(self) -> List[str]:
        """
        List all registered tools
        
        Returns:
            List[str]: List of tool names
        """
        return list(self.tools.keys())


def search_pdf_tool(params: Dict) -> Dict:
    """
    Tool for searching PDFs
    
    Args:
        params: Dictionary with parameters:
            - query: Search query
            - doc_id: Optional specific document ID to search
            - conversation_context: Context of the conversation
            
    Returns:
        Dict: Search results
    """
    try:
        query = params.get("query")
        doc_id = params.get("doc_id")
        conversation_context = params.get("conversation_context", {})
        
        if not query:
            return {
                "error": "Missing required parameter: query",
                "results": []
            }
        
        # Get available documents from conversation context
        available_docs = conversation_context.get("documents", [])
        
        # If no specific doc_id is provided but documents are available, search all of them
        results = []
        if not doc_id and available_docs:
            # In a real implementation, you would iterate through available documents
            # For this sample, we'll just simulate some results
            
            for doc in available_docs:
                doc_id = doc.get("doc_id")
                filename = doc.get("filename", "Unknown")
                
                # Simulate searching this document
                from .pdf_processor import PDFProcessor
                pdf_processor = PDFProcessor()
                doc_results = pdf_processor.search_pdf(doc_id, query)
                
                if doc_results:
                    # Add document info to each result
                    for result in doc_results:
                        result["document"] = {
                            "doc_id": doc_id,
                            "filename": filename
                        }
                    
                    results.extend(doc_results)
        
        # If a specific doc_id is provided, search only that document
        elif doc_id:
            # Check if the document exists in the conversation context
            doc_exists = any(doc.get("doc_id") == doc_id for doc in available_docs)
            
            if not doc_exists:
                return {
                    "error": f"Document with ID '{doc_id}' not found in conversation context",
                    "results": []
                }
            
            # Search the specific document
            from .pdf_processor import PDFProcessor
            pdf_processor = PDFProcessor()
            doc_results = pdf_processor.search_pdf(doc_id, query)
            
            # Add document info to each result
            filename = next((doc.get("filename", "Unknown") for doc in available_docs if doc.get("doc_id") == doc_id), "Unknown")
            for result in doc_results:
                result["document"] = {
                    "doc_id": doc_id,
                    "filename": filename
                }
            
            results = doc_results
        
        else:
            return {
                "error": "No documents available to search",
                "results": []
            }
        
        # Sort results by relevance
        results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        
        return {
            "query": query,
            "results": results,
            "result_count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error in search_pdf_tool: {str(e)}")
        return {
            "error": f"Error searching PDF: {str(e)}",
            "results": []
        }


def summarize_pdf_tool(params: Dict) -> Dict:
    """
    Tool for summarizing PDFs
    
    Args:
        params: Dictionary with parameters:
            - doc_id: Document ID to summarize
            - max_length: Optional maximum length of the summary
            - conversation_context: Context of the conversation
            
    Returns:
        Dict: Summary result
    """
    try:
        doc_id = params.get("doc_id")
        max_length = params.get("max_length", 1000)
        conversation_context = params.get("conversation_context", {})
        
        if not doc_id:
            return {
                "error": "Missing required parameter: doc_id",
                "summary": None
            }
        
        # Check if the document exists in the conversation context
        available_docs = conversation_context.get("documents", [])
        doc_exists = any(doc.get("doc_id") == doc_id for doc in available_docs)
        
        if not doc_exists:
            return {
                "error": f"Document with ID '{doc_id}' not found in conversation context",
                "summary": None
            }
        
        # Get the document summary
        from .pdf_processor import PDFProcessor
        pdf_processor = PDFProcessor()
        summary_result = pdf_processor.get_pdf_summary(doc_id, max_length)
        
        return summary_result
        
    except Exception as e:
        logger.error(f"Error in summarize_pdf_tool: {str(e)}")
        return {
            "error": f"Error summarizing PDF: {str(e)}",
            "summary": None
        }


def web_search_tool(params: Dict) -> Dict:
    """
    Tool for web search (simulated)
    
    Args:
        params: Dictionary with parameters:
            - query: Search query
            - num_results: Optional number of results to return
            
    Returns:
        Dict: Search results
    """
    try:
        query = params.get("query")
        num_results = params.get("num_results", 5)
        
        if not query:
            return {
                "error": "Missing required parameter: query",
                "results": []
            }
        
        # In a real implementation, you would use a search API
        # For this sample, we'll simulate some results
        
        # Simulate search results
        search_results = []
        for i in range(min(num_results, 5)):  # Max 5 simulated results
            search_results.append({
                "title": f"Simulated search result {i+1} for '{query}'",
                "snippet": f"This is a simulated search result for the query '{query}'. "
                          f"In a real implementation, this would be actual content from the web.",
                "url": f"https://example.com/result-{i+1}",
                "rank": i+1
            })
        
        return {
            "query": query,
            "results": search_results,
            "result_count": len(search_results)
        }
        
    except Exception as e:
        logger.error(f"Error in web_search_tool: {str(e)}")
        return {
            "error": f"Error performing web search: {str(e)}",
            "results": []
        }


def calculator_tool(params: Dict) -> Dict:
    """
    Tool for performing calculations
    
    Args:
        params: Dictionary with parameters:
            - expression: Math expression to evaluate
            
    Returns:
        Dict: Calculation result
    """
    try:
        expression = params.get("expression")
        
        if not expression:
            return {
                "error": "Missing required parameter: expression",
                "result": None
            }
        
        # Clean and validate the expression
        # Remove any characters that aren't math operators, numbers, or common math symbols
        clean_expr = re.sub(r'[^0-9+\-*/().^\s]', '', expression)
        
        # Safety check: Don't evaluate if the expression looks different after cleaning
        if clean_expr != expression:
            return {
                "error": "Invalid characters in expression",
                "result": None,
                "expression": expression
            }
        
        # Evaluate the expression
        # Note: In a production environment, you should use a safer way to evaluate math expressions
        # or a dedicated math library with proper sandboxing
        result = eval(clean_expr, {"__builtins__": {}}, {"math": math})
        
        return {
            "expression": expression,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error in calculator_tool: {str(e)}")
        return {
            "error": f"Error calculating expression: {str(e)}",
            "result": None,
            "expression": params.get("expression", "")
        }


def extract_csv_columns_tool(params: Dict) -> Dict:
    """
    Tool for extracting column information from a CSV file
    
    Args:
        params: Dictionary with parameters:
            - doc_id: Document ID of the CSV file
            - conversation_context: Context of the conversation
            
    Returns:
        Dict: Column information
    """
    try:
        doc_id = params.get("doc_id")
        conversation_context = params.get("conversation_context", {})
        
        if not doc_id:
            return {
                "error": "Missing required parameter: doc_id",
                "columns": []
            }
        
        # Check if the document exists in the conversation context
        available_docs = conversation_context.get("documents", [])
        doc_exists = any(doc.get("doc_id") == doc_id for doc in available_docs)
        
        if not doc_exists:
            return {
                "error": f"Document with ID '{doc_id}' not found in conversation context",
                "columns": []
            }
        
        # In a real implementation, you would read the CSV file and extract column information
        # For this sample, we'll return a simulated response
        return {
            "doc_id": doc_id,
            "columns": [
                {"name": "column1", "type": "string"},
                {"name": "column2", "type": "number"},
                {"name": "column3", "type": "date"}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in extract_csv_columns_tool: {str(e)}")
        return {
            "error": f"Error extracting CSV columns: {str(e)}",
            "columns": []
        }


def summarize_csv_tool(params: Dict) -> Dict:
    """
    Tool for summarizing CSV file contents
    
    Args:
        params: Dictionary with parameters:
            - doc_id: Document ID of the CSV file
            - conversation_context: Context of the conversation
            
    Returns:
        Dict: Summary of CSV contents
    """
    try:
        doc_id = params.get("doc_id")
        conversation_context = params.get("conversation_context", {})
        
        if not doc_id:
            return {
                "error": "Missing required parameter: doc_id",
                "summary": None
            }
        
        # Check if the document exists in the conversation context
        available_docs = conversation_context.get("documents", [])
        doc_exists = any(doc.get("doc_id") == doc_id for doc in available_docs)
        
        if not doc_exists:
            return {
                "error": f"Document with ID '{doc_id}' not found in conversation context",
                "summary": None
            }
        
        # In a real implementation, you would read the CSV file and generate a summary
        # For this sample, we'll return a simulated response
        return {
            "doc_id": doc_id,
            "summary": {
                "row_count": 100,
                "column_count": 3,
                "column_types": {
                    "column1": "string",
                    "column2": "number",
                    "column3": "date"
                },
                "sample_data": [
                    {"column1": "value1", "column2": 123, "column3": "2025-01-01"},
                    {"column1": "value2", "column2": 456, "column3": "2025-01-02"}
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in summarize_csv_tool: {str(e)}")
        return {
            "error": f"Error summarizing CSV: {str(e)}",
            "summary": None
        }


def search_csv_tool(params: Dict) -> Dict:
    """
    Tool for searching through CSV data
    
    Args:
        params: Dictionary with parameters:
            - query: Search query
            - doc_id: Document ID of the CSV file
            - conversation_context: Context of the conversation
            
    Returns:
        Dict: Search results
    """
    try:
        query = params.get("query")
        doc_id = params.get("doc_id")
        conversation_context = params.get("conversation_context", {})
        
        if not query:
            return {
                "error": "Missing required parameter: query",
                "results": []
            }
        
        if not doc_id:
            return {
                "error": "Missing required parameter: doc_id",
                "results": []
            }
        
        # Check if the document exists in the conversation context
        available_docs = conversation_context.get("documents", [])
        doc_exists = any(doc.get("doc_id") == doc_id for doc in available_docs)
        
        if not doc_exists:
            return {
                "error": f"Document with ID '{doc_id}' not found in conversation context",
                "results": []
            }
        
        # In a real implementation, you would search through the CSV data
        # For this sample, we'll return a simulated response
        return {
            "query": query,
            "doc_id": doc_id,
            "results": [
                {"column1": "value1", "column2": 123, "column3": "2025-01-01"},
                {"column1": "value2", "column2": 456, "column3": "2025-01-02"}
            ],
            "result_count": 2
        }
        
    except Exception as e:
        logger.error(f"Error in search_csv_tool: {str(e)}")
        return {
            "error": f"Error searching CSV: {str(e)}",
            "results": []
        }


def get_document_location_tool(params: Dict) -> Dict:
    """
    Tool for getting document location information
    
    Args:
        params: Dictionary with parameters:
            - doc_id: Optional specific document ID to get location for
            - conversation_context: Context of the conversation
            
    Returns:
        Dict: Document location information
    """
    try:
        doc_id = params.get("doc_id")
        conversation_context = params.get("conversation_context", {})
        
        # Get available documents from conversation context
        available_docs = conversation_context.get("documents", [])
        
        if not available_docs:
            return {
                "error": "No documents available in the conversation",
                "locations": []
            }
        
        # If a specific doc_id is provided, get location for that document
        if doc_id:
            doc = next((doc for doc in available_docs if doc.get("doc_id") == doc_id), None)
            if not doc:
                return {
                    "error": f"Document with ID '{doc_id}' not found in conversation context",
                    "locations": []
                }
            
            file_path = doc.get("file_path")
            if not file_path:
                return {
                    "error": f"File path not found for document {doc_id}",
                    "locations": []
                }
            
            return {
                "locations": [{
                    "doc_id": doc_id,
                    "filename": doc.get("filename", "Unknown"),
                    "file_path": file_path,
                    "file_type": doc.get("file_type", "Unknown")
                }]
            }
        
        # If no specific doc_id, return locations for all documents
        locations = []
        for doc in available_docs:
            file_path = doc.get("file_path")
            if file_path:
                locations.append({
                    "doc_id": doc.get("doc_id"),
                    "filename": doc.get("filename", "Unknown"),
                    "file_path": file_path,
                    "file_type": doc.get("file_type", "Unknown")
                })
        
        if not locations:
            return {
                "error": "No file paths found for any documents",
                "locations": []
            }
        
        return {
            "locations": locations
        }
        
    except Exception as e:
        logger.error(f"Error in get_document_location_tool: {str(e)}")
        return {
            "error": f"Error getting document location: {str(e)}",
            "locations": []
        }


def anomaly_detection_tool(params: Dict) -> Dict:
    """
    Tool for running anomaly detection on time series data
    
    Args:
        params: Dictionary with parameters:
            - file_path: Path to the CSV file containing the data
            - window_size: Optional window size for sequence creation (default: 10)
            - forecast_horizon: Optional forecast horizon (default: 1)
            - machine_serial: Optional specific machine serial to analyze
            
    Returns:
        Dict: Anomaly detection results including summary and figures
    """
    logger.info(f"anomaly_detection_tool called with params: {params}")
    try:
        file_path = params.get("file_path")
        window_size = params.get("window_size", 10)
        forecast_horizon = params.get("forecast_horizon", 1)
        machine_serial = params.get("machine_serial")
        
        if not file_path:
            logger.error("Missing required parameter: file_path")
            return {
                "error": "Missing required parameter: file_path",
                "summary": None,
                "figures": []
            }
        
        # Import and run the anomaly detection
        from .toolbox import run_anomaly_detection
        result = run_anomaly_detection(
            file_path,
            window_size=window_size,
            forecast_horizon=forecast_horizon,
            machine_serial=machine_serial
        )
        logger.info("anomaly_detection_tool completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error in anomaly_detection_tool: {str(e)}")
        return {
            "error": f"Error running anomaly detection: {str(e)}",
            "summary": None,
            "figures": []
        }


