"""Project API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ..models import Project, ProjectStatus, DocumentScope, Section
from ..services.project_service import project_service
from ..workers.request_tracker import request_tracker

router = APIRouter(prefix="/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    """Request to create a new project."""
    name: str = Field(..., description="Project name")
    questionnaire_id: str = Field(..., description="Questionnaire document ID")
    document_scope: DocumentScope = Field(..., description="Document scope")
    selected_document_ids: Optional[List[str]] = Field(default=None)


class UpdateProjectRequest(BaseModel):
    """Request to update a project."""
    document_scope: Optional[DocumentScope] = Field(default=None)
    selected_document_ids: Optional[List[str]] = Field(default=None)


@router.post("/create-project-async")
async def create_project_async(request: CreateProjectRequest):
    """Create a new questionnaire project asynchronously."""
    try:
        # Create async request tracker
        async_request = request_tracker.create_request("create_project")
        
        # Execute project creation in background
        request_tracker.execute_async(
            async_request.id,
            project_service.create_project,
            request.name,
            request.questionnaire_id,
            request.document_scope,
            request.selected_document_ids
        )
        
        return {
            "request_id": async_request.id,
            "status": "pending",
            "message": "Project creation initiated"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get-project-info/{project_id}")
async def get_project_info(project_id: str):
    """Get detailed project information including sections and questions."""
    try:
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        sections = project_service.get_project_sections(project_id)
        
        return {
            "project": project.dict(),
            "sections": [s.dict() for s in sections]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-project-status/{project_id}")
async def get_project_status(project_id: str):
    """Get project status and progress."""
    try:
        status = project_service.get_project_status(project_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_projects():
    """Get all projects."""
    try:
        projects = project_service.get_all_projects()
        return {
            "projects": [p.dict() for p in projects],
            "total": len(projects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-project-async/{project_id}")
async def update_project_async(project_id: str, request: UpdateProjectRequest):
    """Update project configuration asynchronously."""
    try:
        # Create async request tracker
        async_request = request_tracker.create_request("update_project")
        
        # Execute update in background
        request_tracker.execute_async(
            async_request.id,
            project_service.update_project,
            project_id,
            request.document_scope,
            request.selected_document_ids
        )
        
        return {
            "request_id": async_request.id,
            "status": "pending",
            "message": "Project update initiated"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
