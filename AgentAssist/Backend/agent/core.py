# agent/core.py
import logging
from typing import Dict, List, Optional, Any
import json
import os
from enum import Enum

from .memory import ConversationMemory
from .pdf_processor import PDFProcessor
from .tools import ToolRegistry

# Set up logging
logger = logging.getLogger(__name__)

class AgentState(Enum):
    """Enum representing the different states of the agent processing pipeline"""
    REASONING = "reasoning"
    ACTING = "acting"
    TALKING = "talking"

class AIAgent:
    """
    AI Agent with ReAct (Reason-Act-Talk) pattern implementation
    """
    
    def __init__(self, memory: ConversationMemory, pdf_processor: PDFProcessor):
        self.memory = memory
        self.pdf_processor = pdf_processor
        self.tool_registry = ToolRegistry()
        self.llm_config = self._load_llm_config()
        
        # Register default tools
        self._register_default_tools()
    
    def _load_llm_config(self) -> Dict:
        """Load configuration for the LLM"""
        # In a real implementation, you might load this from a config file
        return {
            "model": "gpt-3.5-turbo",  # Replace with your actual LLM
            "temperature": 0.7,
            "max_tokens": 1000
        }
    
    def _register_default_tools(self):
        """Register the default set of tools available to the agent"""
        # Register tools from the tools module
        from .tools import (
            search_pdf_tool, 
            summarize_pdf_tool, 
            web_search_tool, 
            calculator_tool,
            extract_csv_columns_tool,
            summarize_csv_tool,
            search_csv_tool,
            get_document_location_tool,
            anomaly_detection_tool
        )
        
        self.tool_registry.register_tool("search_pdf", search_pdf_tool)
        self.tool_registry.register_tool("summarize_pdf", summarize_pdf_tool)
        self.tool_registry.register_tool("web_search", web_search_tool)
        self.tool_registry.register_tool("calculator", calculator_tool)
        self.tool_registry.register_tool("extract_csv_columns", extract_csv_columns_tool)
        self.tool_registry.register_tool("summarize_csv", summarize_csv_tool)
        self.tool_registry.register_tool("search_csv", search_csv_tool)
        self.tool_registry.register_tool("get_document_location", get_document_location_tool)
        self.tool_registry.register_tool("anomaly_detection", anomaly_detection_tool)
    
    def process_message(self, user_message: str, conversation_id: str, rag_results: dict = None) -> dict:
        """
        Process a user message through the ReAct framework:
        1. Reason about the message and context
        2. Act (execute tools if needed)
        3. Talk (generate a response)
        Args:
            user_message: The user's input message
            conversation_id: Unique identifier for the conversation
            rag_results: Optional dict with RAG context (text, images, metadata)
        Returns:
            dict: The agent's response, possibly with images
        """
        # Add user message to memory
        self.memory.add_message(conversation_id, "user", user_message)
        # Get conversation context
        context = self.memory.get_context(conversation_id)
        # REASON: Analyze the user's request and determine next steps
        reasoning_result = self._reason(user_message, context)
        logger.info(f"Reasoning result: {reasoning_result}")
        # ACT: Execute tools if needed
        action_result = None
        if reasoning_result.get("should_use_tool", False):
            tool_name = reasoning_result.get("tool_name")
            tool_input = reasoning_result.get("tool_input")
            if tool_name and tool_input:
                logger.info(f"About to call tool: {tool_name} with input: {tool_input}")
                action_result = self._act(tool_name, tool_input, conversation_id)
                logger.info(f"Action result: {action_result}")
        # TALK: Generate the final response
        response = self._talk(user_message, context, reasoning_result, action_result, rag_results=rag_results)
        # Save the agent's response to memory
        if isinstance(response, dict):
            self.memory.add_message(conversation_id, "assistant", response.get("text", ""))
        else:
            self.memory.add_message(conversation_id, "assistant", response)
        return response
    
    def _call_llm(self, prompt: str, system_message: str = None, model_overrides: Dict = None) -> Dict:
        """
        Call the LLM with the given prompt
        
        Args:
            prompt: The user prompt to send to the LLM
            system_message: Optional system message to guide the LLM
            model_overrides: Optional overrides for model parameters
            
        Returns:
            Dict: The LLM response
        """
        try:
            # In a real implementation, you would replace this with your actual LLM API call
            import openai
            
            # Initialize the client
            openai.api_key = os.environ.get("OPENAI_API_KEY", "your-api-key")
            
            # Prepare the config
            config = self.llm_config.copy()
            if model_overrides:
                config.update(model_overrides)
                
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            response = openai.ChatCompletion.create(
                model=config["model"],
                messages=messages,
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )
            
            return {
                "content": response.choices[0].message.content,
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            # Return a fallback response
            return {
                "content": "I'm having trouble processing your request right now. Please try again later.",
                "error": str(e)
            }
    
    def _reason(self, user_message: str, context: Dict) -> Dict:
        """
        First stage of ReAct: Analyze the user's request and determine next steps
        Args:
            user_message: The user's input message
            context: Conversation context
        Returns:
            dict: Reasoning result with thought process and tool usage decision
        """
        # Create a prompt that includes the user's message and relevant context
        prompt = f"""
        User message: {user_message}
        
        Conversation context:
        - Message history: {json.dumps(context.get('messages', [])[-5:], indent=2)}  # Only include recent messages
        - Available documents: {json.dumps(context.get('documents', []), indent=2)}
        
        Based on this information, analyze what the user is asking for and determine the next steps.
        """
        
        # Call the LLM for reasoning
        response = self._call_llm(
            prompt=prompt,
            system_message="You are an AI assistant that helps analyze user requests and determine appropriate actions. Your task is to understand the user's intent and decide if any tools should be used to fulfill their request. Respond in JSON format with the following structure: {\"thought_process\": \"your reasoning\", \"should_use_tool\": boolean, \"tool_name\": \"tool name if needed\", \"tool_input\": {tool parameters if needed}}"
        )
        
        try:
            # Parse the JSON response
            result = json.loads(response["content"])
            return result
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return {
                "thought_process": "Error parsing LLM response",
                "should_use_tool": False,
                "tool_name": None,
                "tool_input": None
            }
    
    def _normalize_tool_name(self, tool_name: str) -> str:
        """
        Normalize tool names by:
        1. Converting to lowercase
        2. Removing spaces and underscores
        3. Removing the word 'tool' if present
        """
        if not tool_name:
            return ""
        # Convert to lowercase and remove spaces/underscores
        normalized = tool_name.lower().replace(" ", "").replace("_", "")
        # Remove 'tool' if present at the end
        if normalized.endswith("tool"):
            normalized = normalized[:-4]
        return normalized

    def _act(self, tool_name: str, tool_input: Dict, conversation_id: str) -> Dict:
        """
        Second stage of ReAct: Act by executing the appropriate tool
        
        Args:
            tool_name: The name of the tool to execute
            tool_input: The input parameters for the tool
            conversation_id: The conversation ID for context
            
        Returns:
            Dict: The result of executing the tool
        """
        try:
            normalized_name = self._normalize_tool_name(tool_name)
            tool_mapping = {
                "anomalydetection": "anomaly_detection",
                "searchpdf": "search_pdf",
                "summarizepdf": "summarize_pdf",
                "websearch": "web_search",
                "calculator": "calculator",
                "extractcsvcolumns": "extract_csv_columns",
                "summarizecsv": "summarize_csv",
                "searchcsv": "search_csv",
                "getdocumentlocation": "get_document_location"
            }
            actual_tool_name = tool_mapping.get(normalized_name)
            if not actual_tool_name:
                return {
                    "error": f"Tool '{tool_name}' not found. Available tools: {list(tool_mapping.keys())}",
                    "success": False
                }
            tool_fn = self.tool_registry.get_tool(actual_tool_name)
            if not tool_fn:
                return {
                    "error": f"Tool '{actual_tool_name}' not found",
                    "success": False
                }
            context = self.memory.get_context(conversation_id)
            tool_input["conversation_context"] = context
            logger.info(f"Calling tool function: {actual_tool_name} with input: {tool_input}")
            result = tool_fn(tool_input)
            logger.info(f"Tool function {actual_tool_name} returned: {result}")
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "error": f"Error executing tool: {str(e)}",
                "success": False
            }
    
    def _talk(self, user_message: str, context: Dict, reasoning_result: Dict, action_result: Optional[Dict] = None, rag_results: dict = None) -> dict:
        """
        Third stage of ReAct: Generate the final response to the user
        Args:
            user_message: The user's input message
            context: Conversation context
            reasoning_result: The result from the reasoning stage
            action_result: The result from the action stage, if any
            rag_results: Optional dict with RAG context (text, images, metadata)
        Returns:
            dict: The final response to the user
        """
        # Check if this is a file location response
        if reasoning_result.get("file_location"):
            filename = reasoning_result.get("filename", "the file")
            return {
                "text": f"The {filename} is stored at: {reasoning_result['file_location']}"
            }

        # Determine if we're dealing with a CSV file
        is_csv_request = False
        if action_result and isinstance(action_result, dict):
            tool_name = reasoning_result.get("tool_name", "")
            is_csv_request = any(tool in tool_name for tool in ["csv", "extract_csv"])

        if is_csv_request:
            system_message = """
            You are a helpful AI assistant with CSV data analysis capabilities.
            Generate a natural, helpful response to the user's message based on the CSV data analysis results.
            Make your response conversational and user-friendly.
            If you're showing data from a CSV file, present it in a clear and organized way.
            Always mention the file path of any CSV files you're working with.
            """
        else:
            system_message = """
            You are a helpful AI assistant with PDF processing capabilities.
            Generate a natural, helpful response to the user's message based on the reasoning and tool results provided.
            Make your response conversational and user-friendly.
            If you used information from a PDF, mention which PDF the information came from and its file path.
            """

        # Create a prompt that includes all the relevant information
        prompt = f"""
        User message: {user_message}
        Reasoning: {json.dumps(reasoning_result, indent=2)}
        Tool execution: {"N/A" if action_result is None else json.dumps(action_result, indent=2)}
        """

        # Add document information to the prompt
        if context.get('documents'):
            prompt += "\n\nAvailable documents:\n"
            for doc in context['documents']:
                prompt += f"- {doc.get('filename', 'Unknown file')}: {doc.get('file_path', 'No path available')}\n"

        prompt += "\nBased on this information, provide a helpful response to the user."

        # Only add RAG context for PDF-related requests
        if not is_csv_request and rag_results:
            if rag_results.get("context"):
                prompt += "\n\nRelevant information from the PDF(s):\n" + "\n".join(rag_results["context"])

        # Call the LLM for response generation
        response = self._call_llm(
            prompt=prompt,
            system_message=system_message
        )

        # Add state tracking
        conversation_id = context.get("conversation_id")
        self.memory.add_state_data(conversation_id=conversation_id, 
                                  state=AgentState.TALKING.value,
                                  data={
                                      "response": response["content"]
                                  })

        # Return response with images only for PDF-related requests
        if not is_csv_request and rag_results and rag_results.get("images"):
            return {"text": response["content"], "images": rag_results["images"]}
        return {"text": response["content"]}