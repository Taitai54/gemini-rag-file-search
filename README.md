# Gemini RAG File Search Application

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![Gemini API](https://img.shields.io/badge/Gemini-2.5--flash-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**A modern, full-featured web application for chatting with your documents using Google's Gemini AI**

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Screenshots](#screenshots) • [Contributing](#contributing)

</div>

---

## Overview

The Gemini RAG File Search Application is a powerful, user-friendly tool that enables you to upload documents and interact with them through natural language conversations. Built on Google's cutting-edge Gemini API with File Search capabilities, this application provides enterprise-grade Retrieval Augmented Generation (RAG) functionality with a clean, modern interface.

### What Makes This Special?

- **Fully Managed RAG**: No need to manage vector databases, embeddings, or chunking strategies - Gemini handles it all
- **Rich Metadata Support**: Tag documents with custom metadata and filter searches accordingly
- **Configurable Chunking**: Fine-tune how documents are split for optimal retrieval
- **Built-in Citations**: Every AI response includes source citations for verification
- **System Prompts**: Customize AI behavior with custom instructions
- **Beautiful UI**: Clean, professional design with drag-and-drop functionality
- **Cost Effective**: Free storage, pay only for initial indexing ($0.15 per 1M tokens)

---

## Features

### Core Functionality

#### 📤 **Smart Document Upload**
- **Drag & Drop Interface**: Intuitive file upload with visual feedback
- **Wide Format Support**: PDF, DOCX, TXT, JSON, MD, Python, JavaScript, HTML, CSS, XML, CSV, and more
- **Large File Handling**: Support for files up to 100MB
- **Real-time Processing**: Visual feedback during upload and indexing
- **Secure Storage**: Files are temporarily stored locally and permanently indexed in the cloud

#### 💬 **Intelligent Chat Interface**
- **Context-Aware Conversations**: Maintains conversation history (last 7 messages) for coherent dialogues
- **Semantic Search**: Powered by Gemini's state-of-the-art embedding model
- **Instant Responses**: Fast query processing with efficient retrieval
- **Suggested Prompts**: Smart prompt suggestions when files are uploaded
- **Clear Chat History**: Easy conversation reset without losing uploaded files

#### 📎 **Citation & Source Tracking**
- **Automatic Citations**: Every response includes references to source documents
- **Expandable Citation Views**: Click to view detailed source excerpts
- **Source Verification**: See exactly which document sections were used
- **Multiple Sources**: Responses can pull from multiple document sections

#### 🏷️ **Advanced Metadata Management**
- **Custom Tags**: Add key-value metadata to each document
- **Flexible Filtering**: Query specific documents using metadata filters
- **Numeric & String Values**: Support for both text and numeric metadata
- **Complex Queries**: Use AND/OR logic for sophisticated filtering
  - Example: `author="John Doe" AND year>2020`
  - Example: `category="research" OR category="analysis"`

#### ⚙️ **Configurable Chunking**
- **Custom Chunk Sizes**: Set maximum tokens per chunk (10-1000)
- **Overlap Control**: Configure chunk overlap for better context (0-100 tokens)
- **White Space Splitting**: Intelligent document segmentation
- **Per-File Configuration**: Different chunking strategies for different documents

#### 🎭 **System Prompt Customization**
- **Behavioral Control**: Guide AI responses with custom instructions
- **Toggle On/Off**: Enable system prompts only when needed
- **Visual Feedback**: Active indicator when system prompt is in use
- **Examples**:
  - "Be concise and technical"
  - "Explain like I'm 5"
  - "Focus on financial implications"
  - "Provide step-by-step instructions"

#### 📁 **File Management**
- **Multi-File Support**: Upload and manage multiple documents
- **File Details**: View filename, size, upload timestamp
- **Individual Deletion**: Remove specific files from the store
- **Store Management**: Delete entire file search store when needed
- **Metadata Display**: See custom metadata and chunking config for each file

### User Interface

#### Design Philosophy
- **Clean & Modern**: Minimalist design with focus on functionality
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Intuitive Navigation**: Logical organization of features
- **Visual Feedback**: Loading states, success/error messages, animations
- **Accessibility**: Keyboard navigation, clear labels, high contrast

#### Color System
- **Primary Teal**: `#0F766E` - Main brand color for CTAs and accents
- **Success Green**: `#10B981` - Positive feedback and confirmations
- **Error Red**: `#DC2626` - Error messages and destructive actions
- **Warning Amber**: `#F59E0B` - Advanced settings and cautions
- **Info Blue**: `#2563EB` - Information and metadata
- **Neutral Grays**: Clean backgrounds and text

---

## Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.13+** ([Download Python](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Google Gemini API Key** ([Get API Key](https://aistudio.google.com/app/apikey))
- **Git** (optional, for cloning) ([Download Git](https://git-scm.com/downloads))

### Installation Steps

#### 1. Clone or Download the Repository

**Option A: Using Git**
```bash
git clone https://github.com/yourusername/gemini-rag-app.git
cd gemini-rag-app
```

**Option B: Download ZIP**
- Download the repository as a ZIP file
- Extract to your desired location
- Navigate to the folder in terminal/command prompt

#### 2. Set Up Python Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt indicating the virtual environment is active.

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask 3.0.0 (web framework)
- Flask-CORS 4.0.0 (CORS handling)
- google-genai 0.2.2 (Gemini API client)
- python-dotenv 1.0.0 (environment variables)
- werkzeug 3.0.1 (secure file handling)

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# On macOS/Linux
cp .env.example .env

# On Windows
copy .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

**How to get a Gemini API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key"
4. Copy the key and paste it into your `.env` file

#### 5. Run the Application

```bash
python app.py
```

You should see output like:
```
 * Running on http://localhost:5001
 * Debug mode: on
```

#### 6. Access the Application

Open your web browser and navigate to:
```
http://localhost:5001
```

### First-Time Usage

1. **Upload Your First Document**:
   - Drag and drop a PDF, DOCX, or TXT file onto the upload zone
   - Or click the upload zone to browse for a file
   - Wait for the success message (usually 5-15 seconds)

2. **Start Chatting**:
   - Try a suggested prompt like "What is this document about?"
   - Or type your own question in the chat input
   - Press Enter or click "Send"

3. **Explore Features**:
   - Click on citation counts to see sources
   - Add metadata to documents for better organization
   - Try metadata filters to search specific documents
   - Enable system prompts to customize AI behavior

---

## Documentation

### Project Structure

```
gemini-rag-app/
├── app.py                      # Flask backend application
├── templates/
│   └── index.html             # Frontend SPA (HTML, CSS, JS)
├── uploads/                   # Temporary file storage (auto-created)
├── .env                       # Environment variables (not in repo)
├── .env.example              # Environment template
├── .gitignore                # Git exclusions
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── MEGA_PROMPT.md           # Complete rebuild instructions
└── CLAUDE.md                # Development guidelines
```

### Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────────┐
│   Browser   │◄────►│   Flask     │◄────►│  Gemini API     │
│  (Frontend) │      │  (Backend)  │      │  (File Search)  │
└─────────────┘      └─────────────┘      └─────────────────┘
      │                    │                      │
      │                    │                      │
   HTML/CSS/JS        REST APIs            RAG Processing
   User Interface     JSON Data           Vector Search
```

### API Endpoints

#### File Operations

**Upload File**
```http
POST /upload
Content-Type: multipart/form-data

Parameters:
- file: File (required)
- metadata: JSON string (optional)
- chunking_config: JSON string (optional)

Response:
{
  "success": true,
  "message": "File uploaded successfully",
  "filename": "document.pdf",
  "uploaded_files": [...]
}
```

**Delete File**
```http
DELETE /delete-file/<file_index>

Response:
{
  "success": true,
  "message": "File deleted",
  "uploaded_files": [...]
}
```

**List Files**
```http
GET /files

Response:
{
  "success": true,
  "files": [...],
  "store_name": "store_id"
}
```

#### Chat Operations

**Send Chat Message**
```http
POST /chat
Content-Type: application/json

Body:
{
  "message": "What are the main points?",
  "metadata_filter": "author=\"John\"",  // optional
  "system_prompt": "Be concise"           // optional
}

Response:
{
  "success": true,
  "response": "The main points are...",
  "metadata": {
    "citations": [...],
    "citation_count": 3
  },
  "conversation_length": 4
}
```

**Clear Conversation**
```http
POST /clear

Response:
{
  "success": true,
  "message": "Conversation cleared"
}
```

#### Store Operations

**Get Store Info**
```http
GET /store-info

Response:
{
  "success": true,
  "store_exists": true,
  "name": "store_id",
  "display_name": "RAG-App-Store",
  "document_count": 5
}
```

**Delete Store**
```http
DELETE /delete-store

Response:
{
  "success": true,
  "message": "Store deleted"
}
```

**List All Stores**
```http
GET /stores

Response:
{
  "success": true,
  "stores": [...],
  "count": 2
}
```

**Status Check**
```http
GET /status

Response:
{
  "file_uploaded": true,
  "conversation_length": 4,
  "store_name": "store_id",
  "uploaded_files": [...]
}
```

### Configuration Options

#### Environment Variables (.env)

```env
# Required
GEMINI_API_KEY=your_api_key_here

# Optional (defaults shown)
FLASK_ENV=development
FLASK_DEBUG=True
MAX_CONTENT_LENGTH=104857600  # 100MB in bytes
UPLOAD_FOLDER=uploads
```

#### Application Settings (app.py)

```python
# File Upload
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'json', 'md', 'py', 'js', 'html', 'css', 'xml', 'csv'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Conversation
MAX_HISTORY = 7  # Number of messages to keep in context

# Timeouts
UPLOAD_TIMEOUT = 60  # seconds
```

### Advanced Usage

#### Custom Metadata Examples

**Organize by Author and Date**:
```javascript
{
  "author": "Jane Smith",
  "date": "2024-01-15",
  "category": "research"
}
```

**Track Versions**:
```javascript
{
  "version": 2,
  "status": "final",
  "department": "Engineering"
}
```

**Numeric Filtering**:
```javascript
{
  "year": 2024,
  "priority": 1,
  "pages": 45
}
```

#### Metadata Filter Syntax

**String Equality**:
```
author="John Doe"
category="research"
```

**Numeric Comparison**:
```
year>2020
priority<=2
pages>=10
```

**Boolean Logic**:
```
author="John" AND year>2020
category="research" OR category="analysis"
(author="John" OR author="Jane") AND year>2023
```

#### Chunking Configuration Examples

**Technical Documents** (detailed context):
```javascript
{
  "enabled": true,
  "max_tokens_per_chunk": 500,
  "max_overlap_tokens": 50
}
```

**Short Articles** (smaller chunks):
```javascript
{
  "enabled": true,
  "max_tokens_per_chunk": 200,
  "max_overlap_tokens": 20
}
```

**Code Files** (minimal overlap):
```javascript
{
  "enabled": true,
  "max_tokens_per_chunk": 300,
  "max_overlap_tokens": 10
}
```

#### System Prompt Examples

**Technical Support**:
```
You are a technical support assistant. Provide clear, step-by-step
instructions. Use simple language and avoid jargon.
```

**Research Assistant**:
```
You are a research assistant. Provide detailed analysis with citations.
Focus on evidence-based responses and highlight key findings.
```

**Executive Summary**:
```
Provide concise, high-level summaries. Focus on key takeaways and
business implications. Use bullet points when appropriate.
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "GEMINI_API_KEY not found in environment variables"

**Solution**:
1. Ensure `.env` file exists in project root
2. Check that the file contains: `GEMINI_API_KEY=your_key_here`
3. Make sure there are no spaces around the `=` sign
4. Restart the Flask application after adding the key

#### Issue: "File processing timeout"

**Cause**: Large files or slow network connection

**Solutions**:
- Wait a bit longer (large files can take 30-60 seconds)
- Check your internet connection
- Try uploading a smaller file first
- Increase timeout in `app.py`: `max_wait = 120`

#### Issue: No citations showing in responses

**Possible Causes**:
- File not fully indexed yet
- Query too general or abstract
- Document doesn't contain relevant information

**Solutions**:
- Wait a few seconds after upload before querying
- Ask more specific questions
- Try different phrasings of your question

#### Issue: Chat input is disabled

**Cause**: No file has been uploaded yet

**Solution**:
- Upload at least one document first
- Check that upload was successful (green success message)
- Refresh the page if upload succeeded but input is still disabled

#### Issue: Metadata filter not working

**Common Mistakes**:
- Missing quotes around string values: Use `author="John"` not `author=John`
- Wrong operator for strings: Use `=` not `==`
- Typo in metadata key: Must match exactly what was uploaded

**Correct Examples**:
```
author="John Doe"
year>2020
category="research" AND priority<=2
```

#### Issue: Application won't start

**Check**:
1. Virtual environment is activated (see `(venv)` in prompt)
2. All dependencies installed: `pip install -r requirements.txt`
3. Python version 3.13 or higher: `python --version`
4. Port 5001 is not in use by another application

**Kill process on port 5001** (if needed):
```bash
# On macOS/Linux
lsof -ti:5001 | xargs kill

# On Windows
netstat -ano | findstr :5001
taskkill /PID <PID> /F
```

---

## Performance & Limitations

### Rate Limits

**Gemini API**:
- Free tier: 15 requests per minute
- Paid tier: Higher limits based on subscription
- Monitor usage in [Google AI Studio](https://aistudio.google.com/)

### File Limits

- **Maximum file size**: 100 MB per file
- **File search store size**:
  - Free tier: 1 GB total
  - Tier 1: 10 GB total
  - Tier 2: 100 GB total
  - Tier 3: 1 TB total
- **Recommended**: Keep each store under 20 GB for optimal performance

### Pricing

- **Embedding indexing**: $0.15 per 1 million tokens (one-time cost)
- **Storage**: Free
- **Query-time embeddings**: Free
- **Retrieved document tokens**: Charged as regular context tokens
- **Generation**: Standard Gemini pricing

**Example Cost Calculation**:
- 100-page PDF ≈ 50,000 tokens
- Indexing cost: $0.0075 (less than one cent)
- Storage: Free
- 100 queries ≈ $0.01-$0.05 depending on response length

### Best Practices

1. **Chunking**: Start with default settings (200 tokens/chunk, 20 overlap)
2. **Metadata**: Add relevant metadata to all uploads for better organization
3. **Queries**: Be specific in your questions for better responses
4. **Files**: Group related documents in separate stores for faster searches
5. **History**: Clear conversation when switching topics
6. **Store Management**: Delete old stores to free up quota

---

## Security Considerations

### API Key Security

⚠️ **Never commit `.env` file to version control**

- Keep API keys in `.env` file (already in `.gitignore`)
- Use environment variables in production
- Rotate keys periodically
- Monitor API usage for anomalies

### File Upload Security

The application includes several security measures:
- Filename sanitization (prevents directory traversal)
- File type validation
- File size limits
- Temporary local storage (files deleted after processing)

**Additional Recommendations for Production**:
- Add user authentication
- Implement rate limiting
- Scan uploaded files for malware
- Use HTTPS only
- Set up CORS properly for your domain

### Data Privacy

- Files are processed by Google's Gemini API
- Review [Google's Privacy Policy](https://policies.google.com/privacy)
- Don't upload sensitive/confidential documents without proper authorization
- Consider data residency requirements for your use case

---

## Development

### Running in Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run with debug mode
python app.py

# Flask will auto-reload on code changes
```

### Running in Production

**Using Gunicorn** (recommended for production):

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**Environment Variables for Production**:
```env
FLASK_ENV=production
FLASK_DEBUG=False
```

### Testing

**Manual Testing Checklist**:
- [ ] Upload file (PDF, DOCX, TXT)
- [ ] Upload file with metadata
- [ ] Upload file with custom chunking
- [ ] Send chat message
- [ ] View citations
- [ ] Apply metadata filter
- [ ] Enable system prompt
- [ ] Delete individual file
- [ ] Delete entire store
- [ ] Clear conversation
- [ ] Test with multiple files
- [ ] Test drag-and-drop
- [ ] Test responsive design

**API Testing with curl**:

```bash
# Upload file
curl -X POST http://localhost:5001/upload \
  -F "file=@test.pdf" \
  -F 'metadata={"author":"Test"}'

# Send chat
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Summarize the document"}'

# Check status
curl http://localhost:5001/status
```

### Code Style

- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: Use consistent indentation (2 spaces)
- **Comments**: Explain complex logic
- **Naming**: Use descriptive variable/function names

---

## Contributing

We welcome contributions! Here's how you can help:

### Reporting Bugs

1. Check if the issue already exists in [Issues](https://github.com/yourusername/gemini-rag-app/issues)
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Open an issue tagged with `enhancement`
2. Describe the feature and its benefits
3. Provide examples or mockups if possible

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages: `git commit -m "Add amazing feature"`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup for Contributors

```bash
# Clone your fork
git clone https://github.com/yourusername/gemini-rag-app.git
cd gemini-rag-app

# Add upstream remote
git remote add upstream https://github.com/original/gemini-rag-app.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
# ...

# Commit and push
git add .
git commit -m "Your change description"
git push origin feature/your-feature
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Acknowledgments

- **Google Gemini Team** for the powerful File Search API
- **Flask Community** for the excellent web framework
- **Contributors** who have helped improve this project

---

## Support

### Get Help

- **Documentation**: Read this README and [MEGA_PROMPT.md](MEGA_PROMPT.md)
- **Issues**: Check [existing issues](https://github.com/yourusername/gemini-rag-app/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/yourusername/gemini-rag-app/discussions)
- **Email**: support@yourproject.com (if applicable)

### Stay Updated

- ⭐ Star this repository to show support
- 👁️ Watch for updates and new features
- 🔔 Subscribe to release notifications

---

## Roadmap

### Current Features ✅
- [x] File upload with drag & drop
- [x] Multi-format document support
- [x] AI-powered chat with citations
- [x] Custom metadata and filtering
- [x] Configurable chunking
- [x] System prompts
- [x] File management
- [x] Responsive UI

### Planned Features 🚀

**Version 2.0**
- [ ] User authentication and multi-user support
- [ ] Document folders and organization
- [ ] Batch file upload
- [ ] Export conversation history
- [ ] Dark mode
- [ ] Mobile app (iOS/Android)

**Version 2.1**
- [ ] Document comparison mode
- [ ] Advanced analytics dashboard
- [ ] Cost tracking and budgets
- [ ] Collaborative annotations
- [ ] Email document upload
- [ ] Scheduled queries

**Version 3.0**
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Integration with Google Drive, Dropbox
- [ ] Custom AI model fine-tuning
- [ ] API for third-party integrations
- [ ] Enterprise features (SSO, audit logs)

---

## FAQ

**Q: Can I use this for commercial purposes?**
A: Yes, under the MIT license. However, review Google's Gemini API terms of service.

**Q: How much does it cost to run?**
A: Very affordable! Indexing costs $0.15 per 1M tokens. A 100-page document costs less than a penny to index. Storage is free.

**Q: Can I deploy this on a server?**
A: Yes! Use a production WSGI server like Gunicorn and deploy on platforms like Google Cloud, AWS, Heroku, or DigitalOcean.

**Q: Does this work offline?**
A: No, it requires internet connection to communicate with Gemini API.

**Q: Can I customize the UI?**
A: Absolutely! All styles are in `index.html` and can be modified. The color system is well-documented.

**Q: Is my data private?**
A: Files are processed by Google's Gemini API. Review Google's privacy policy and don't upload sensitive data without authorization.

**Q: Can I use different AI models?**
A: Currently supports `gemini-2.5-flash` and `gemini-2.5-pro`. Change the model in `app.py`.

**Q: What file formats are supported?**
A: PDF, DOCX, TXT, JSON, MD, PY, JS, HTML, CSS, XML, CSV, and more. See Gemini docs for full list.

**Q: How many files can I upload?**
A: Limited by your Gemini API tier (1GB free, up to 1TB on higher tiers).

**Q: Can I search multiple documents at once?**
A: Yes! Upload multiple files to the same store and queries search across all of them.

---

<div align="center">

**Built with ❤️ using Google Gemini AI**

[⬆ Back to Top](#gemini-rag-file-search-application)

</div>
