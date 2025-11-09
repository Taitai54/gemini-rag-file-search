# MEGA PROMPT: Gemini RAG File Search Application

## Project Overview
Create a full-stack web application that enables users to upload documents and interact with them through an AI-powered chat interface using Google's Gemini API File Search feature. The application implements a Retrieval Augmented Generation (RAG) system with a modern, clean UI and comprehensive document management capabilities.

## Core Technologies
- **Backend Framework**: Flask (Python 3.13+)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **AI/ML**: Google Gemini API (gemini-2.5-flash model)
- **File Handling**: Werkzeug secure file uploads
- **Environment Management**: python-dotenv
- **CORS**: Flask-CORS for API access

## Dependencies (requirements.txt)
```
flask==3.0.0
flask-cors==4.0.0
google-genai==0.2.2
python-dotenv==1.0.0
werkzeug==3.0.1
```

## Architecture & File Structure

```
gemini-rag/
├── app.py                    # Flask backend application
├── templates/
│   └── index.html           # Single-page frontend application
├── modern-style.css         # Standalone stylesheet (optional)
├── uploads/                 # Temporary file storage
├── .env                     # Environment variables (API key)
├── .gitignore              # Git exclusions
├── requirements.txt        # Python dependencies
└── README.md              # Documentation
```

## Backend Implementation (app.py)

### Configuration & Setup
```python
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

# Configuration constants
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'json', 'md', 'py', 'js', 'html', 'css', 'xml', 'csv'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_HISTORY = 7  # Conversation history limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Gemini client
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

# Global state management
conversation_history = []
file_search_store = None
uploaded_files = []  # Track uploaded files with metadata
```

### Core Features & API Endpoints

#### 1. File Upload with Advanced Features
**Endpoint**: `POST /upload`

**Features**:
- Secure file upload with validation
- Two-step Gemini API process: Upload → Import
- Custom metadata support (key-value pairs)
- Configurable chunking parameters
- Automatic file search store creation
- Operation polling with timeout handling

**Implementation**:
```python
@app.route('/upload', methods=['POST'])
def upload_file():
    global file_search_store, uploaded_files

    # Validate file presence and type
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    # Save file temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Parse metadata and chunking config from request
    metadata_json = request.form.get('metadata', '{}')
    chunking_json = request.form.get('chunking_config', '{}')
    custom_metadata = json.loads(metadata_json)
    chunking_config = json.loads(chunking_json)

    # Create file search store if needed
    if file_search_store is None:
        file_search_store = client.file_search_stores.create(
            config={'display_name': 'RAG-App-Store'}
        )

    # STEP 1: Upload to Files API
    uploaded_api_file = client.files.upload(
        file=filepath,
        config={'display_name': filename}
    )

    # STEP 2: Import into file search store with config
    import_config = {}

    # Add custom metadata
    if custom_metadata:
        metadata_list = []
        for key, value in custom_metadata.items():
            if isinstance(value, (int, float)):
                metadata_list.append({"key": key, "numeric_value": value})
            else:
                metadata_list.append({"key": key, "string_value": str(value)})
        import_config['custom_metadata'] = metadata_list

    # Add chunking configuration
    if chunking_config.get('enabled'):
        import_config['chunking_config'] = {
            'white_space_config': {
                'max_tokens_per_chunk': chunking_config.get('max_tokens_per_chunk', 200),
                'max_overlap_tokens': chunking_config.get('max_overlap_tokens', 20)
            }
        }

    # Import and wait for completion
    operation = client.file_search_stores.import_file(
        file_search_store_name=file_search_store.name,
        file_name=uploaded_api_file.name,
        config=import_config if import_config else None
    )

    # Poll operation status
    max_wait = 60
    wait_time = 0
    while not operation.done and wait_time < max_wait:
        time.sleep(2)
        operation = client.operations.get(operation)
        wait_time += 2

    if not operation.done:
        return jsonify({'error': 'File processing timeout'}), 500

    # Track uploaded file
    file_info = {
        'filename': filename,
        'size': os.path.getsize(filepath),
        'uploaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'custom_metadata': custom_metadata,
        'chunking_config': chunking_config if chunking_config.get('enabled') else None,
        'file_api_name': uploaded_api_file.name,
        'document_id': getattr(operation.response, 'name', None)
    }
    uploaded_files.append(file_info)

    # Clean up local file
    os.remove(filepath)

    return jsonify({
        'success': True,
        'message': f'File "{filename}" uploaded successfully',
        'uploaded_files': uploaded_files
    })
```

#### 2. Chat with RAG & Citations
**Endpoint**: `POST /chat`

**Features**:
- Conversational AI with context awareness
- Metadata filtering for targeted search
- System prompt customization
- Automatic citation extraction
- Rolling conversation history (last 7 messages)

**Implementation**:
```python
@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history

    data = request.json
    user_message = data.get('message', '')
    metadata_filter = data.get('metadata_filter', '')
    system_prompt = data.get('system_prompt', '')

    if not user_message or file_search_store is None:
        return jsonify({'error': 'Invalid request'}), 400

    # Add user message to history
    conversation_history.append({'role': 'user', 'content': user_message})

    # Build conversation context
    context_messages = conversation_history[-MAX_HISTORY:]
    prompt_parts = []

    # Add system prompt if provided
    if system_prompt:
        prompt_parts.append(f"System Instructions: {system_prompt}\n")

    # Add conversation history
    for msg in context_messages[:-1]:
        if msg['role'] == 'user':
            prompt_parts.append(f"User: {msg['content']}")
        else:
            prompt_parts.append(f"Assistant: {msg['content']}")

    # Add current question
    prompt_parts.append(f"User: {user_message}")
    prompt_parts.append("Assistant:")

    full_prompt = "\n\n".join(prompt_parts)

    # Build file search config
    file_search_config = types.FileSearch(
        file_search_store_names=[file_search_store.name]
    )

    # Add metadata filter if provided
    if metadata_filter:
        file_search_config.metadata_filter = metadata_filter

    # Generate response with File Search
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(file_search=file_search_config)]
        )
    )

    assistant_message = response.text

    # Add to history and maintain size limit
    conversation_history.append({'role': 'assistant', 'content': assistant_message})
    if len(conversation_history) > MAX_HISTORY:
        conversation_history = conversation_history[-MAX_HISTORY:]

    # Extract grounding metadata (citations)
    metadata = None
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            grounding = candidate.grounding_metadata
            citations = []
            if hasattr(grounding, 'grounding_chunks'):
                for chunk in grounding.grounding_chunks:
                    if hasattr(chunk, 'retrieved_context'):
                        ctx = chunk.retrieved_context
                        citation = {
                            'title': getattr(ctx, 'title', None),
                            'uri': getattr(ctx, 'uri', None),
                            'text': getattr(ctx, 'text', None)
                        }
                        citations.append(citation)
            metadata = {
                'citations': citations,
                'citation_count': len(citations)
            }

    return jsonify({
        'success': True,
        'response': assistant_message,
        'metadata': metadata,
        'conversation_length': len(conversation_history)
    })
```

#### 3. Additional Endpoints

**File Management**:
- `DELETE /delete-file/<int:file_index>` - Delete individual files
- `DELETE /delete-store` - Delete entire file search store
- `GET /files` - List all uploaded files
- `GET /store-info` - Get store details
- `GET /stores` - List all stores

**Conversation Management**:
- `POST /clear` - Clear conversation history
- `GET /status` - Application status check

**Main Route**:
- `GET /` - Serve frontend application

## Frontend Implementation (templates/index.html)

### UI Design System

**Color Palette**:
- Primary Teal: `#0F766E`, `#0D9488`, `#14B8A6`
- Neutral Grays: `#F8FAFB`, `#F1F5F9`, `#E2E8F0`, `#CBD5E1`, `#64748B`
- Success Green: `#D1FAE5`, `#065F46`, `#10B981`
- Error Red: `#DC2626`, `#B91C1C`, `#FEE2E2`
- Warning Amber: `#FEF3C7`, `#F59E0B`, `#92400E`
- Info Blue: `#DBEAFE`, `#2563EB`, `#1E40AF`
- System Purple: `#F3E8FF`, `#9333EA`, `#6B21A8`

**Layout Structure**:
```
┌─────────────────────────────────────────────────┐
│              HEADER (Title & Subtitle)          │
└─────────────────────────────────────────────────┘
┌──────────────┬──────────────────────────────────┐
│   SIDEBAR    │          CHAT AREA              │
│              │                                  │
│ Store Info   │  Metadata Filter                │
│ Upload Zone  │  Chat Messages                  │
│ Metadata     │  Suggested Prompts              │
│ Advanced     │  Chat Input                     │
│ System Prompt│                                  │
│ Files List   │                                  │
└──────────────┴──────────────────────────────────┘
```

### Key Frontend Features

#### 1. Drag & Drop File Upload
```javascript
// Drop zone interaction
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0]);
    }
});

async function handleFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(getMetadata()));
    formData.append('chunking_config', JSON.stringify(getChunkingConfig()));

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    // Handle response and update UI
}
```

#### 2. Dynamic Metadata Management
```javascript
// Add metadata fields dynamically
addMetadataBtn.addEventListener('click', () => {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'metadata-field';
    fieldDiv.innerHTML = `
        <input type="text" placeholder="Key" class="metadata-key">
        <input type="text" placeholder="Value" class="metadata-value">
        <button onclick="removeMetadataField('${fieldId}')">×</button>
    `;
    metadataFields.appendChild(fieldDiv);
});

// Collect metadata on upload
function getMetadata() {
    const metadata = {};
    const fields = metadataFields.querySelectorAll('.metadata-field');
    fields.forEach(field => {
        const key = field.querySelector('.metadata-key').value.trim();
        const value = field.querySelector('.metadata-value').value.trim();
        if (key && value) {
            const numValue = parseFloat(value);
            metadata[key] = isNaN(numValue) ? value : numValue;
        }
    });
    return metadata;
}
```

#### 3. Advanced Chunking Configuration
```javascript
function getChunkingConfig() {
    const enabled = document.getElementById('chunkingEnabled').checked;
    if (!enabled) return { enabled: false };

    return {
        enabled: true,
        max_tokens_per_chunk: parseInt(document.getElementById('maxTokensPerChunk').value),
        max_overlap_tokens: parseInt(document.getElementById('maxOverlapTokens').value)
    };
}
```

#### 4. System Prompt Feature
```javascript
// Toggle system prompt UI
window.toggleSystemPrompt = () => {
    const content = document.getElementById('systemPromptContent');
    const arrow = document.getElementById('systemPromptArrow');
    content.classList.toggle('show');
    arrow.textContent = content.classList.contains('show') ? '▲' : '▼';
};

// Include in chat request
async function sendMessage() {
    const systemPromptEnabled = document.getElementById('systemPromptEnabled').checked;
    const systemPromptText = document.getElementById('systemPromptText').value.trim();

    const payload = {
        message: chatInput.value.trim(),
        metadata_filter: metadataFilter.value.trim()
    };

    if (systemPromptEnabled && systemPromptText) {
        payload.system_prompt = systemPromptText;
    }

    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
}
```

#### 5. Chat Interface with Citations
```javascript
function addMessage(role, content, metadata = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    let metadataHTML = '';
    if (metadata && metadata.citations && metadata.citations.length > 0) {
        const metadataId = `metadata-${Date.now()}`;
        metadataHTML = `
            <div class="metadata-section">
                <div class="metadata-toggle" onclick="toggleMetadata('${metadataId}')">
                    📎 ${metadata.citation_count} source${metadata.citation_count > 1 ? 's' : ''} cited
                    <span id="${metadataId}-arrow">▼</span>
                </div>
                <div class="metadata-content" id="${metadataId}">
                    ${metadata.citations.map((citation, index) => `
                        <div class="citation">
                            <div class="citation-title">📄 ${citation.title || 'Untitled'}</div>
                            ${citation.text ? `<div class="citation-text">"${citation.text}"</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-label">${role === 'user' ? 'You' : 'Assistant'}</div>
        <div class="message-content">
            ${content}
            ${metadataHTML}
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
```

#### 6. Suggested Prompts
```javascript
function showFileReadyState(filename) {
    const suggestedPrompts = [
        "What is this document about?",
        "Summarize the main points",
        "What are the key takeaways?",
        "List the main topics covered",
        "Extract important information"
    ];

    chatMessages.innerHTML = `
        <div class="file-ready-banner">
            <strong>✅ File "${filename}" is ready!</strong>
        </div>
        <div class="suggested-prompts">
            <h3>💡 Try asking:</h3>
            <div class="prompt-bubbles">
                ${suggestedPrompts.map(prompt => `
                    <div class="prompt-bubble" onclick="useSuggestedPrompt('${prompt}')">
                        ${prompt}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

window.useSuggestedPrompt = (prompt) => {
    chatInput.value = prompt;
    chatInput.focus();
    sendMessage();
};
```

#### 7. File Management UI
```javascript
function updateFilesList(files) {
    document.getElementById('filesCount').textContent = files ? files.length : 0;

    if (!files || files.length === 0) {
        filesList.innerHTML = '<div class="empty-files-state">No files uploaded yet</div>';
        return;
    }

    filesList.innerHTML = files.map((file, index) => {
        const metadataHTML = file.custom_metadata && Object.keys(file.custom_metadata).length > 0
            ? `<div class="file-item-metadata">
                <strong>Metadata:</strong><br>
                ${Object.entries(file.custom_metadata).map(([k, v]) => `${k}: ${v}`).join('<br>')}
               </div>`
            : '';

        return `
            <div class="file-item">
                <div class="file-item-header">
                    <div class="file-item-name">📄 ${file.filename}</div>
                    <button class="btn-delete-file" onclick="deleteFile(${index})">🗑️</button>
                </div>
                <div class="file-item-details">
                    Size: ${(file.size / 1024).toFixed(2)} KB | ${file.uploaded_at}
                </div>
                ${metadataHTML}
            </div>
        `;
    }).join('');
}
```

## Environment Configuration

### .env File
```
GEMINI_API_KEY=your_api_key_here
```

### .env.example Template
```
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

## Git Configuration

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# Environment Variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Application Specific
uploads/
*.log
```

## Setup & Deployment Instructions

### Local Development Setup

1. **Clone/Create Project Directory**:
```bash
mkdir gemini-rag-app
cd gemini-rag-app
```

2. **Create Virtual Environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

5. **Create Directories**:
```bash
mkdir uploads
mkdir templates
```

6. **Run Application**:
```bash
python app.py
```

7. **Access Application**:
- Open browser to `http://localhost:5001`

### Production Deployment Considerations

1. **Security**:
   - Use HTTPS
   - Implement rate limiting
   - Add authentication if needed
   - Validate file types rigorously
   - Sanitize user inputs

2. **Performance**:
   - Use production WSGI server (Gunicorn, uWSGI)
   - Implement caching
   - Use CDN for static assets
   - Add connection pooling

3. **Monitoring**:
   - Add logging middleware
   - Implement error tracking (Sentry)
   - Monitor API usage
   - Track performance metrics

## Key Technical Details

### Gemini File Search API Flow

1. **File Upload Process**:
   ```
   Local File → Files API Upload → Import to Store → Embedding Generation → Ready for Search
   ```

2. **Chat Query Process**:
   ```
   User Query → Build Context → Apply Filters → File Search → Generate Response → Extract Citations
   ```

### Data Models

**Uploaded File Info**:
```python
{
    'filename': str,
    'size': int,  # bytes
    'uploaded_at': str,  # timestamp
    'custom_metadata': dict,  # user-defined key-value pairs
    'chunking_config': dict,  # optional chunking parameters
    'file_api_name': str,  # Gemini Files API reference
    'document_id': str  # File Search Store document ID
}
```

**Conversation Message**:
```python
{
    'role': str,  # 'user' or 'assistant'
    'content': str  # message text
}
```

**Citation Object**:
```python
{
    'title': str,  # document title
    'uri': str,  # optional document URI
    'text': str  # excerpt from document
}
```

### API Rate Limits & Pricing

**Gemini File Search**:
- Indexing: $0.15 per 1M tokens
- Storage: Free
- Query-time embeddings: Free
- Retrieved tokens: Charged as context tokens

**Limits**:
- Max file size: 100 MB
- Store size limits by tier (Free: 1GB, Tier 1: 10GB, etc.)
- Recommended: Keep stores under 20GB

## Testing & Usage Examples

### Example User Workflow

1. **Upload Document**:
   - User drags PDF file onto upload zone
   - Optionally adds metadata: `{"author": "John Doe", "year": 2024}`
   - Optionally enables chunking: `max_tokens_per_chunk: 300`
   - File is processed and embeddings created

2. **Chat with Document**:
   - User asks: "What are the main conclusions?"
   - System builds prompt with conversation history
   - Gemini searches document and generates response
   - Citations are displayed showing source sections

3. **Metadata Filtering**:
   - User enters filter: `author="John Doe" AND year>2020`
   - Only matching documents are searched
   - Response is scoped to filtered subset

4. **System Prompt**:
   - User enables system prompt: "Be concise and technical"
   - All responses follow this guidance
   - Useful for consistent tone/style

### API Testing Examples

**Upload File**:
```bash
curl -X POST http://localhost:5001/upload \
  -F "file=@document.pdf" \
  -F 'metadata={"author":"John","category":"research"}' \
  -F 'chunking_config={"enabled":true,"max_tokens_per_chunk":200}'
```

**Chat Query**:
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the key findings?",
    "metadata_filter": "category=\"research\"",
    "system_prompt": "Be concise"
  }'
```

## Customization & Extension Ideas

1. **Multi-user Support**:
   - Add user authentication
   - Separate file stores per user
   - User-specific conversation history

2. **Enhanced File Management**:
   - File versioning
   - Batch upload
   - Folder organization
   - Search within files list

3. **Advanced Features**:
   - Export conversation history
   - Save/load chat sessions
   - Document comparison mode
   - Collaborative annotations

4. **UI Enhancements**:
   - Dark mode toggle
   - Customizable themes
   - Mobile-responsive design improvements
   - Accessibility features

5. **Analytics**:
   - Usage dashboard
   - Popular queries tracking
   - Document engagement metrics
   - Cost tracking

## Troubleshooting

**Common Issues**:

1. **"GEMINI_API_KEY not found"**:
   - Ensure `.env` file exists
   - Check API key is valid
   - Restart Flask after adding key

2. **"File processing timeout"**:
   - Large files may take longer
   - Increase timeout in code
   - Check API quota

3. **No citations in response**:
   - File may not be fully indexed
   - Query may be too general
   - Check grounding metadata structure

4. **Conversation loses context**:
   - Increase MAX_HISTORY value
   - Check conversation_history array
   - Verify prompt building logic

## References & Documentation

- **Gemini API File Search**: https://ai.google.dev/gemini-api/docs/file-search
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Google GenAI Python SDK**: https://github.com/googleapis/python-genai

---

## Implementation Checklist

- [ ] Set up Python virtual environment
- [ ] Install all dependencies
- [ ] Create directory structure
- [ ] Implement Flask backend with all endpoints
- [ ] Create HTML frontend with complete UI
- [ ] Add CSS styling with design system
- [ ] Implement JavaScript functionality
- [ ] Configure environment variables
- [ ] Test file upload flow
- [ ] Test chat functionality
- [ ] Test metadata features
- [ ] Test chunking configuration
- [ ] Test system prompts
- [ ] Test file deletion
- [ ] Test store management
- [ ] Add error handling
- [ ] Add loading states
- [ ] Test responsive design
- [ ] Document API endpoints
- [ ] Create README
- [ ] Set up Git repository
- [ ] Deploy and test

---

**This mega-prompt contains everything needed to rebuild the entire Gemini RAG File Search application from scratch, including complete code implementations, UI/UX specifications, API documentation, and deployment instructions.**
