"""Answer generation service."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models import Answer, AnswerStatus, Citation, Reference, DocumentScope
from ..storage.database import db
from ..storage.vector_store import vector_store
from ..utils import generate_id


class AnswerService:
    """Handle answer generation and management."""
    
    def __init__(self):
        self.db = db
        self.vector_store = vector_store
    
    def generate_answer(self, question_id: str) -> Answer:
        """Generate answer for a single question."""
        # Get question and project info
        question = self.db.get("questions", question_id)
        if not question:
            raise ValueError(f"Question not found: {question_id}")
        
        project = self.db.get("projects", question["project_id"])
        if not project:
            raise ValueError(f"Project not found: {question['project_id']}")
        
        # Get document scope
        document_ids = self._get_document_ids_for_project(project)
        
        # Search for relevant chunks
        relevant_chunks = self.vector_store.search_for_answer(
            query=question["text"],
            document_ids=document_ids,
            top_k=5
        )
        
        # Generate answer
        if not relevant_chunks:
            # No relevant information found
            answer_data = {
                "is_answerable": False,
                "ai_answer": None,
                "citations": [],
                "confidence_score": 0.0,
                "status": AnswerStatus.MISSING_DATA.value
            }
        else:
            # Generate answer from chunks
            answer_text = self._generate_answer_text(question["text"], relevant_chunks)
            citations = self._generate_citations(answer_text, relevant_chunks, document_ids)
            confidence = self._calculate_confidence(relevant_chunks)
            
            answer_data = {
                "is_answerable": True,
                "ai_answer": answer_text,
                "citations": citations,
                "confidence_score": confidence,
                "status": AnswerStatus.GENERATED.value
            }
        
        # Update answer in database
        answer_record = self.db.find_one("answers", {"question_id": question_id})
        if answer_record:
            answer_data["updated_at"] = datetime.utcnow().isoformat()
            self.db.update("answers", answer_record["id"], answer_data)
            updated = self.db.get("answers", answer_record["id"])
            
            # Update project answered count
            self._update_project_answered_count(project["id"])
            
            return Answer(**updated)
        
        raise ValueError(f"Answer record not found for question: {question_id}")
    
    def generate_all_answers(self, project_id: str) -> Dict[str, Any]:
        """Generate answers for all questions in a project."""
        from ..models import ProjectStatus
        
        # Update project status
        self.db.update("projects", project_id, {
            "status": ProjectStatus.GENERATING.value,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        # Get all questions
        questions = self.db.find("questions", {"project_id": project_id})
        
        generated_count = 0
        failed_count = 0
        
        for question in questions:
            try:
                self.generate_answer(question["id"])
                generated_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to generate answer for question {question['id']}: {e}")
        
        # Update project status to READY
        self.db.update("projects", project_id, {
            "status": ProjectStatus.READY.value,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return {
            "project_id": project_id,
            "total_questions": len(questions),
            "generated": generated_count,
            "failed": failed_count
        }
    
    def update_answer(self, answer_id: str, status: Optional[AnswerStatus] = None,
                     manual_answer: Optional[str] = None,
                     review_notes: Optional[str] = None) -> Answer:
        """Update answer with manual edits or status change."""
        answer = self.db.get("answers", answer_id)
        if not answer:
            raise ValueError(f"Answer not found: {answer_id}")
        
        updates = {
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if status:
            updates["status"] = status.value
        
        if manual_answer is not None:
            updates["manual_answer"] = manual_answer
            updates["status"] = AnswerStatus.MANUAL_UPDATED.value
        
        if review_notes is not None:
            updates["review_notes"] = review_notes
        
        self.db.update("answers", answer_id, updates)
        updated = self.db.get("answers", answer_id)
        
        return Answer(**updated)
    
    def get_answer(self, answer_id: str) -> Optional[Answer]:
        """Get answer by ID."""
        answer_data = self.db.get("answers", answer_id)
        return Answer(**answer_data) if answer_data else None
    
    def get_answers_for_project(self, project_id: str) -> List[Answer]:
        """Get all answers for a project."""
        answers_data = self.db.find("answers", {"project_id": project_id})
        return [Answer(**a) for a in answers_data]
    
    def _get_document_ids_for_project(self, project: Dict[str, Any]) -> Optional[List[str]]:
        """Get document IDs based on project scope."""
        if project["document_scope"] == DocumentScope.ALL_DOCS.value:
            # Get all non-questionnaire documents
            docs = self.db.find("documents", {"is_questionnaire": False})
            return [d["id"] for d in docs]
        else:
            return project.get("selected_document_ids", [])
    
    def _generate_answer_text(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """Generate answer text from relevant chunks."""
        # For demo: simple concatenation with context
        # In production: use LLM to synthesize answer
        
        context_texts = [chunk["text"][:200] for chunk in chunks[:3]]
        answer = f"Based on the available documentation: {' '.join(context_texts)}"
        
        return answer
    
    def _generate_citations(self, answer_text: str, chunks: List[Dict[str, Any]], 
                          document_ids: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Generate citations for the answer."""
        citations = []
        
        # Find citation chunks for each relevant passage
        for chunk in chunks[:3]:  # Top 3 chunks
            citation_chunks = self.vector_store.search_for_citations(
                text=chunk["text"],
                document_ids=document_ids,
                top_k=2
            )
            
            if citation_chunks:
                references = []
                for cite_chunk in citation_chunks:
                    doc = self.db.get("documents", cite_chunk["document_id"])
                    if doc:
                        references.append({
                            "document_id": doc["id"],
                            "document_name": doc["name"],
                            "chunk_id": cite_chunk["chunk_id"],
                            "page_number": cite_chunk.get("page_number"),
                            "bounding_box": cite_chunk.get("bounding_box"),
                            "text": cite_chunk["text"][:200]
                        })
                
                if references:
                    citations.append({
                        "text": chunk["text"][:150],
                        "references": references
                    })
        
        return citations
    
    def _calculate_confidence(self, chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on chunk relevance."""
        if not chunks:
            return 0.0
        
        # Simple average of top chunk scores
        scores = [chunk.get("score", 0.0) for chunk in chunks[:3]]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _update_project_answered_count(self, project_id: str):
        """Update the answered questions count for a project."""
        from ..models import AnswerStatus
        
        answers = self.db.find("answers", {"project_id": project_id})
        answered = sum(1 for a in answers if a["status"] != AnswerStatus.PENDING.value)
        
        self.db.update("projects", project_id, {
            "answered_questions": answered,
            "updated_at": datetime.utcnow().isoformat()
        })


# Global service instance
answer_service = AnswerService()
