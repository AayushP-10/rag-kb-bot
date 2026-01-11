"""Document ingestion and chunking."""
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2


class DocumentChunker:
    """Handles document ingestion and chunking."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_document(self, file_path: Path) -> str:
        """Load document content from file."""
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            return self._load_pdf(file_path)
        elif suffix in [".txt", ".md"]:
            return self._load_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    def _load_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        text = []
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return "\n".join(text)
    
    def _load_text(self, file_path: Path) -> str:
        """Load text from plain text or markdown file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata."""
        # Word-based chunking with overlap
        words = text.split()
        chunks = []
        
        i = 0
        chunk_index = 0
        
        while i < len(words):
            # Get chunk of words
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            # Generate chunk ID
            chunk_id = self._generate_chunk_id(chunk_text, metadata.get("source", ""), chunk_index)
            
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": {**metadata, "chunk_index": chunk_index}
            })
            
            chunk_index += 1
            
            # Move forward, accounting for overlap
            if i + self.chunk_size >= len(words):
                break
            i += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def _generate_chunk_id(self, text: str, source: str, chunk_index: int) -> str:
        """Generate unique ID for chunk."""
        content = f"{source}:{chunk_index}:{text[:100]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a file and return chunks."""
        text = self.load_document(file_path)
        metadata = {
            "source": str(file_path.name),
            "file_path": str(file_path),
            "file_type": file_path.suffix.lower()
        }
        return self.chunk_text(text, metadata)

