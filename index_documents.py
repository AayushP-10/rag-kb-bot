"""Script to index documents from the docs directory."""
import sys
import io
from pathlib import Path
from src.rag import RAGPipeline
import src.config as config

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def main():
    """Index all documents in the docs directory."""
    rag = RAGPipeline()
    docs_dir = config.DOCS_DIR
    
    # Find all supported documents
    doc_files = []
    for ext in [".pdf", ".txt", ".md"]:
        doc_files.extend(list(docs_dir.glob(f"*{ext}")))
    
    if not doc_files:
        print(f"No documents found in {docs_dir}")
        print(f"Supported formats: PDF, TXT, MD")
        return
    
    print(f"Found {len(doc_files)} document(s) to index...")
    
    for doc_file in doc_files:
        print(f"\nIndexing: {doc_file.name}")
        result = rag.ingest_document(doc_file)
        if result["status"] == "success":
            print(f"  [OK] Successfully indexed {result['chunks']} chunks")
        else:
            print(f"  [ERROR] Error: {result.get('error', 'Unknown error')}")
    
    # Print stats
    stats = rag.get_stats()
    print(f"\n[SUCCESS] Indexing complete! Total chunks in knowledge base: {stats['count']}")

if __name__ == "__main__":
    main()

