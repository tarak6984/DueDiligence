"""Document indexer orchestrator."""

from typing import Dict, Any
from .document_parser import document_parser
from .chunking import chunking_strategy
from ..storage.vector_store import vector_store
from ..storage.database import db
from ..models import IndexingStatus
from datetime import datetime


class DocumentIndexer:
    """Orchestrate document indexing pipeline."""
    
    def __init__(self):
        self.parser = document_parser
        self.chunking = chunking_strategy
        self.vector_store = vector_store
        self.db = db
    
    def index_document(self, document_id: str, file_path: str) -> Dict[str, Any]:
        """Index a document through the multi-layer pipeline."""
        try:
            # Update status to INDEXING
            self.db.update("documents", document_id, {
                "indexing_status": IndexingStatus.INDEXING.value
            })
            
            # Parse document
            parsed = self.parser.parse(file_path)
            
            # Create chunks for both layers
            answer_chunks = self.chunking.create_answer_chunks(parsed)
            citation_chunks = self.chunking.create_citation_chunks(parsed)
            
            # Add to vector indices
            self.vector_store.add_answer_chunks(document_id, answer_chunks)
            self.vector_store.add_citation_chunks(document_id, citation_chunks)
            
            # Update status to INDEXED
            self.db.update("documents", document_id, {
                "indexing_status": IndexingStatus.INDEXED.value,
                "indexed_at": datetime.utcnow().isoformat()
            })
            
            # Mark ALL_DOCS projects as OUTDATED
            self._mark_all_docs_projects_outdated()
            
            return {
                "document_id": document_id,
                "status": "indexed",
                "answer_chunks": len(answer_chunks),
                "citation_chunks": len(citation_chunks)
            }
            
        except Exception as e:
            # Update status to FAILED
            self.db.update("documents", document_id, {
                "indexing_status": IndexingStatus.FAILED.value,
                "error_message": str(e)
            })
            raise
    
    def _mark_all_docs_projects_outdated(self):
        """Mark all projects with ALL_DOCS scope as OUTDATED."""
        from ..models import DocumentScope, ProjectStatus
        
        projects = self.db.find("projects", {"document_scope": DocumentScope.ALL_DOCS.value})
        
        for project in projects:
            if project["status"] == ProjectStatus.READY.value:
                self.db.update("projects", project["id"], {
                    "status": ProjectStatus.OUTDATED.value,
                    "updated_at": datetime.utcnow().isoformat()
                })
    
    def reindex_document(self, document_id: str, file_path: str) -> Dict[str, Any]:
        """Reindex a document (delete old chunks and reindex)."""
        # Remove old chunks
        self.vector_store.delete_document_chunks(document_id)
        
        # Index again
        return self.index_document(document_id, file_path)


# Global indexer instance
document_indexer = DocumentIndexer()
