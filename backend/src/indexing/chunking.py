"""Chunking strategies for document indexing."""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ChunkConfig:
    """Configuration for chunking strategy."""
    chunk_size: int = 500  # characters per chunk
    overlap: int = 50      # overlap between chunks
    min_chunk_size: int = 100


class ChunkingStrategy:
    """Create chunks for multi-layer indexing."""
    
    def __init__(self, config: ChunkConfig = None):
        self.config = config or ChunkConfig()
    
    def create_answer_chunks(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create larger chunks for answer retrieval (Layer 1)."""
        # Use larger chunks for semantic retrieval
        large_config = ChunkConfig(chunk_size=1000, overlap=100)
        return self._create_chunks(parsed_doc, large_config, chunk_type="answer")
    
    def create_citation_chunks(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create smaller chunks for citations (Layer 2)."""
        # Use smaller chunks for precise citations
        small_config = ChunkConfig(chunk_size=300, overlap=30)
        return self._create_chunks(parsed_doc, small_config, chunk_type="citation")
    
    def _create_chunks(self, parsed_doc: Dict[str, Any], config: ChunkConfig, chunk_type: str) -> List[Dict[str, Any]]:
        """Create chunks from parsed document."""
        chunks = []
        
        for page in parsed_doc.get("pages", []):
            text = page.get("text", "")
            page_number = page.get("page_number")
            
            # Split text into sentences (simple split for demo)
            sentences = text.split('. ')
            
            current_chunk = ""
            chunk_start = 0
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > config.chunk_size and len(current_chunk) > config.min_chunk_size:
                    # Save current chunk
                    chunks.append({
                        "text": current_chunk.strip(),
                        "page_number": page_number,
                        "chunk_type": chunk_type,
                        "metadata": {
                            "source_page": page_number,
                            **page.get("metadata", {})
                        }
                    })
                    
                    # Start new chunk with overlap
                    overlap_text = current_chunk[-config.overlap:] if len(current_chunk) > config.overlap else current_chunk
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk += " " + sentence
            
            # Add remaining text as final chunk
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "page_number": page_number,
                    "chunk_type": chunk_type,
                    "metadata": {
                        "source_page": page_number,
                        **page.get("metadata", {})
                    }
                })
        
        return chunks


# Global chunking strategy instance
chunking_strategy = ChunkingStrategy()
