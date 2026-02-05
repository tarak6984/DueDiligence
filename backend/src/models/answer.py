"""Answer and citation data models."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class AnswerStatus(str, Enum):
    """Status of an answer."""
    PENDING = "PENDING"
    GENERATED = "GENERATED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    MANUAL_UPDATED = "MANUAL_UPDATED"
    MISSING_DATA = "MISSING_DATA"


class Reference(BaseModel):
    """A reference to a document chunk."""
    document_id: str = Field(..., description="Document ID")
    document_name: str = Field(..., description="Document name")
    chunk_id: str = Field(..., description="Chunk ID")
    page_number: Optional[int] = Field(default=None, description="Page number in document")
    bounding_box: Optional[dict] = Field(default=None, description="Bounding box coordinates")
    text: str = Field(..., description="Referenced text content")


class Citation(BaseModel):
    """A citation linking answer text to source references."""
    text: str = Field(..., description="Cited text from answer")
    references: List[Reference] = Field(..., description="Source references for this citation")


class Answer(BaseModel):
    """Answer to a question with citations and confidence."""
    id: str = Field(..., description="Unique answer identifier")
    question_id: str = Field(..., description="Parent question ID")
    project_id: str = Field(..., description="Parent project ID")
    status: AnswerStatus = Field(default=AnswerStatus.PENDING)
    
    # AI-generated fields
    is_answerable: bool = Field(default=False, description="Whether the question can be answered")
    ai_answer: Optional[str] = Field(default=None, description="AI-generated answer text")
    citations: List[Citation] = Field(default_factory=list, description="Citations with references")
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score (0-1)")
    
    # Manual override fields
    manual_answer: Optional[str] = Field(default=None, description="Manually entered/edited answer")
    review_notes: Optional[str] = Field(default=None, description="Reviewer notes")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ans_1",
                "question_id": "q_1",
                "project_id": "proj_123",
                "status": "GENERATED",
                "is_answerable": True,
                "ai_answer": "The fund focuses on growth equity investments...",
                "confidence_score": 0.87,
                "citations": []
            }
        }
