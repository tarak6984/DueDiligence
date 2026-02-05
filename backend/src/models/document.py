"""Document data models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class IndexingStatus(str, Enum):
    """Status of document indexing."""
    PENDING = "PENDING"
    INDEXING = "INDEXING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


class Document(BaseModel):
    """A document in the system."""
    id: str = Field(..., description="Unique document identifier")
    name: str = Field(..., description="Document filename")
    file_type: str = Field(..., description="File type (PDF, DOCX, XLSX, PPTX)")
    file_size: int = Field(..., description="File size in bytes")
    file_path: str = Field(..., description="Storage path")
    indexing_status: IndexingStatus = Field(default=IndexingStatus.PENDING)
    is_questionnaire: bool = Field(default=False, description="Whether this is a questionnaire document")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    indexed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_1",
                "name": "prospectus.pdf",
                "file_type": "PDF",
                "file_size": 2048576,
                "file_path": "/storage/doc_1.pdf",
                "indexing_status": "INDEXED",
                "is_questionnaire": False
            }
        }
