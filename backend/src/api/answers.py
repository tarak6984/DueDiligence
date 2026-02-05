"""Answer API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from ..models import Answer, AnswerStatus
from ..services.answer_service import answer_service
from ..workers.request_tracker import request_tracker

router = APIRouter(prefix="/answers", tags=["answers"])


class UpdateAnswerRequest(BaseModel):
    """Request to update an answer."""
    status: Optional[AnswerStatus] = Field(default=None)
    manual_answer: Optional[str] = Field(default=None)
    review_notes: Optional[str] = Field(default=None)


@router.post("/generate-single-answer/{question_id}")
async def generate_single_answer(question_id: str):
    """Generate answer for a single question."""
    try:
        answer = answer_service.generate_answer(question_id)
        return answer.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-all-answers/{project_id}")
async def generate_all_answers(project_id: str):
    """Generate answers for all questions in a project."""
    try:
        # Create async request tracker
        async_request = request_tracker.create_request("generate_all_answers")
        
        # Execute generation in background
        request_tracker.execute_async(
            async_request.id,
            answer_service.generate_all_answers,
            project_id
        )
        
        return {
            "request_id": async_request.id,
            "status": "pending",
            "message": "Answer generation initiated"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-answer/{answer_id}")
async def update_answer(answer_id: str, request: UpdateAnswerRequest):
    """Update an answer with manual edits or status change."""
    try:
        answer = answer_service.update_answer(
            answer_id,
            request.status,
            request.manual_answer,
            request.review_notes
        )
        return answer.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-answer/{answer_id}")
async def get_answer(answer_id: str):
    """Get answer by ID."""
    try:
        answer = answer_service.get_answer(answer_id)
        if not answer:
            raise HTTPException(status_code=404, detail="Answer not found")
        return answer.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{project_id}")
async def list_answers(project_id: str):
    """Get all answers for a project."""
    try:
        answers = answer_service.get_answers_for_project(project_id)
        return {
            "answers": [a.dict() for a in answers],
            "total": len(answers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
