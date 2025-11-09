# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a documentation and reference repository for implementing Retrieval Augmented Generation (RAG) using Google's Gemini API File Search feature. The repository contains API documentation and examples for building RAG applications with the Gemini platform.

## Key Concepts

### File Search Tool
The Gemini API provides a fully managed RAG system through the File Search tool, which:
- Automatically handles file storage, chunking, embeddings, and indexing
- Uses semantic search powered by the Gemini Embedding model (gemini-embedding-001)
- Supports 100+ file formats including PDF, DOCX, TXT, JSON, and common programming languages
- Provides built-in citations in responses
- Works within the existing `generateContent` API

### Supported Models
- `gemini-2.5-pro`
- `gemini-2.5-flash`

## API Architecture

### Two Upload Approaches

1. **Direct Upload to File Search Store** (`uploadToFileSearchStore`):
   - Upload and import in one step
   - File is temporarily stored (48 hours), but embeddings persist indefinitely

2. **Separate Upload and Import**:
   - First upload via Files API (`files.upload`)
   - Then import into file search store (`import_file`)
   - Gives more control over file management

### Core Components

- **File Search Store**: Container for document embeddings, persists indefinitely
- **Chunking Configuration**: Optional `chunking_config` with `max_tokens_per_chunk` and `max_overlap_tokens`
- **Custom Metadata**: Key-value pairs for filtering documents during search
- **Grounding Metadata**: Contains citations showing which document chunks were used

## Common Code Patterns

### Basic RAG Implementation
```python
from google import genai
from google.genai import types
import time

client = genai.Client()

# Create store and upload file
store = client.file_search_stores.create(config={'display_name': 'store-name'})
operation = client.file_search_stores.upload_to_file_search_store(
    file='document.pdf',
    file_search_store_name=store.name,
    config={'display_name': 'file-name'}
)

# Wait for processing
while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

# Query with File Search
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your question here",
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name]
            )
        )]
    )
)
```

### Custom Chunking
```python
operation = client.file_search_stores.upload_to_file_search_store(
    file_search_store_name=store.name,
    file='document.pdf',
    config={
        'chunking_config': {
            'white_space_config': {
                'max_tokens_per_chunk': 200,
                'max_overlap_tokens': 20
            }
        }
    }
)
```

### Metadata Filtering
```python
# Add metadata during import
op = client.file_search_stores.import_file(
    file_search_store_name=store.name,
    file_name=file.name,
    custom_metadata=[
        {"key": "author", "string_value": "John Doe"},
        {"key": "year", "numeric_value": 2024}
    ]
)

# Filter during query
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your question",
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name],
                metadata_filter='author="John Doe"'
            )
        )]
    )
)
```

### Accessing Citations
```python
# Get grounding metadata
grounding = response.candidates[0].grounding_metadata
sources = {c.retrieved_context.title for c in grounding.grounding_chunks}
```

## Rate Limits & Pricing

### Limits
- Maximum file size: 100 MB per document
- Total file search store size (by tier):
  - Free: 1 GB
  - Tier 1: 10 GB
  - Tier 2: 100 GB
  - Tier 3: 1 TB
- Recommended: Keep each file search store under 20 GB for optimal performance

### Pricing
- Indexing embeddings: $0.15 per 1M tokens
- Storage: Free
- Query-time embeddings: Free
- Retrieved document tokens: Charged as regular context tokens

## API Authentication

The repository contains an API key in [api_key.md](api_key.md). When implementing code that uses this API:
- Initialize the client with: `client = genai.Client(api_key=YOUR_KEY)`
- Never commit API keys to version control in production environments
