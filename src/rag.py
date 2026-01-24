"""RAG pipeline implementation."""
from typing import Dict, Any, List, Optional
from pathlib import Path
from src.ingestion import DocumentChunker
from src.vector_store import VectorStore
import src.config as config

# Import LLM based on provider
if config.LLM_PROVIDER == "ollama":
    from src.llm import OllamaLLM as LLM
else:
    from src.llm_huggingface import HuggingFaceLLM as LLM


class RAGPipeline:
    """Main RAG pipeline."""
    
    def __init__(self):
        self.chunker = DocumentChunker(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        self.vector_store = VectorStore()
        # Initialize LLM based on provider
        self.llm = LLM()
    
    def ingest_document(self, file_path: Path) -> Dict[str, Any]:
        """Ingest a document into the knowledge base."""
        try:
            chunks = self.chunker.process_file(file_path)
            self.vector_store.add_documents(chunks)
            return {
                "status": "success",
                "file": str(file_path),
                "chunks": len(chunks)
            }
        except Exception as e:
            return {
                "status": "error",
                "file": str(file_path),
                "error": str(e)
            }
    
    def query(self, question: str, top_k: int = None, source_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """Query the RAG system.
        
        Args:
            question: The question to ask
            top_k: Number of document chunks to retrieve
            source_filter: Optional list of source file names to filter by (e.g., ["myfile.pdf"])
        """
        top_k = top_k or config.TOP_K
        
        # Retrieve relevant documents
        retrieved_docs = self.vector_store.search(question, top_k=top_k, source_filter=source_filter)
        
        if not retrieved_docs:
            return {
                "question": question,
                "answer": "No relevant documents found in the knowledge base.",
                "sources": [],
                "retrieved_docs": []
            }
        
        # Extract context texts
        context_texts = [doc["text"] for doc in retrieved_docs]
        
        # Generate answer using LLM
        try:
            answer = self.llm.generate(question, context=context_texts)
        except Exception as e:
            return {
                "question": question,
                "answer": f"Error generating answer: {str(e)}",
                "sources": self._extract_sources(retrieved_docs),
                "retrieved_docs": retrieved_docs
            }
        
        # Extract sources
        sources = self._extract_sources(retrieved_docs)
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "retrieved_docs": retrieved_docs
        }
    
    def _extract_sources(self, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract source information from retrieved documents."""
        sources = []
        seen_sources = set()
        
        for doc in retrieved_docs:
            source = doc["metadata"].get("source", "Unknown")
            if source not in seen_sources:
                sources.append({
                    "source": source,
                    "file_path": doc["metadata"].get("file_path", "")
                })
                seen_sources.add(source)
        
        return sources
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return self.vector_store.get_collection_info()

