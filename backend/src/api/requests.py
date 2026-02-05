"""Request tracking API endpoints."""

from fastapi import APIRouter, HTTPException
from ..workers.request_tracker import request_tracker

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("/get-request-status/{request_id}")
async def get_request_status(request_id: str):
    """Get the status of an async request."""
    try:
        request = request_tracker.get_request(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        return request.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
