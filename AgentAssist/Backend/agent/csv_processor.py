import pandas as pd
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

class CSVProcessor:
    """Class for processing CSV files"""
    
    def __init__(self):
        """Initialize the CSV processor"""
        self.processed_files = {}
    
    def process_csv(self, file_path: str, doc_id: str) -> Dict:
        """
        Process a CSV file and store its contents
        
        Args:
            file_path: Path to the CSV file
            doc_id: Unique identifier for the document
            
        Returns:
            Dict: Processing result with metadata
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "error": f"File not found: {file_path}",
                    "success": False
                }
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Store the processed data
            self.processed_files[doc_id] = {
                "dataframe": df,
                "file_path": file_path,
                "columns": list(df.columns),
                "row_count": len(df),
                "column_count": len(df.columns)
            }
            
            return {
                "success": True,
                "doc_id": doc_id,
                "columns": list(df.columns),
                "row_count": len(df),
                "column_count": len(df.columns)
            }
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            return {
                "error": f"Error processing CSV file: {str(e)}",
                "success": False
            }
    
    def get_columns(self, doc_id: str) -> Dict:
        """
        Get column information for a processed CSV file
        
        Args:
            doc_id: Document ID
            
        Returns:
            Dict: Column information
        """
        if doc_id not in self.processed_files:
            return {
                "error": f"Document {doc_id} not found",
                "success": False
            }
        
        file_info = self.processed_files[doc_id]
        return {
            "success": True,
            "columns": file_info["columns"],
            "column_count": file_info["column_count"]
        }
    
    def get_summary(self, doc_id: str) -> Dict:
        """
        Get a summary of the CSV file contents
        
        Args:
            doc_id: Document ID
            
        Returns:
            Dict: Summary information
        """
        if doc_id not in self.processed_files:
            return {
                "error": f"Document {doc_id} not found",
                "success": False
            }
        
        file_info = self.processed_files[doc_id]
        df = file_info["dataframe"]
        
        # Generate summary statistics
        summary = {
            "success": True,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "summary_stats": {}
        }
        
        # Add summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            summary["summary_stats"][col] = {
                "mean": df[col].mean(),
                "std": df[col].std(),
                "min": df[col].min(),
                "max": df[col].max()
            }
        
        return summary
    
    def search_data(self, doc_id: str, query: str) -> Dict:
        """
        Search through the CSV data
        
        Args:
            doc_id: Document ID
            query: Search query
            
        Returns:
            Dict: Search results
        """
        if doc_id not in self.processed_files:
            return {
                "error": f"Document {doc_id} not found",
                "success": False
            }
        
        try:
            df = self.processed_files[doc_id]["dataframe"]
            
            # Convert query to lowercase for case-insensitive search
            query = query.lower()
            
            # Search in all columns
            results = []
            for col in df.columns:
                # Convert column values to string and search
                matches = df[df[col].astype(str).str.lower().str.contains(query, na=False)]
                
                if not matches.empty:
                    for _, row in matches.iterrows():
                        results.append({
                            "column": col,
                            "value": str(row[col]),
                            "row_index": row.name
                        })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "result_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching CSV data: {str(e)}")
            return {
                "error": f"Error searching CSV data: {str(e)}",
                "success": False
            } 