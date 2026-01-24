"""LLM integration using Hugging Face Inference API."""
import requests
import os
from typing import List, Optional
import src.config as config


class HuggingFaceLLM:
    """Interface to Hugging Face Inference API."""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or config.HF_API_URL
        self.api_key = api_key or config.HF_API_KEY
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
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
        
        # Make request to Hugging Face API
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers if self.headers else None,
                json=payload,
                timeout=60
            )
            
            # Handle model loading (503 status)
            if response.status_code == 503:
                # Model is loading, wait and retry
                import time
                time.sleep(10)
                response = requests.post(
                    self.api_url,
                    headers=self.headers if self.headers else None,
                    json=payload,
                    timeout=60
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract generated text (HF API returns different formats)
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict):
                    return result[0].get("generated_text", result[0].get("text", ""))
                else:
                    return str(result[0])
            elif isinstance(result, dict):
                return result.get("generated_text", result.get("text", str(result)))
            else:
                return str(result)
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                raise Exception(
                    "Hugging Face model is loading. Please wait a moment and try again. "
                    "Free tier models may take 20-30 seconds to wake up."
                )
            raise Exception(f"Error calling Hugging Face API: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Hugging Face API: {e}")
    
    def is_model_available(self) -> bool:
        """Check if Hugging Face API is available."""
        try:
            # Simple check - try a minimal request
            test_payload = {"inputs": "test", "parameters": {"max_new_tokens": 1}}
            response = requests.post(
                self.api_url,
                headers=self.headers if self.headers else None,
                json=test_payload,
                timeout=10
            )
            # 200 or 503 (loading) both mean the endpoint exists
            return response.status_code in [200, 503]
        except:
            return False

