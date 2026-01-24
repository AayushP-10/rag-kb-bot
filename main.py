"""Main entry point for RAG system."""
import uvicorn
from src.api import app
import src.config as config

if __name__ == "__main__":
    print(f"Starting RAG Knowledge Base Assistant...")
    print(f"API will be available at http://{config.API_HOST}:{config.API_PORT}")
    
    if config.LLM_PROVIDER == "ollama":
        print(f"Using Ollama at {config.OLLAMA_BASE_URL}")
        print(f"Model: {config.OLLAMA_MODEL}")
    else:
        print(f"Using Hugging Face Inference API")
        print(f"Model: {config.HF_API_URL}")
        if not config.HF_API_KEY:
            print("⚠️  Warning: No HF_API_KEY set. Some models may require authentication.")
            print("   Get a free token at: https://huggingface.co/settings/tokens")
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level="info"
    )


