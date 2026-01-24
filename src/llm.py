"""LLM integration with Ollama."""
import requests
import json
from typing import List, Dict, Any
import src.config as config


class OllamaLLM:
    """Interface to Ollama LLM."""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.model = model or config.OLLAMA_MODEL
        self.api_url = f"{self.base_url}/api/generate"
    
    def generate(self, prompt: str, context: List[str] = None) -> str:
        """Generate response from LLM."""
        # Build context-aware prompt
        if context:
            context_text = "\n\n".join([
                f"[Document {i+1}]: {doc}" 
                for i, doc in enumerate(context)
            ])
            full_prompt = f"""Context from knowledge base:
{context_text}

Question: {prompt}

Answer the question based on the context provided above. If the answer cannot be found in the context, say so. Cite which document(s) you used in your answer."""
        else:
            full_prompt = prompt
        
        # Make request to Ollama
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. "
                f"Please make sure Ollama is running and the model {self.model} is available."
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Ollama API: {e}")
    
    def check_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


