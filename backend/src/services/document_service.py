"""Document management service."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
from ..models import Document, IndexingStatus
from ..storage.database import db
from ..storage.object_storage import object_storage
from ..utils import generate_id, validate_file_type, get_file_type


class DocumentService:
    """Handle document operations."""
    
    def __init__(self):
        self.db = db
        self.storage = object_storage
    
    def upload_document(self, filename: str, file_content: bytes, 
                       is_questionnaire: bool = False) -> Document:
        """Upload and register a new document."""
        if not validate_file_type(filename):
            raise ValueError(f"Unsupported file type: {filename}")
        
        document_id = generate_id("doc")
        
        # Save file to storage
        storage_path = self.storage.save_file(filename, file_content, document_id)
        
        # Create document record
        document_data = {
            "id": document_id,
            "name": filename,
            "file_type": get_file_type(filename),
            "file_size": len(file_content),
            "file_path": storage_path,
            "indexing_status": IndexingStatus.PENDING.value,
            "is_questionnaire": is_questionnaire,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.db.insert("documents", document_id, document_data)
        
        return Document(**document_data)
    
    def register_existing_document(self, file_path: str, is_questionnaire: bool = False) -> Document:
        """Register an existing document from the data directory."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        filename = path.name
        if not validate_file_type(filename):
            raise ValueError(f"Unsupported file type: {filename}")
        
        document_id = generate_id("doc")
        
        # Copy file to storage
        storage_path = self.storage.copy_from_data_dir(file_path, document_id)
        
        # Create document record
        file_size = path.stat().st_size
        document_data = {
            "id": document_id,
            "name": filename,
            "file_type": get_file_type(filename),
            "file_size": file_size,
            "file_path": storage_path,
            "indexing_status": IndexingStatus.PENDING.value,
            "is_questionnaire": is_questionnaire,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.db.insert("documents", document_id, document_data)
        
        return Document(**document_data)
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID."""
        document_data = self.db.get("documents", document_id)
        return Document(**document_data) if document_data else None
    
    def get_all_documents(self, is_questionnaire: Optional[bool] = None) -> List[Document]:
        """Get all documents, optionally filtered by type."""
        if is_questionnaire is not None:
            documents_data = self.db.find("documents", {"is_questionnaire": is_questionnaire})
        else:
            documents_data = self.db.find("documents")
        
        return [Document(**d) for d in documents_data]
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        document = self.get_document(document_id)
        if not document:
            return False
        
        # Delete file from storage
        self.storage.delete_file(document.file_path)
        
        # Delete from database
        self.db.delete("documents", document_id)
        
        return True
    
    def update_indexing_status(self, document_id: str, status: IndexingStatus,
                              error_message: Optional[str] = None) -> Document:
        """Update document indexing status."""
        updates = {
            "indexing_status": status.value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if status == IndexingStatus.INDEXED:
            updates["indexed_at"] = datetime.now(timezone.utc).isoformat()
        
        if error_message:
            updates["error_message"] = error_message
        
        self.db.update("documents", document_id, updates)
        updated = self.db.get("documents", document_id)
        
        return Document(**updated)


# Global service instance
document_service = DocumentService()
