"""Project management service."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from ..models import Project, ProjectStatus, DocumentScope, Question, Section
from ..storage.database import db
from ..utils import generate_id
from ..indexing.document_parser import document_parser


class ProjectService:
    """Handle project lifecycle operations."""
    
    def __init__(self):
        self.db = db
        self.parser = document_parser
    
    def create_project(self, name: str, questionnaire_id: str, 
                      document_scope: DocumentScope,
                      selected_document_ids: Optional[List[str]] = None) -> Project:
        """Create a new questionnaire project."""
        project_id = generate_id("proj")
        
        # Get questionnaire document
        questionnaire_doc = self.db.get("documents", questionnaire_id)
        if not questionnaire_doc:
            raise ValueError(f"Questionnaire document not found: {questionnaire_id}")
        
        if not questionnaire_doc.get("is_questionnaire"):
            raise ValueError(f"Document {questionnaire_id} is not marked as a questionnaire")
        
        # Parse questionnaire to extract structure
        file_path = questionnaire_doc["file_path"]
        parsed = self.parser.parse_questionnaire(file_path)
        
        # Create project
        project_data = {
            "id": project_id,
            "name": name,
            "questionnaire_id": questionnaire_id,
            "document_scope": document_scope.value,
            "selected_document_ids": selected_document_ids or [],
            "status": ProjectStatus.CREATING.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_questions": parsed["total_questions"],
            "answered_questions": 0
        }
        
        self.db.insert("projects", project_id, project_data)
        
        # Create sections and questions
        self._create_sections_and_questions(project_id, parsed["sections"])
        
        # Update project status to READY
        self.db.update("projects", project_id, {
            "status": ProjectStatus.READY.value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        
        project_data["status"] = ProjectStatus.READY.value
        return Project(**project_data)
    
    def _create_sections_and_questions(self, project_id: str, sections_data: List[Dict[str, Any]]):
        """Create sections and questions for a project."""
        from ..models import AnswerStatus
        
        for section_data in sections_data:
            section_id = generate_id("sec")
            
            section = {
                "id": section_id,
                "project_id": project_id,
                "title": section_data["title"],
                "order": section_data["order"]
            }
            self.db.insert("sections", section_id, section)
            
            # Create questions
            for question_data in section_data["questions"]:
                question_id = generate_id("q")
                
                question = {
                    "id": question_id,
                    "project_id": project_id,
                    "section_id": section_id,
                    "text": question_data["text"],
                    "order": question_data["order"],
                    "context": question_data.get("context")
                }
                self.db.insert("questions", question_id, question)
                
                # Create pending answer
                answer_id = generate_id("ans")
                answer = {
                    "id": answer_id,
                    "question_id": question_id,
                    "project_id": project_id,
                    "status": AnswerStatus.PENDING.value,
                    "is_answerable": False,
                    "citations": [],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                self.db.insert("answers", answer_id, answer)
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        project_data = self.db.get("projects", project_id)
        return Project(**project_data) if project_data else None
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects."""
        projects_data = self.db.find("projects")
        return [Project(**p) for p in projects_data]
    
    def update_project(self, project_id: str, document_scope: Optional[DocumentScope] = None,
                      selected_document_ids: Optional[List[str]] = None) -> Project:
        """Update project configuration."""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        updates = {
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if document_scope:
            updates["document_scope"] = document_scope.value
        
        if selected_document_ids is not None:
            updates["selected_document_ids"] = selected_document_ids
        
        # Configuration change triggers regeneration
        if document_scope or selected_document_ids is not None:
            updates["status"] = ProjectStatus.OUTDATED.value
        
        self.db.update("projects", project_id, updates)
        
        updated_data = self.db.get("projects", project_id)
        return Project(**updated_data)
    
    def get_project_sections(self, project_id: str) -> List[Section]:
        """Get all sections for a project."""
        sections_data = self.db.find("sections", {"project_id": project_id})
        sections_data.sort(key=lambda s: s["order"])
        
        sections = []
        for section_data in sections_data:
            questions_data = self.db.find("questions", {
                "project_id": project_id,
                "section_id": section_data["id"]
            })
            questions_data.sort(key=lambda q: q["order"])
            
            section_data["questions"] = [Question(**q) for q in questions_data]
            sections.append(Section(**section_data))
        
        return sections
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get detailed project status."""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        answers = self.db.find("answers", {"project_id": project_id})
        
        status_counts = {}
        for answer in answers:
            status = answer["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "project_id": project_id,
            "status": project.status,
            "total_questions": project.total_questions,
            "answered_questions": project.answered_questions,
            "status_breakdown": status_counts
        }
    
    def delete_project(self, project_id: str) -> None:
        """Delete a project and all its associated data (sections, questions, answers)."""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        # Delete all answers for this project
        answers = self.db.find("answers", {"project_id": project_id})
        for answer in answers:
            self.db.delete("answers", answer["id"])
        
        # Delete all questions for this project
        questions = self.db.find("questions", {"project_id": project_id})
        for question in questions:
            self.db.delete("questions", question["id"])
        
        # Delete all sections for this project
        sections = self.db.find("sections", {"project_id": project_id})
        for section in sections:
            self.db.delete("sections", section["id"])
        
        # Delete the project itself
        self.db.delete("projects", project_id)


# Global service instance
project_service = ProjectService()
