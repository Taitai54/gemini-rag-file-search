from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import time
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'json', 'md', 'py', 'js', 'html', 'css', 'xml', 'csv'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Gemini client
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

# Store conversation history and file search store
conversation_history = []
file_search_store = None
uploaded_files = []  # Track uploaded files with metadata and document IDs
MAX_HISTORY = 7
PERSISTENCE_FILE = 'store_state.json'

# Load persisted state on startup
def load_state():
    global file_search_store, uploaded_files
    try:
        if os.path.exists(PERSISTENCE_FILE):
            with open(PERSISTENCE_FILE, 'r') as f:
                state = json.load(f)
                store_name = state.get('store_name')
                uploaded_files = state.get('uploaded_files', [])

                if store_name:
                    # Verify the store still exists
                    try:
                        file_search_store = client.file_search_stores.get(name=store_name)
                        logger.info(f"Restored file search store: {store_name} with {len(uploaded_files)} files")
                    except Exception as e:
                        logger.warning(f"Stored file search store not found: {e}")
                        file_search_store = None
                        uploaded_files = []
    except Exception as e:
        logger.error(f"Error loading state: {e}")

# Save state to file
def save_state():
    try:
        state = {
            'store_name': file_search_store.name if file_search_store else None,
            'uploaded_files': uploaded_files
        }
        with open(PERSISTENCE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info("State saved successfully")
    except Exception as e:
        logger.error(f"Error saving state: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global file_search_store, uploaded_files

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400

    filepath = None
    uploaded_api_file = None

    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get file size
        file_size = os.path.getsize(filepath)
        logger.info(f"File saved: {filename}, size: {file_size} bytes")

        # Get custom metadata and chunking config from request
        metadata_json = request.form.get('metadata', '{}')
        chunking_json = request.form.get('chunking_config', '{}')
        custom_metadata = json.loads(metadata_json)
        chunking_config = json.loads(chunking_json)

        # Create or reuse file search store
        if file_search_store is None:
            logger.info("Creating new file search store")
            file_search_store = client.file_search_stores.create(
                config={'display_name': 'RAG-App-Store'}
            )

        # STEP 1: Upload file using Files API (per docs)
        logger.info(f"Uploading {filename} to Files API")
        uploaded_api_file = client.files.upload(
            file=filepath,
            config={'display_name': filename}
        )

        # STEP 2: Import file into file search store with metadata (per docs)
        logger.info(f"Importing {filename} into file search store")

        import_config = {}

        # Add custom metadata if provided
        if custom_metadata:
            metadata_list = []
            for key, value in custom_metadata.items():
                if isinstance(value, (int, float)):
                    metadata_list.append({"key": key, "numeric_value": value})
                else:
                    metadata_list.append({"key": key, "string_value": str(value)})
            import_config['custom_metadata'] = metadata_list

        # Add chunking config if provided
        if chunking_config and chunking_config.get('enabled'):
            import_config['chunking_config'] = {
                'white_space_config': {
                    'max_tokens_per_chunk': chunking_config.get('max_tokens_per_chunk', 200),
                    'max_overlap_tokens': chunking_config.get('max_overlap_tokens', 20)
                }
            }

        operation = client.file_search_stores.import_file(
            file_search_store_name=file_search_store.name,
            file_name=uploaded_api_file.name,
            config=import_config if import_config else None
        )

        # Wait for operation to complete
        logger.info("Waiting for file import to complete")
        max_wait = 120  # Increased to 2 minutes
        wait_time = 0
        while not operation.done and wait_time < max_wait:
            time.sleep(3)
            operation = client.operations.get(operation)
            wait_time += 3
            if wait_time % 15 == 0:  # Log progress every 15 seconds
                logger.info(f"Still waiting... ({wait_time}s elapsed)")

        if not operation.done:
            logger.error(f"File processing timeout after {max_wait}s")
            return jsonify({'error': f'File processing timeout after {max_wait} seconds. The file may still be processing in the background.'}), 500

        # Extract document ID from operation response
        document_id = None
        if hasattr(operation, 'response') and operation.response:
            # The response contains the document information
            document_id = getattr(operation.response, 'name', None)

        # Track uploaded file
        file_info = {
            'filename': filename,
            'size': file_size,
            'uploaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'custom_metadata': custom_metadata,
            'chunking_config': chunking_config if chunking_config.get('enabled') else None,
            'file_api_name': uploaded_api_file.name,
            'document_id': document_id
        }
        uploaded_files.append(file_info)

        # Save state to persistence
        save_state()

        # Clean up local file
        os.remove(filepath)
        logger.info(f"File {filename} successfully uploaded and imported")

        return jsonify({
            'success': True,
            'message': f'File "{filename}" uploaded and processed successfully',
            'filename': filename,
            'file_size': file_size,
            'store_name': file_search_store.name,
            'document_id': document_id,
            'uploaded_files': uploaded_files
        })

    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        # Clean up file if it exists
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        # Clean up API file if uploaded
        if uploaded_api_file:
            try:
                client.files.delete(uploaded_api_file.name)
            except:
                pass
        return jsonify({'error': f'Error uploading file: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history

    data = request.json
    user_message = data.get('message', '')
    metadata_filter = data.get('metadata_filter', '')
    system_prompt = data.get('system_prompt', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    if file_search_store is None:
        return jsonify({'error': 'Please upload a file first'}), 400

    try:
        # Add user message to history
        conversation_history.append({
            'role': 'user',
            'content': user_message
        })

        # Build conversation context (last MAX_HISTORY messages)
        context_messages = conversation_history[-MAX_HISTORY:]

        # Create prompt with conversation history
        prompt_parts = []

        # Add system prompt at the beginning if provided
        if system_prompt:
            prompt_parts.append(f"System Instructions: {system_prompt}\n")

        for msg in context_messages[:-1]:  # All except current message
            if msg['role'] == 'user':
                prompt_parts.append(f"User: {msg['content']}")
            else:
                prompt_parts.append(f"Assistant: {msg['content']}")

        # Add current question
        prompt_parts.append(f"User: {user_message}")
        prompt_parts.append("Assistant:")

        full_prompt = "\n\n".join(prompt_parts)

        logger.info(f"Querying with message: {user_message}")
        if metadata_filter:
            logger.info(f"Using metadata filter: {metadata_filter}")

        # Build file search config
        file_search_config = types.FileSearch(
            file_search_store_names=[file_search_store.name]
        )

        # Add metadata filter if provided
        if metadata_filter:
            file_search_config.metadata_filter = metadata_filter

        # Query with File Search
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(file_search=file_search_config)]
            )
        )

        assistant_message = response.text

        # Add assistant response to history
        conversation_history.append({
            'role': 'assistant',
            'content': assistant_message
        })

        # Keep only last MAX_HISTORY messages
        if len(conversation_history) > MAX_HISTORY:
            conversation_history = conversation_history[-MAX_HISTORY:]

        # Extract grounding metadata (citations)
        metadata = None
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                grounding = candidate.grounding_metadata

                # Extract citation information
                citations = []
                if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                    for chunk in grounding.grounding_chunks:
                        if hasattr(chunk, 'retrieved_context'):
                            ctx = chunk.retrieved_context
                            citation = {}
                            if hasattr(ctx, 'title'):
                                citation['title'] = ctx.title
                            if hasattr(ctx, 'uri'):
                                citation['uri'] = ctx.uri
                            if hasattr(ctx, 'text'):
                                citation['text'] = ctx.text
                            citations.append(citation)

                metadata = {
                    'citations': citations,
                    'citation_count': len(citations)
                }

        logger.info(f"Response generated successfully with {len(metadata['citations']) if metadata else 0} citations")

        return jsonify({
            'success': True,
            'response': assistant_message,
            'metadata': metadata,
            'conversation_length': len(conversation_history),
            'metadata_filter_used': metadata_filter if metadata_filter else None
        })

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500

@app.route('/delete-file/<int:file_index>', methods=['DELETE'])
def delete_file(file_index):
    global uploaded_files

    try:
        if file_index < 0 or file_index >= len(uploaded_files):
            return jsonify({'error': 'Invalid file index'}), 400

        file_info = uploaded_files[file_index]

        # Delete from Files API
        if file_info.get('file_api_name'):
            try:
                client.files.delete(file_info['file_api_name'])
                logger.info(f"Deleted file from Files API: {file_info['file_api_name']}")
            except Exception as e:
                logger.warning(f"Could not delete from Files API: {str(e)}")

        # Remove from tracking
        deleted_file = uploaded_files.pop(file_index)
        logger.info(f"Removed file from tracking: {deleted_file['filename']}")

        # Save state to persistence
        save_state()

        return jsonify({
            'success': True,
            'message': f"File '{deleted_file['filename']}' deleted successfully",
            'uploaded_files': uploaded_files
        })

    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({'error': f'Error deleting file: {str(e)}'}), 500

@app.route('/store-info', methods=['GET'])
def get_store_info():
    try:
        if file_search_store is None:
            return jsonify({
                'success': True,
                'store_exists': False,
                'message': 'No file search store created yet'
            })

        # Get store details
        store_details = client.file_search_stores.get(name=file_search_store.name)

        store_info = {
            'success': True,
            'store_exists': True,
            'name': store_details.name,
            'display_name': getattr(store_details, 'display_name', 'N/A'),
            'create_time': getattr(store_details, 'create_time', 'N/A'),
            'update_time': getattr(store_details, 'update_time', 'N/A'),
            'document_count': len(uploaded_files)
        }

        return jsonify(store_info)

    except Exception as e:
        logger.error(f"Error getting store info: {str(e)}")
        return jsonify({'error': f'Error getting store info: {str(e)}'}), 500

@app.route('/stores', methods=['GET'])
def list_stores():
    try:
        stores = []
        for store in client.file_search_stores.list():
            stores.append({
                'name': store.name,
                'display_name': getattr(store, 'display_name', 'N/A'),
                'create_time': str(getattr(store, 'create_time', 'N/A'))
            })

        return jsonify({
            'success': True,
            'stores': stores,
            'count': len(stores)
        })

    except Exception as e:
        logger.error(f"Error listing stores: {str(e)}")
        return jsonify({'error': f'Error listing stores: {str(e)}'}), 500

@app.route('/delete-store', methods=['DELETE'])
def delete_store():
    global file_search_store, uploaded_files

    try:
        if file_search_store is None:
            return jsonify({'error': 'No store to delete'}), 400

        store_name = file_search_store.name

        # Delete the store with force=True
        client.file_search_stores.delete(name=store_name, config={'force': True})
        logger.info(f"Deleted file search store: {store_name}")

        # Reset state
        file_search_store = None
        uploaded_files = []

        # Save state to persistence
        save_state()

        return jsonify({
            'success': True,
            'message': 'File search store deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting store: {str(e)}")
        return jsonify({'error': f'Error deleting store: {str(e)}'}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    global conversation_history
    conversation_history = []
    logger.info("Conversation history cleared")
    return jsonify({'success': True, 'message': 'Conversation cleared'})

@app.route('/files', methods=['GET'])
def get_files():
    return jsonify({
        'success': True,
        'files': uploaded_files,
        'store_name': file_search_store.name if file_search_store else None
    })

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'file_uploaded': file_search_store is not None,
        'conversation_length': len(conversation_history),
        'store_name': file_search_store.name if file_search_store else None,
        'uploaded_files': uploaded_files
    })

@app.route('/api-info', methods=['GET'])
def get_api_info():
    """Return API information for documentation tab"""
    try:
        api_info = {
            'success': True,
            'api_key': api_key,
            'store_exists': file_search_store is not None,
            'store_name': file_search_store.name if file_search_store else None,
            'store_display_name': getattr(file_search_store, 'display_name', 'RAG-App-Store') if file_search_store else 'RAG-App-Store',
            'file_count': len(uploaded_files),
            'files': uploaded_files,
            'model': 'gemini-2.5-flash',
            'example_metadata_filters': []
        }

        # Collect example metadata keys from uploaded files
        metadata_keys = set()
        for file_info in uploaded_files:
            if file_info.get('custom_metadata'):
                for key in file_info['custom_metadata'].keys():
                    metadata_keys.add(key)

        api_info['metadata_keys'] = list(metadata_keys)

        return jsonify(api_info)

    except Exception as e:
        logger.error(f"Error getting API info: {str(e)}")
        return jsonify({'error': f'Error getting API info: {str(e)}'}), 500

@app.route('/update-api-key', methods=['POST'])
def update_api_key():
    """Update API key in .env file and reinitialize client"""
    global api_key, client
    try:
        data = request.json
        new_api_key = data.get('api_key', '').strip()

        if not new_api_key:
            return jsonify({'error': 'API key cannot be empty'}), 400

        # Update .env file
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()

            with open(env_path, 'w') as f:
                found = False
                for line in lines:
                    if line.startswith('GEMINI_API_KEY='):
                        f.write(f'GEMINI_API_KEY={new_api_key}\n')
                        found = True
                    else:
                        f.write(line)

                if not found:
                    f.write(f'\nGEMINI_API_KEY={new_api_key}\n')
        else:
            with open(env_path, 'w') as f:
                f.write(f'GEMINI_API_KEY={new_api_key}\n')

        # Update runtime variable and reinitialize client
        api_key = new_api_key
        client = genai.Client(api_key=api_key)

        logger.info("API key updated successfully")
        return jsonify({'success': True, 'message': 'API key updated successfully. Please reload the page.'})

    except Exception as e:
        logger.error(f"Error updating API key: {str(e)}")
        return jsonify({'error': f'Error updating API key: {str(e)}'}), 500

if __name__ == '__main__':
    # Load persisted state on startup
    load_state()
    app.run(debug=True, host='localhost', port=5001)
