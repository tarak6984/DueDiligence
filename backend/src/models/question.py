"""Question and section data models."""

from typing import Optional, List
from pydantic import BaseModel, Field


class Question(BaseModel):
    """A single question from the questionnaire."""
    id: str = Field(..., description="Unique question identifier")
    project_id: str = Field(..., description="Parent project ID")
    section_id: str = Field(..., description="Parent section ID")
    text: str = Field(..., description="Question text")
    order: int = Field(..., description="Question order within section")
    context: Optional[str] = Field(default=None, description="Additional context or instructions")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "q_1",
                "project_id": "proj_123",
                "section_id": "sec_1",
                "text": "What is the fund's investment strategy?",
                "order": 1
            }
        }


class Section(BaseModel):
    """A section containing related questions."""
    id: str = Field(..., description="Unique section identifier")
    project_id: str = Field(..., description="Parent project ID")
    title: str = Field(..., description="Section title")
    order: int = Field(..., description="Section order within questionnaire")
    questions: List[Question] = Field(default_factory=list, description="Questions in this section")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sec_1",
                "project_id": "proj_123",
                "title": "Investment Strategy",
                "order": 1,
                "questions": []
            }
        }
