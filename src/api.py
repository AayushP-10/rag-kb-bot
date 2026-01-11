"""FastAPI backend for RAG system."""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel
import tempfile
import shutil

from src.rag import RAGPipeline
import src.config as config


app = FastAPI(title="RAG Knowledge Base Assistant")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline
rag = RAGPipeline()


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None
    source_filter: Optional[List[str]] = None  # Filter by source file names


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list


@app.get("/")
async def root():
    """Serve the web UI."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RAG Knowledge Base Assistant</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            .content {
                padding: 40px;
            }
            .upload-section {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                border: 2px dashed #667eea;
            }
            .upload-section h2 {
                color: #333;
                margin-bottom: 20px;
            }
            .file-input-wrapper {
                position: relative;
                display: inline-block;
                width: 100%;
            }
            .file-input-wrapper input[type=file] {
                font-size: 18px;
                padding: 15px;
                width: 100%;
                border: 2px solid #667eea;
                border-radius: 10px;
                background: white;
            }
            .upload-btn {
                margin-top: 15px;
                padding: 15px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                cursor: pointer;
                transition: background 0.3s;
            }
            .upload-btn:hover {
                background: #5568d3;
            }
            .upload-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .query-section {
                margin-top: 30px;
            }
            .query-section h2 {
                color: #333;
                margin-bottom: 20px;
            }
            .query-input {
                width: 100%;
                padding: 20px;
                font-size: 18px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-bottom: 15px;
                font-family: inherit;
            }
            .query-input:focus {
                outline: none;
                border-color: #667eea;
            }
            .query-btn {
                padding: 15px 40px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                cursor: pointer;
                transition: background 0.3s;
            }
            .query-btn:hover {
                background: #5568d3;
            }
            .query-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .answer-section {
                margin-top: 30px;
                padding: 30px;
                background: #f8f9fa;
                border-radius: 15px;
                display: none;
            }
            .answer-section.visible {
                display: block;
            }
            .answer-section h3 {
                color: #333;
                margin-bottom: 15px;
            }
            .answer-text {
                background: white;
                padding: 20px;
                border-radius: 10px;
                line-height: 1.8;
                color: #333;
                white-space: pre-wrap;
                margin-bottom: 20px;
            }
            .sources {
                margin-top: 20px;
            }
            .sources h4 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .source-list {
                list-style: none;
                padding: 0;
            }
            .source-item {
                background: white;
                padding: 10px 15px;
                margin-bottom: 10px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .status {
                padding: 15px;
                border-radius: 10px;
                margin-top: 15px;
                display: none;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
                display: block;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                display: block;
            }
            .status.info {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
                display: block;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            .loading.visible {
                display: block;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .stats {
                background: #e9ecef;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .stats h3 {
                color: #333;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 RAG Knowledge Base Assistant</h1>
                <p>Ask questions based on your uploaded documents</p>
            </div>
            <div class="content">
                <div class="stats">
                    <h3>Knowledge Base Statistics</h3>
                    <p id="stats-text">Loading...</p>
                    <div id="sources-list" style="margin-top: 10px; display: none;">
                        <h4 style="color: #667eea; font-size: 14px; margin-bottom: 5px;">Indexed Documents:</h4>
                        <div id="sources-container" style="display: flex; flex-wrap: wrap; gap: 10px;"></div>
                    </div>
                </div>
                
                <div class="upload-section">
                    <h2>📄 Upload Document</h2>
                    <form id="upload-form">
                        <div class="file-input-wrapper">
                            <input type="file" id="file-input" accept=".pdf,.txt,.md" required>
                        </div>
                        <button type="submit" class="upload-btn" id="upload-btn">Upload & Index</button>
                        <div id="upload-status" class="status"></div>
                    </form>
                </div>
                
                <div class="query-section">
                    <h2>💬 Ask a Question</h2>
                    <input type="text" class="query-input" id="query-input" placeholder="Enter your question here...">
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; color: #667eea; font-weight: bold; margin-bottom: 5px;">
                            Filter by documents (optional - leave empty to search all):
                        </label>
                        <select id="source-filter" multiple style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 14px;">
                            <option value="">-- Select documents (hold Ctrl/Cmd for multiple) --</option>
                        </select>
                        <small style="color: #666; display: block; margin-top: 5px;">
                            Tip: Leave empty to search all documents, or select specific documents
                        </small>
                    </div>
                    <button class="query-btn" id="query-btn">Ask</button>
                    <div id="query-loading" class="loading">
                        <div class="spinner"></div>
                        <p>Thinking...</p>
                    </div>
                    <div id="query-status" class="status"></div>
                    <div class="answer-section" id="answer-section">
                        <h3>Answer</h3>
                        <div class="answer-text" id="answer-text"></div>
                        <div class="sources">
                            <h4>Sources</h4>
                            <ul class="source-list" id="source-list"></ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Load stats
            let availableSources = [];
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    document.getElementById('stats-text').textContent = 
                        `Chunks indexed: ${data.count || 0}`;
                    
                    // Show available sources
                    if (data.sources && data.sources.length > 0) {
                        availableSources = data.sources;
                        const sourcesContainer = document.getElementById('sources-container');
                        sourcesContainer.innerHTML = '';
                        data.sources.forEach(source => {
                            const badge = document.createElement('span');
                            badge.textContent = source;
                            badge.style.cssText = 'background: #667eea; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;';
                            sourcesContainer.appendChild(badge);
                        });
                        document.getElementById('sources-list').style.display = 'block';
                    }
                    
                    // Populate source filter dropdown
                    populateSourceFilter();
                } catch (error) {
                    document.getElementById('stats-text').textContent = 'Error loading stats';
                }
            }
            
            // Populate source filter dropdown
            function populateSourceFilter() {
                const select = document.getElementById('source-filter');
                if (!select) return;
                
                // Clear existing options except the first one
                while (select.options.length > 1) {
                    select.remove(1);
                }
                // Add available sources
                availableSources.forEach(source => {
                    const option = document.createElement('option');
                    option.value = source;
                    option.textContent = source;
                    select.appendChild(option);
                });
            }
            
            loadStats();
            
            // Upload form
            document.getElementById('upload-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const fileInput = document.getElementById('file-input');
                const file = fileInput.files[0];
                const uploadBtn = document.getElementById('upload-btn');
                const status = document.getElementById('upload-status');
                
                if (!file) return;
                
                uploadBtn.disabled = true;
                status.className = 'status info';
                status.textContent = 'Uploading and indexing...';
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/api/ingest', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        status.className = 'status success';
                        status.textContent = `Success! Indexed ${data.chunks} chunks from ${data.file}`;
                        fileInput.value = '';
                        loadStats();
                    } else {
                        status.className = 'status error';
                        status.textContent = `Error: ${data.error || 'Unknown error'}`;
                    }
                } catch (error) {
                    status.className = 'status error';
                    status.textContent = `Error: ${error.message}`;
                } finally {
                    uploadBtn.disabled = false;
                }
            });
            
            // Query
            document.getElementById('query-btn').addEventListener('click', async () => {
                const queryInput = document.getElementById('query-input');
                const sourceFilter = document.getElementById('source-filter');
                const query = queryInput.value.trim();
                const queryBtn = document.getElementById('query-btn');
                const loading = document.getElementById('query-loading');
                const status = document.getElementById('query-status');
                const answerSection = document.getElementById('answer-section');
                const answerText = document.getElementById('answer-text');
                const sourceList = document.getElementById('source-list');
                
                if (!query) return;
                
                // Get selected sources
                const selectedSources = Array.from(sourceFilter.selectedOptions)
                    .map(opt => opt.value)
                    .filter(val => val !== '');
                
                queryBtn.disabled = true;
                loading.className = 'loading visible';
                status.className = 'status';
                answerSection.classList.remove('visible');
                
                try {
                    const requestBody = { question: query };
                    if (selectedSources.length > 0) {
                        requestBody.source_filter = selectedSources;
                    }
                    
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestBody)
                    });
                    const data = await response.json();
                    
                    loading.className = 'loading';
                    
                    if (data.answer) {
                        answerText.textContent = data.answer;
                        sourceList.innerHTML = '';
                        if (data.sources && data.sources.length > 0) {
                            data.sources.forEach(source => {
                                const li = document.createElement('li');
                                li.className = 'source-item';
                                li.textContent = source.source;
                                sourceList.appendChild(li);
                            });
                        }
                        answerSection.classList.add('visible');
                    } else {
                        status.className = 'status error';
                        status.textContent = 'No answer received';
                    }
                } catch (error) {
                    loading.className = 'loading';
                    status.className = 'status error';
                    status.textContent = `Error: ${error.message}`;
                } finally {
                    queryBtn.disabled = false;
                }
            });
            
            // Enter key for query
            document.getElementById('query-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    document.getElementById('query-btn').click();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/stats")
async def get_stats():
    """Get knowledge base statistics."""
    try:
        stats = rag.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Ingest a document into the knowledge base."""
    # Check file type
    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".pdf", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, TXT, or MD.")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = Path(tmp_file.name)
    
    try:
        # Move to docs directory
        docs_path = config.DOCS_DIR / file.filename
        shutil.move(str(tmp_path), str(docs_path))
        
        # Ingest document
        result = rag.ingest_document(docs_path)
        return result
    except Exception as e:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system.
    
    You can filter by specific documents using source_filter.
    Example: {"question": "What is RAG?", "source_filter": ["myfile.pdf"]}
    """
    try:
        result = rag.query(
            request.question, 
            top_k=request.top_k,
            source_filter=request.source_filter
        )
        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)

