"""Async request tracking models."""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class RequestStatus(str, Enum):
    """Status of an async request."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AsyncRequest(BaseModel):
    """An asynchronous request tracker."""
    id: str = Field(..., description="Unique request identifier")
    request_type: str = Field(..., description="Type of request (create_project, index_document, etc.)")
    status: RequestStatus = Field(default=RequestStatus.PENDING)
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    result: Optional[Any] = Field(default=None, description="Result data when completed")
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "req_123",
                "request_type": "create_project",
                "status": "IN_PROGRESS",
                "progress": 45,
                "result": None
            }
        }
