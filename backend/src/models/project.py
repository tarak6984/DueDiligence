"""Project data models."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectStatus(str, Enum):
    """Status of a questionnaire project."""
    CREATING = "CREATING"
    READY = "READY"
    GENERATING = "GENERATING"
    OUTDATED = "OUTDATED"
    ERROR = "ERROR"


class DocumentScope(str, Enum):
    """Document scope for a project."""
    ALL_DOCS = "ALL_DOCS"
    SELECTED_DOCS = "SELECTED_DOCS"


class Project(BaseModel):
    """Questionnaire project."""
    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    questionnaire_id: str = Field(..., description="ID of the questionnaire document")
    document_scope: DocumentScope = Field(..., description="Which documents to use for answers")
    selected_document_ids: Optional[List[str]] = Field(default=None, description="List of document IDs if scope is SELECTED_DOCS")
    status: ProjectStatus = Field(default=ProjectStatus.CREATING, description="Current project status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    total_questions: int = Field(default=0, description="Total number of questions")
    answered_questions: int = Field(default=0, description="Number of answered questions")
    error_message: Optional[str] = Field(default=None, description="Error message if status is ERROR")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "proj_123",
                "name": "Q1 2026 Due Diligence",
                "questionnaire_id": "doc_questionnaire_1",
                "document_scope": "ALL_DOCS",
                "status": "READY",
                "total_questions": 150,
                "answered_questions": 145
            }
        }
