"""Main entry point for RAG system."""
import uvicorn
from src.api import app
import src.config as config

if __name__ == "__main__":
    print(f"Starting RAG Knowledge Base Assistant...")
    print(f"API will be available at http://{config.API_HOST}:{config.API_PORT}")
    print(f"Make sure Ollama is running at {config.OLLAMA_BASE_URL}")
    print(f"Using model: {config.OLLAMA_MODEL}")
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level="info"
    )

