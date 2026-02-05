"""Chat API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    document_ids: Optional[List[str]] = None  # Optional document scope
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str
    citations: List[dict]
    confidence_score: float
    relevant_chunks: int


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question using the indexed document corpus.
    
    Uses the same indexing infrastructure as questionnaire answers.
    Returns answer with citations and confidence score.
    
    Note: Chat operates independently from questionnaire projects to avoid conflicts.
    """
    try:
        result = chat_service.generate_chat_response(
            question=request.message,
            document_ids=request.document_ids,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            answer=result["answer"],
            citations=result["citations"],
            confidence_score=result["confidence_score"],
            relevant_chunks=result["relevant_chunks"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def chat_health():
    """Check if chat service is available."""
    return {"status": "available", "message": "Chat service is ready"}
