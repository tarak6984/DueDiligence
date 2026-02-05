"""Evaluation data models."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class EvaluationResult(BaseModel):
    """Result of comparing AI answer to human ground truth."""
    id: str = Field(..., description="Unique evaluation identifier")
    question_id: str = Field(..., description="Question being evaluated")
    project_id: str = Field(..., description="Parent project ID")
    ai_answer: str = Field(..., description="AI-generated answer")
    human_answer: str = Field(..., description="Human ground truth answer")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Overall similarity score (0-1)")
    semantic_similarity: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score")
    keyword_overlap: float = Field(..., ge=0.0, le=1.0, description="Keyword overlap score")
    explanation: str = Field(..., description="Qualitative explanation of the comparison")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "eval_1",
                "question_id": "q_1",
                "project_id": "proj_123",
                "ai_answer": "The fund focuses on growth equity...",
                "human_answer": "Growth equity strategy targeting...",
                "similarity_score": 0.85,
                "semantic_similarity": 0.88,
                "keyword_overlap": 0.82,
                "explanation": "Both answers correctly identify the growth equity focus..."
            }
        }
