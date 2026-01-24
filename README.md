# RAG Knowledge Base Assistant

A complete, runnable Retrieval-Augmented Generation (RAG) knowledge base assistant using free, local components with optional cloud LLM integration.

## Features

- **Document Support**: PDF, TXT, and Markdown files
- **Vector Search**: Uses ChromaDB for efficient semantic search
- **LLM Integration**: Hugging Face Inference API (default) or Ollama (local)
- **Web UI**: Beautiful, easy-to-use interface
- **Document Filtering**: Search specific documents or all documents
- **Citations**: Answers include source document citations
- **REST API**: Programmatic access to all features

## Architecture

- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB**: ChromaDB (persisted to `./chroma_db`)
- **LLM**: Hugging Face Inference API (default) or Ollama (optional)
- **Backend**: FastAPI
- **Frontend**: HTML/CSS/JavaScript

## Prerequisites

1. **Python 3.8+**
2. **LLM Provider** (choose one):
   - **Hugging Face API** (default, recommended)
     - Get free API key: https://huggingface.co/settings/tokens
     - No installation needed!
   - **Ollama** (for fully local use)
     - Download from: https://ollama.ai
     - Install and start Ollama service
     - Pull the model: `ollama pull llama3.1:8b`

## Installation

1. **Clone or navigate to this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure LLM Provider**:

   **Option A: Hugging Face (Default, Recommended)**
   ```bash
   # Set environment variable (optional, works without key on free tier)
   export HF_API_KEY=your_huggingface_token_here
   # Get token from: https://huggingface.co/settings/tokens
   ```

   **Option B: Ollama (Fully Local)**
   ```bash
   # Set environment variable
   export LLM_PROVIDER=ollama
   
   # Start Ollama
   ollama serve
   
   # In another terminal, verify the model is available:
   ollama list
   
   # If the model isn't installed:
   ollama pull llama3.1:8b
   ```

## Quick Start

1. **Index the sample document** (optional):
   ```bash
   python index_documents.py
   ```

2. **Start the server**:
   ```bash
   python main.py
   ```

3. **Open your browser**:
   Navigate to `http://localhost:8000`

4. **Start using it**:
   - Upload documents using the web interface
   - Ask questions about your documents
   - Use the document filter to search specific documents
   - Get answers with source citations

## Usage

### Web Interface

1. Start the server: `python main.py`
2. Open `http://localhost:8000` in your browser
3. Upload documents (PDF, TXT, or MD)
4. Use the document filter dropdown to select which documents to search (leave empty to search all)
5. Ask questions about the uploaded documents

### Document Filtering

The web interface includes a document filter dropdown:
- **Leave empty** = Search ALL indexed documents (default)
- **Select specific documents** = Search ONLY those documents
- **Multiple selection** = Hold Ctrl (Windows) or Cmd (Mac) to select multiple

### Command Line Indexing

Index all documents in the `docs/` directory:
```bash
python index_documents.py
```

### API Usage

The FastAPI server provides REST endpoints:

- **GET** `/api/stats` - Get knowledge base statistics and list of indexed documents
- **POST** `/api/ingest` - Upload and index a document
- **POST** `/api/query` - Query the knowledge base

**Query without filter (search all):**
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

**Query with document filter:**
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is RAG?",
    "source_filter": ["sample_document.txt"]
  }'
```

## Configuration

Environment variables:

**LLM Provider:**
- `LLM_PROVIDER`: `huggingface` (default) or `ollama`
- `HF_API_KEY`: Hugging Face API token (optional, recommended)
- `HF_API_URL`: Hugging Face model URL (default: Mistral-7B-Instruct)
- `OLLAMA_BASE_URL`: Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Ollama model name (default: `llama3.1:8b`)

**Server:**
- `API_HOST`: API host (default: `0.0.0.0`)
- `API_PORT`: API port (default: `8000`)

Or modify `src/config.py` directly.

## Project Structure

```
rag-kb-bot/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── ingestion.py       # Document loading and chunking
│   ├── vector_store.py    # ChromaDB integration
│   ├── llm.py            # Ollama LLM interface
│   ├── llm_huggingface.py # Hugging Face LLM interface
│   ├── rag.py            # Main RAG pipeline
│   └── api.py            # FastAPI backend
├── docs/                  # Document directory
│   └── sample_document.txt
├── chroma_db/             # ChromaDB storage (created automatically)
├── main.py               # Entry point
├── index_documents.py    # Indexing script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## How It Works

1. **Ingestion**: Documents are loaded and split into chunks
2. **Embedding**: Chunks are converted to vectors using sentence-transformers
3. **Storage**: Vectors are stored in ChromaDB
4. **Retrieval**: Questions are embedded and similar chunks are retrieved (with optional filtering)
5. **Generation**: Retrieved chunks are used as context for the LLM (Hugging Face API or Ollama)
6. **Response**: Answer is generated with source citations

## Troubleshooting

**Hugging Face API errors**:
- First request may take 20-30 seconds (model loading on free tier)
- Get a free API key: https://huggingface.co/settings/tokens
- Check if model URL is correct
- Free tier has rate limits (30 requests/hour without key, 1000 requests/month with key)

**Ollama connection error** (if using Ollama):
- Ensure Ollama is running: `ollama serve`
- Check if the model is installed: `ollama list`
- Verify the URL in config matches your Ollama instance

**Import errors**:
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.8 or higher

**Empty results**:
- Make sure documents are indexed: `python index_documents.py`
- Check that documents are in the `docs/` directory
- Verify ChromaDB collection has data (check stats endpoint)

**Port already in use**:
- Find the process: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Linux/Mac)
- Kill it: `taskkill /F /PID <PID>` (Windows) or `kill <PID>` (Linux/Mac)
- Or use a different port: Set `API_PORT` environment variable

## License

This project is provided as-is for local use.
