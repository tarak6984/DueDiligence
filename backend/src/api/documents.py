"""Document API endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from ..models import Document
from ..services.document_service import document_service
from ..indexing.indexer import document_indexer
from ..workers.request_tracker import request_tracker

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), is_questionnaire: bool = False):
    """Upload a new document."""
    try:
        content = await file.read()
        document = document_service.upload_document(
            file.filename,
            content,
            is_questionnaire
        )
        return document.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index-document-async/{document_id}")
async def index_document_async(document_id: str):
    """Index a document asynchronously."""
    try:
        document = document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create async request tracker
        async_request = request_tracker.create_request("index_document")
        
        # Execute indexing in background
        request_tracker.execute_async(
            async_request.id,
            document_indexer.index_document,
            document_id,
            document.file_path
        )
        
        return {
            "request_id": async_request.id,
            "status": "pending",
            "message": "Document indexing initiated"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-document/{document_id}")
async def get_document(document_id: str):
    """Get document by ID."""
    try:
        document = document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_documents(is_questionnaire: Optional[bool] = None):
    """Get all documents."""
    try:
        documents = document_service.get_all_documents(is_questionnaire)
        return {
            "documents": [d.model_dump() for d in documents],
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    try:
        success = document_service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
