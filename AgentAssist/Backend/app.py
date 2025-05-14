# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
import logging
import shutil

# Import our custom modules
from agent.core import AIAgent
from agent.pdf_processor import PDFProcessor
from agent.memory import ConversationMemory
from agent.csv_processor import CSVProcessor
from agent.toolbox import run_anomaly_detection, run_forecasting, generate_synthetic_data

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize components
memory = ConversationMemory()
pdf_processor = PDFProcessor()
csv_processor = CSVProcessor()
agent = AIAgent(memory=memory, pdf_processor=pdf_processor)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
CSV_FOLDER = os.path.join(UPLOAD_FOLDER, 'csv_files')
os.makedirs(CSV_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a chat message from the user"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))
        
        # Get conversation context
        context = memory.get_context(conversation_id)
        logger.info(f"Context for conversation {conversation_id}: {context}")
        logger.info(f"Documents in context: {context.get('documents', [])}")
        
        # Check if we're dealing with a CSV file
        is_csv_request = False
        if context.get('documents'):
            for doc in context['documents']:
                if doc.get('file_type') == 'csv':
                    is_csv_request = True
                    break
        
        # Only get RAG results for PDF files
        rag_results = None
        if not is_csv_request and context.get('documents'):
            for doc in context['documents']:
                doc_id = doc.get('doc_id')
                doc_info = memory.documents.get(doc_id, {})
                rag_ctx = doc_info.get('rag_context', {})
                if rag_ctx.get('folder_path') and rag_ctx.get('base_name'):
                    rag_results = pdf_processor.get_rag_context(
                        user_message,
                        rag_ctx['folder_path'],
                        rag_ctx['base_name'],
                        top_k=3
                    )
                    break
        
        # Process the message through our agent
        response = agent.process_message(user_message, conversation_id, rag_results=rag_results)
        
        return jsonify({
            'response': response.get('text') if isinstance(response, dict) else response,
            'images': response.get('images', []) if isinstance(response, dict) else [],
            'conversation_id': conversation_id,
            'documents': context.get('documents', [])  # Include documents with file paths
        })
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF upload from the frontend"""
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        conversation_id = request.form.get('conversation_id', str(uuid.uuid4()))
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            # Process the PDF (basic metadata)
            doc_id = pdf_processor.process_pdf(filepath, conversation_id)
            # Process the PDF for RAG and get context
            base_name, folder_path = pdf_processor.process_pdf_for_rag(filepath)
            rag_context = {"folder_path": folder_path, "base_name": base_name}
            # Add file context to the conversation memory
            memory.add_file_context(conversation_id, doc_id, filename)
            # Add document metadata and RAG context
            doc_metadata = pdf_processor.processed_pdfs[doc_id]["metadata"] if doc_id in pdf_processor.processed_pdfs else {}
            memory.add_document(doc_id, doc_metadata, rag_context=rag_context)
            return jsonify({
                'message': f'PDF "{filename}" uploaded and processed successfully',
                'doc_id': doc_id,
                'conversation_id': conversation_id,
                'rag_context': rag_context
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """Handle CSV file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be a CSV'}), 400
        
        # Create a unique ID for the document
        doc_id = str(uuid.uuid4())
        
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        logger.info(f"CSV file saved at: {file_path}")
        
        # Process the CSV file
        result = csv_processor.process_csv(file_path, doc_id)
        logger.info(f"CSV processing result: {result}")
        
        if not result.get('success', False):
            return jsonify({'error': result.get('error', 'Error processing CSV file')}), 500
        
        # Add the document to the conversation memory
        conversation_id = request.form.get('conversation_id')
        if conversation_id:
            logger.info(f"Adding CSV file to conversation {conversation_id}")
            memory.add_file_context(conversation_id, doc_id, filename)
            doc_metadata = {
                'doc_id': doc_id,
                'filename': filename,
                'file_type': 'csv',
                'file_path': file_path
            }
            logger.info(f"Adding document to memory with metadata: {doc_metadata}")
            memory.add_document(doc_id, doc_metadata)
            
            # Verify the document was added correctly
            context = memory.get_context(conversation_id)
            logger.info(f"Verification - Documents in context after adding: {context.get('documents', [])}")
            
            # Double check the file path is in the document
            for doc in context.get('documents', []):
                if doc.get('doc_id') == doc_id:
                    logger.info(f"Document in memory has file_path: {doc.get('file_path')}")
        
        return jsonify({
            'message': f'CSV file "{filename}" uploaded and processed successfully',
            'doc_id': doc_id,
            'conversation_id': conversation_id,
            'file_path': file_path,
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation context"""
    try:
        data = request.json
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            return jsonify({'error': 'Conversation ID is required'}), 400
        
        # Reset the conversation in memory
        memory.reset_conversation(conversation_id)
        
        return jsonify({
            'message': 'Conversation reset successfully',
            'conversation_id': conversation_id
        })
    
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictive/anomaly', methods=['POST'])
def detect_anomalies():
    """Run anomaly detection on uploaded CSV data"""
    try:
        logger.info("/api/predictive/anomaly endpoint called")
        data = request.json
        file_path = data.get('file_path')
        window_size = data.get('window_size', 10)
        forecast_horizon = data.get('forecast_horizon', 1)
        machine_serial = data.get('machine_serial')

        if not file_path:
            return jsonify({'error': 'File path is required'}), 400

        result = run_anomaly_detection(
            file_path,
            window_size=window_size,
            forecast_horizon=forecast_horizon,
            machine_serial=machine_serial
        )
        logger.info(f"Anomaly detection result: {result}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in anomaly detection: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictive/forecast', methods=['POST'])
def forecast():
    """Run time series forecasting on uploaded CSV data"""
    try:
        data = request.json
        file_path = data.get('file_path')
        steps = data.get('steps', 30)

        if not file_path:
            return jsonify({'error': 'File path is required'}), 400

        result = run_forecasting(file_path, steps=steps)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in forecasting: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictive/synthetic', methods=['POST'])
def generate_synthetic():
    """Generate synthetic data based on uploaded CSV"""
    try:
        data = request.json
        file_path = data.get('file_path')
        task = data.get('task')
        anomaly_pct = data.get('anomaly_pct')
        series_noise = data.get('series_noise', 0.1)

        if not file_path:
            return jsonify({'error': 'File path is required'}), 400
        if not task:
            return jsonify({'error': 'Task type is required'}), 400

        result = generate_synthetic_data(
            file_path,
            task=task,
            anomaly_pct=anomaly_pct,
            series_noise=series_noise
        )

        return jsonify({'file_path': result})

    except Exception as e:
        logger.error(f"Error generating synthetic data: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)