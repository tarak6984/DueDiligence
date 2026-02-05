"""Vector store for semantic search and retrieval."""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import json
import hashlib


class VectorStore:
    """Simple in-memory vector store for demo purposes."""
    
    def __init__(self, data_dir: str = "data/vectors"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Two-layer index structure
        self.answer_index: Dict[str, Dict[str, Any]] = {}  # Layer 1: Section/semantic retrieval
        self.citation_index: Dict[str, Dict[str, Any]] = {}  # Layer 2: Citation chunks
        
        self._load_indices()
    
    def _load_indices(self):
        """Load indices from disk."""
        answer_path = self.data_dir / "answer_index.json"
        citation_path = self.data_dir / "citation_index.json"
        
        if answer_path.exists():
            with open(answer_path, 'r') as f:
                self.answer_index = json.load(f)
        
        if citation_path.exists():
            with open(citation_path, 'r') as f:
                self.citation_index = json.load(f)
    
    def _save_indices(self):
        """Save indices to disk."""
        with open(self.data_dir / "answer_index.json", 'w') as f:
            json.dump(self.answer_index, f, indent=2)
        
        with open(self.data_dir / "citation_index.json", 'w') as f:
            json.dump(self.citation_index, f, indent=2)
    
    def add_answer_chunks(self, document_id: str, chunks: List[Dict[str, Any]]):
        """Add chunks to answer retrieval index (Layer 1)."""
        for chunk in chunks:
            chunk_id = self._generate_chunk_id(document_id, chunk)
            self.answer_index[chunk_id] = {
                "document_id": document_id,
                "chunk_id": chunk_id,
                "text": chunk["text"],
                "embedding": chunk.get("embedding", []),
                "metadata": chunk.get("metadata", {})
            }
        self._save_indices()
    
    def add_citation_chunks(self, document_id: str, chunks: List[Dict[str, Any]]):
        """Add chunks to citation index (Layer 2)."""
        for chunk in chunks:
            chunk_id = self._generate_chunk_id(document_id, chunk)
            self.citation_index[chunk_id] = {
                "document_id": document_id,
                "chunk_id": chunk_id,
                "text": chunk["text"],
                "embedding": chunk.get("embedding", []),
                "page_number": chunk.get("page_number"),
                "bounding_box": chunk.get("bounding_box"),
                "metadata": chunk.get("metadata", {})
            }
        self._save_indices()
    
    def search_for_answer(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search Layer 1 index for answer generation."""
        # Simple keyword-based search for demo (in production, use embeddings)
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for chunk_id, chunk in self.answer_index.items():
            if document_ids and chunk["document_id"] not in document_ids:
                continue
            
            text_lower = chunk["text"].lower()
            text_words = set(text_lower.split())
            
            # Simple overlap score
            overlap = len(query_words & text_words)
            if overlap > 0:
                results.append({
                    **chunk,
                    "score": overlap / len(query_words)
                })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def search_for_citations(self, text: str, document_ids: Optional[List[str]] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search Layer 2 index for citation references."""
        results = []
        text_lower = text.lower()
        text_words = set(text_lower.split())
        
        for chunk_id, chunk in self.citation_index.items():
            if document_ids and chunk["document_id"] not in document_ids:
                continue
            
            chunk_text_lower = chunk["text"].lower()
            chunk_words = set(chunk_text_lower.split())
            
            overlap = len(text_words & chunk_words)
            if overlap > 0:
                results.append({
                    **chunk,
                    "score": overlap / len(text_words)
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def delete_document_chunks(self, document_id: str):
        """Remove all chunks for a document."""
        self.answer_index = {k: v for k, v in self.answer_index.items() if v["document_id"] != document_id}
        self.citation_index = {k: v for k, v in self.citation_index.items() if v["document_id"] != document_id}
        self._save_indices()
    
    def _generate_chunk_id(self, document_id: str, chunk: Dict[str, Any]) -> str:
        """Generate a unique chunk ID."""
        content = f"{document_id}_{chunk.get('text', '')}_{chunk.get('page_number', 0)}"
        return hashlib.md5(content.encode()).hexdigest()


# Global vector store instance
vector_store = VectorStore()
