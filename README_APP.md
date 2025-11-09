# Gemini RAG File Search Application

A beautiful web application that lets you upload documents and chat with them using Google's Gemini API File Search feature.

## Features

- **Drag & Drop File Upload**: Easily upload documents by dragging and dropping
- **AI-Powered Chat**: Ask questions about your uploaded documents
- **Citation Support**: View source citations for AI responses
- **Conversation History**: Maintains context of last 5-7 messages
- **Blue-Themed UI**: Clean, modern interface with gradient design
- **Supported File Types**: PDF, TXT, DOC, DOCX, JSON, MD, Python, JavaScript, and more

## Setup

1. **Install Dependencies**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

2. **Environment Configuration**:
The `.env` file is already configured with your API key.

3. **Run the Application**:
```bash
python app.py
```

4. **Access the Application**:
Open your browser and navigate to: `http://localhost:5000`

## How to Use

1. **Upload a Document**:
   - Drag and drop a file onto the upload area, or click to browse
   - Wait for the file to be processed (you'll see a success message)

2. **Start Chatting**:
   - Type your question in the chat input
   - Press Enter or click "Send"
   - The AI will respond based on the document content

3. **View Citations**:
   - Click on the citation count below AI responses to see source references
   - Citations show which parts of your document were used

4. **Clear Conversation**:
   - Click "Clear Chat" to reset the conversation history
   - The uploaded file remains available

## Architecture

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **AI**: Google Gemini 2.5 Flash with File Search
- **File Storage**: Temporary local storage, persistent cloud embeddings

## API Endpoints

- `GET /` - Main application page
- `POST /upload` - Upload and process files
- `POST /chat` - Send chat messages
- `POST /clear` - Clear conversation history
- `GET /status` - Check application status

## Notes

- Files are automatically chunked and embedded by Gemini
- Conversation history is limited to 7 messages for optimal context
- The file search store persists across sessions
- Maximum file size: 100MB
