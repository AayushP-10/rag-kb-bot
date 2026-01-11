# How the RAG System Works - Complete Guide for Beginners

## 🎯 Quick Answer: How to Add New Documents

**You can already upload documents!** The web interface at http://localhost:8000 has an upload section.

1. **Open the web interface** (http://localhost:8000)
2. **Click "Choose File"** in the upload section
3. **Select your PDF, TXT, or MD file**
4. **Click "Upload & Index"**
5. **Wait for success message**
6. **Ask questions** about your new document!

---

## 📚 Complete Explanation: How Everything Works

### Overview: What is RAG?

**RAG = Retrieval-Augmented Generation**

Think of it like a librarian helping you:
1. You ask a question
2. Librarian (system) searches the library (vector database)
3. Finds relevant books/pages (document chunks)
4. Reads those pages (retrieves text)
5. Uses a smart assistant (LLM) to write an answer based on what was found
6. Gives you the answer with citations (which documents were used)

---

## 🔄 The Complete Flow: Upload → Query

### **PART 1: When You Upload a Document**

#### Step 1: File Upload (Web Interface)
```
User uploads file → FastAPI receives it → Saves to docs/ folder
```

**Code location**: `src/api.py` - `/api/ingest` endpoint

**What happens:**
1. You select a file in the browser
2. Browser sends file to server (POST request)
3. Server saves file to `docs/` directory
4. Server calls the indexing function

---

#### Step 2: Document Loading (`src/ingestion.py`)

**What happens:**
```python
DocumentChunker.load_document(file_path)
```

**For different file types:**
- **PDF**: Uses PyPDF2 to extract text from each page
- **TXT/MD**: Reads the file directly as text

**Example:**
```
PDF file → ["Page 1 text...", "Page 2 text..."] → "Page 1 text...\nPage 2 text..."
```

---

#### Step 3: Text Chunking (`src/ingestion.py`)

**Why chunk?**
- Documents can be HUGE (thousands of words)
- LLMs have token limits (can't process entire books at once)
- We need smaller, manageable pieces

**How it works:**
```python
DocumentChunker.chunk_text(text, metadata)
```

**Process:**
1. Split text into words
2. Create chunks of ~512 words each
3. Overlap chunks by 50 words (keeps context)

**Example:**
```
Original text (1500 words)
↓
Chunk 1: words 1-512
Chunk 2: words 463-974    (starts at 463 = 512-50 overlap)
Chunk 3: words 925-1437
Chunk 4: words 1388-1500
```

**Why overlap?**
- Sentences/ideas don't always align with chunk boundaries
- Overlap ensures important context isn't split between chunks

**Code location**: `src/ingestion.py` - `chunk_text()` method

---

#### Step 4: Generate Embeddings (`src/vector_store.py`)

**What are embeddings?**
- Embeddings = numerical representations of text meaning
- Think of them as "coordinates" in a high-dimensional space
- Similar meanings = close together in space

**Example (simplified):**
```
"dog" → [0.2, 0.8, 0.1, 0.5, ...]  (384 numbers for our model)
"puppy" → [0.25, 0.75, 0.15, 0.48, ...]  (very close numbers!)
"car" → [0.9, 0.1, 0.8, 0.2, ...]  (far away - different meaning)
```

**How it works:**
```python
sentence_transformers.encode(text)
# Input: "What is RAG?"
# Output: [0.23, 0.45, -0.12, 0.67, ...] (384 numbers)
```

**Model used**: `all-MiniLM-L6-v2`
- Converts text → 384-dimensional vector
- Trained on millions of text examples
- Understands semantic meaning

**Code location**: `src/vector_store.py` - `add_documents()` method

---

#### Step 5: Store in Vector Database (ChromaDB)

**What is ChromaDB?**
- Database specialized for storing vectors
- Can quickly find "similar" vectors (semantic search)
- Persists data to disk (`./chroma_db/` folder)

**What gets stored:**
```python
{
    "id": "unique_chunk_id",
    "embedding": [0.23, 0.45, ...],  # 384 numbers
    "document": "actual text content",
    "metadata": {
        "source": "myfile.pdf",
        "file_path": "docs/myfile.pdf",
        "chunk_index": 0
    }
}
```

**Why vector database?**
- Regular databases: "Find documents containing word 'dog'"
- Vector databases: "Find documents similar in MEANING to 'canine companion'"
- Much smarter search!

**Code location**: `src/vector_store.py` - `add_documents()` method

---

### **PART 2: When You Ask a Question**

#### Step 6: Question Embedding (`src/vector_store.py`)

**Same process as document chunks:**
```python
query_embedding = embedding_model.encode("What is RAG?")
# Output: [0.34, 0.12, 0.89, ...] (384 numbers)
```

**Why?**
- Convert question to same format as documents
- Compare "question vector" with "document vectors"

---

#### Step 7: Vector Search (`src/vector_store.py`)

**How similarity search works:**
1. Calculate distance between query vector and all document vectors
2. Distance = how "far apart" they are (cosine similarity)
3. Closer = more similar in meaning
4. Return top K closest chunks (default: 5)

**Example:**
```
Query: "What is RAG?"
↓
Chunk 1: "RAG is a technique..." → Distance: 0.12 (very close!)
Chunk 2: "Python syntax..." → Distance: 0.89 (far away)
Chunk 3: "RAG combines retrieval..." → Distance: 0.15 (close!)
...
↓
Returns: Top 5 closest chunks
```

**Code location**: `src/vector_store.py` - `search()` method

---

#### Step 8: Build Context (`src/rag.py`)

**Combine retrieved chunks:**
```python
context = """
[Document 1]: RAG is a technique that combines...
[Document 2]: Retrieval-Augmented Generation (RAG)...
[Document 3]: The RAG pipeline consists of...
"""
```

**Why multiple chunks?**
- More context = better answers
- Different chunks might have different information
- LLM can synthesize information from multiple sources

---

#### Step 9: Generate Answer (Ollama LLM)

**Build the prompt:**
```python
prompt = f"""
Context from knowledge base:
{context}

Question: {question}

Answer the question based on the context provided above.
If the answer cannot be found in the context, say so.
Cite which document(s) you used in your answer.
"""
```

**Send to Ollama:**
- Ollama receives prompt
- llama3.1:8b model processes it
- Generates answer word-by-word
- Returns complete answer

**Why this approach?**
- LLM only sees YOUR documents (no general knowledge)
- Answer is "grounded" in retrieved documents
- Can cite sources (transparency)

**Code location**: `src/llm.py` - `generate()` method

---

#### Step 10: Extract Sources (`src/rag.py`)

**Track which documents were used:**
```python
sources = [
    {"source": "myfile.pdf", "file_path": "docs/myfile.pdf"},
    {"source": "another.pdf", "file_path": "docs/another.pdf"}
]
```

**Why?**
- Transparency: know where answer came from
- Verification: can check original documents
- Trust: shows sources

---

#### Step 11: Return Response (API)

**Format the response:**
```python
{
    "question": "What is RAG?",
    "answer": "RAG is a technique that...",
    "sources": [
        {"source": "sample_document.txt", "file_path": "..."}
    ]
}
```

**Display in browser:**
- Shows answer
- Lists source documents
- User can verify information

---

## 🧠 Key Concepts Explained

### **1. Embeddings (Vector Representations)**

**Simple analogy:**
- Words in a dictionary vs. words in a thesaurus
- Dictionary: alphabetical order (no meaning relationship)
- Thesaurus: grouped by meaning
- Embeddings = "thesaurus coordinates" in multi-dimensional space

**Technical:**
- Text → numbers (384 numbers for our model)
- Similar meanings = similar numbers
- Model learned this from billions of text examples

---

### **2. Vector Search (Semantic Search)**

**Regular search:**
- "Find documents with word 'dog'"
- Exact word matching
- Misses synonyms, context

**Vector/Semantic search:**
- "Find documents similar to 'canine companion'"
- Meaning-based matching
- Finds "dog", "puppy", "pet", etc.
- Much smarter!

**How it works:**
- Calculate distance between vectors
- Closer = more similar
- Use cosine similarity (measures angle between vectors)

---

### **3. Chunking Strategy**

**Why chunks?**
- LLMs have token limits (can't process entire books)
- Need manageable pieces
- Allows precise retrieval (get only relevant parts)

**Our strategy:**
- 512 words per chunk
- 50 word overlap
- Word-based (not sentence-based) for consistency

**Trade-offs:**
- Smaller chunks: More precise, but lose context
- Larger chunks: More context, but less precise
- Overlap: Prevents splitting important ideas

---

### **4. RAG vs. Regular LLM**

**Regular LLM (like ChatGPT):**
- Trained on internet data (outdated, may not know your documents)
- Can hallucinate (make up information)
- No citations

**RAG System:**
- Uses YOUR documents (up-to-date, specific)
- Answers grounded in retrieved text (less hallucination)
- Provides citations
- Can update knowledge without retraining model

---

## 🔍 Code Walkthrough: Upload → Query

### Upload Flow (Code Path)

```
1. Browser uploads file
   → src/api.py: ingest_document() endpoint

2. Save file
   → docs/myfile.pdf

3. Process file
   → src/rag.py: ingest_document()
   → src/ingestion.py: DocumentChunker.process_file()
   → Load document, chunk text

4. Generate embeddings
   → src/vector_store.py: add_documents()
   → sentence_transformers.encode()

5. Store in ChromaDB
   → chromadb.collection.add()
   → Saved to ./chroma_db/
```

### Query Flow (Code Path)

```
1. User asks question
   → Browser sends POST to /api/query

2. Retrieve documents
   → src/api.py: query() endpoint
   → src/rag.py: query()
   → src/vector_store.py: search()
   → Embed query, search ChromaDB

3. Generate answer
   → src/llm.py: generate()
   → Build prompt with context
   → Send to Ollama API
   → Receive answer

4. Extract sources
   → src/rag.py: _extract_sources()
   → Get unique sources from retrieved docs

5. Return response
   → JSON with question, answer, sources
   → Display in browser
```

---

## 🛠️ Technical Stack Breakdown

### **1. sentence-transformers (Embeddings)**
- **What**: Converts text to vectors
- **Model**: all-MiniLM-L6-v2 (384 dimensions)
- **CPU-friendly**: Works without GPU
- **Fast**: Optimized for production

### **2. ChromaDB (Vector Database)**
- **What**: Stores and searches vectors
- **Type**: Persistent (saves to disk)
- **Search**: Cosine similarity (semantic search)
- **Why**: Fast, local, free

### **3. Ollama (LLM)**
- **What**: Runs language models locally
- **Model**: llama3.1:8b (8 billion parameters)
- **Local**: No API costs, private
- **HTTP API**: Easy to integrate

### **4. FastAPI (Backend)**
- **What**: Web framework
- **Purpose**: REST API + Web UI
- **Endpoints**: /api/ingest, /api/query, /api/stats

---

## 🎓 Learning Path: Understanding Each Component

### Start Here:
1. **Try uploading a document** - See it work
2. **Read the code** in this order:
   - `src/ingestion.py` - How documents become chunks
   - `src/vector_store.py` - How embeddings work
   - `src/rag.py` - How everything connects
   - `src/api.py` - How web interface works

### Deep Dive Topics:
1. **Embeddings**: Research "word embeddings", "sentence transformers"
2. **Vector Search**: Research "cosine similarity", "semantic search"
3. **RAG**: Research "Retrieval-Augmented Generation" papers
4. **Chunking**: Research "text chunking strategies for RAG"

---

## 💡 Common Questions

### **Q: Why do I need to index documents?**
**A**: Indexing converts documents into a searchable format (vectors). Without indexing, the system can't find relevant information when you ask questions.

### **Q: What if I upload the same document twice?**
**A**: It will be indexed again (duplicates allowed). Each chunk gets a unique ID, so duplicates will exist. For production, you might want to check if a document already exists.

### **Q: How much data can I store?**
**A**: Depends on your disk space. ChromaDB stores efficiently, but:
- Each chunk = ~384 numbers (embeddings) + text
- 1,000 chunks ≈ few MB
- Millions of chunks = several GB

### **Q: Can I use other models?**
**A**: Yes! Change `OLLAMA_MODEL` in `src/config.py` or set environment variable. Make sure the model is pulled in Ollama first.

### **Q: How accurate is the search?**
**A**: Depends on:
- Embedding model quality (sentence-transformers is good)
- Chunk size (512 words is a good balance)
- Question clarity (clearer questions = better results)
- Document quality (well-written docs = better embeddings)

---

## 🚀 Next Steps: Customize Your System

### **1. Change Chunk Size**
Edit `src/config.py`:
```python
CHUNK_SIZE = 512  # Try 256, 512, 1024
CHUNK_OVERLAP = 50  # Try 25, 50, 100
```

### **2. Change Retrieval Count**
Edit `src/config.py`:
```python
TOP_K = 5  # Try 3, 5, 10 (more = more context, but slower)
```

### **3. Use Different Embedding Model**
Edit `src/config.py`:
```python
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Try other sentence-transformers models
```

### **4. Use Different LLM**
Edit `src/config.py` or set environment variable:
```python
OLLAMA_MODEL = "llama3.1:8b"  # Try other Ollama models
```

---

## 📖 Summary: The Magic Behind RAG

1. **Documents → Chunks**: Break documents into manageable pieces
2. **Chunks → Vectors**: Convert text to numbers (embeddings)
3. **Vectors → Database**: Store in searchable vector database
4. **Question → Vector**: Convert question to same format
5. **Search**: Find similar document chunks
6. **Context → LLM**: Send relevant chunks to language model
7. **Answer**: LLM generates answer based on YOUR documents
8. **Citations**: Track which documents were used

**The key insight**: Instead of training the LLM on your documents (expensive, slow), we give it relevant documents at query time (cheap, fast, flexible).

---

Now you understand how it all works! Try uploading your own documents and see the magic happen! 🎉

