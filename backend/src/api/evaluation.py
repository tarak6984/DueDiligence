"""Evaluation API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict
from ..services.evaluation_service import evaluation_service

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


class EvaluateAnswerRequest(BaseModel):
    """Request to evaluate an answer."""
    question_id: str = Field(..., description="Question ID")
    human_answer: str = Field(..., description="Human ground truth answer")


class EvaluateProjectRequest(BaseModel):
    """Request to evaluate a project."""
    human_answers: Dict[str, str] = Field(..., description="Map of question_id to human answer")


@router.post("/evaluate-answer")
async def evaluate_answer(request: EvaluateAnswerRequest):
    """Evaluate a single answer against human ground truth."""
    try:
        result = evaluation_service.evaluate_answer(
            request.question_id,
            request.human_answer
        )
        return result.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-project/{project_id}")
async def evaluate_project(project_id: str, request: EvaluateProjectRequest):
    """Evaluate all answers in a project."""
    try:
        results = evaluation_service.evaluate_project(
            project_id,
            request.human_answers
        )
        return {
            "results": [r.dict() for r in results],
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-report/{project_id}")
async def get_evaluation_report(project_id: str):
    """Get evaluation report for a project."""
    try:
        report = evaluation_service.get_evaluation_report(project_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
