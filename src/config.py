"""Configuration management for RAG system."""
import os
from pathlib import Path
from typing import Optional

# Base paths
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"
CONFIG_DIR = BASE_DIR / "config"

# Create directories if they don't exist
DOCS_DIR.mkdir(exist_ok=True)
CHROMA_DB_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ChromaDB settings
CHROMA_COLLECTION_NAME = "rag_kb"

# LLM Provider Selection (ollama or huggingface)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "huggingface")  # Default to Hugging Face for deployment

# Ollama settings (if using Ollama)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# Hugging Face settings (if using Hugging Face)
HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2")
HF_API_KEY = os.getenv("HF_API_KEY", "")  # Get from https://huggingface.co/settings/tokens

# Chunking settings
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Retrieval settings
TOP_K = 5

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
# Railway provides PORT env var, fallback to 8000
API_PORT = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))


