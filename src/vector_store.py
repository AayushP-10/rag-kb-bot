"""Vector store using ChromaDB."""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import src.config as config


class VectorStore:
    """Manages vector storage with ChromaDB."""
    
    def __init__(self, persist_directory: Path = None):
        self.persist_directory = persist_directory or config.CHROMA_DB_DIR
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """Add document chunks to vector store."""
        if not chunks:
            return
        
        texts = [chunk["text"] for chunk in chunks]
        ids = [chunk["id"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False).tolist()
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, top_k: int = None, source_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query: The search query text
            top_k: Number of results to return
            source_filter: Optional list of source file names to filter by
        """
        top_k = top_k or config.TOP_K
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False).tolist()[0]
        
        # Build where filter if source_filter is provided
        where_filter = None
        if source_filter:
            # ChromaDB supports filtering with $in operator
            where_filter = {"source": {"$in": source_filter}}
        
        # Search in ChromaDB
        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k
        }
        if where_filter:
            query_kwargs["where"] = where_filter
        
        results = self.collection.query(**query_kwargs)
        
        # Format results
        retrieved_docs = []
        if results["documents"] and len(results["documents"][0]) > 0:
            for i in range(len(results["documents"][0])):
                retrieved_docs.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
        
        return retrieved_docs
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        count = self.collection.count()
        
        # Get all documents to extract unique sources
        all_results = self.collection.get()
        unique_sources = set()
        if all_results.get("metadatas"):
            for metadata in all_results["metadatas"]:
                if metadata and "source" in metadata:
                    unique_sources.add(metadata["source"])
        
        return {
            "count": count,
            "collection_name": config.CHROMA_COLLECTION_NAME,
            "sources": sorted(list(unique_sources))
        }
    
    def delete_collection(self) -> None:
        """Delete the collection (for testing/reset)."""
        try:
            self.client.delete_collection(name=config.CHROMA_COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=config.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Error deleting collection: {e}")

