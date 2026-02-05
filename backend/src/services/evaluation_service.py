"""Evaluation service for comparing AI vs human answers."""

from typing import Dict, Any, List
from datetime import datetime, timezone
from ..models import EvaluationResult
from ..storage.database import db
from ..utils import generate_id


class EvaluationService:
    """Handle answer evaluation and comparison."""
    
    def __init__(self):
        self.db = db
    
    def evaluate_answer(self, question_id: str, human_answer: str) -> EvaluationResult:
        """Evaluate AI answer against human ground truth."""
        # Get the answer
        answer = self.db.find_one("answers", {"question_id": question_id})
        if not answer:
            raise ValueError(f"Answer not found for question: {question_id}")
        
        ai_answer = answer.get("ai_answer") or answer.get("manual_answer", "")
        if not ai_answer:
            raise ValueError(f"No answer available for question: {question_id}")
        
        # Calculate similarity metrics
        semantic_sim = self._calculate_semantic_similarity(ai_answer, human_answer)
        keyword_overlap = self._calculate_keyword_overlap(ai_answer, human_answer)
        
        # Overall similarity (weighted average)
        similarity_score = (semantic_sim * 0.6) + (keyword_overlap * 0.4)
        
        # Generate explanation
        explanation = self._generate_explanation(ai_answer, human_answer, 
                                                semantic_sim, keyword_overlap)
        
        # Save evaluation result
        eval_id = generate_id("eval")
        eval_data = {
            "id": eval_id,
            "question_id": question_id,
            "project_id": answer["project_id"],
            "ai_answer": ai_answer,
            "human_answer": human_answer,
            "similarity_score": similarity_score,
            "semantic_similarity": semantic_sim,
            "keyword_overlap": keyword_overlap,
            "explanation": explanation,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.db.insert("evaluations", eval_id, eval_data)
        
        return EvaluationResult(**eval_data)
    
    def evaluate_project(self, project_id: str, human_answers: Dict[str, str]) -> List[EvaluationResult]:
        """Evaluate all answers in a project against human ground truth.
        
        Args:
            project_id: Project ID
            human_answers: Dict mapping question_id to human answer text
        """
        results = []
        
        for question_id, human_answer in human_answers.items():
            try:
                result = self.evaluate_answer(question_id, human_answer)
                results.append(result)
            except Exception as e:
                print(f"Failed to evaluate question {question_id}: {e}")
        
        return results
    
    def get_evaluation_report(self, project_id: str) -> Dict[str, Any]:
        """Get evaluation report for a project."""
        evaluations = self.db.find("evaluations", {"project_id": project_id})
        
        if not evaluations:
            return {
                "project_id": project_id,
                "total_evaluations": 0,
                "average_similarity": 0.0,
                "evaluations": []
            }
        
        # Calculate statistics
        total = len(evaluations)
        avg_similarity = sum(e["similarity_score"] for e in evaluations) / total
        avg_semantic = sum(e["semantic_similarity"] for e in evaluations) / total
        avg_keyword = sum(e["keyword_overlap"] for e in evaluations) / total
        
        # Group by similarity ranges
        high_similarity = sum(1 for e in evaluations if e["similarity_score"] >= 0.8)
        medium_similarity = sum(1 for e in evaluations if 0.5 <= e["similarity_score"] < 0.8)
        low_similarity = sum(1 for e in evaluations if e["similarity_score"] < 0.5)
        
        return {
            "project_id": project_id,
            "total_evaluations": total,
            "average_similarity": avg_similarity,
            "average_semantic_similarity": avg_semantic,
            "average_keyword_overlap": avg_keyword,
            "high_similarity_count": high_similarity,
            "medium_similarity_count": medium_similarity,
            "low_similarity_count": low_similarity,
            "evaluations": [EvaluationResult(**e).dict() for e in evaluations]
        }
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        # For demo: simple word overlap with normalization
        # In production: use sentence transformers or similar
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_keyword_overlap(self, text1: str, text2: str) -> float:
        """Calculate keyword overlap between two texts."""
        # Extract important words (length > 3, not common)
        common_words = {'the', 'and', 'or', 'but', 'with', 'for', 'from', 'this', 'that'}
        
        words1 = {w.lower() for w in text1.split() if len(w) > 3 and w.lower() not in common_words}
        words2 = {w.lower() for w in text2.split() if len(w) > 3 and w.lower() not in common_words}
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        min_length = min(len(words1), len(words2))
        
        return intersection / min_length if min_length > 0 else 0.0
    
    def _generate_explanation(self, ai_answer: str, human_answer: str,
                            semantic_sim: float, keyword_overlap: float) -> str:
        """Generate qualitative explanation of the comparison."""
        if semantic_sim >= 0.8:
            quality = "excellent"
            detail = "Both answers convey highly similar information and key concepts."
        elif semantic_sim >= 0.6:
            quality = "good"
            detail = "The answers share common themes but with some differences in detail or emphasis."
        elif semantic_sim >= 0.4:
            quality = "moderate"
            detail = "The answers touch on similar topics but differ significantly in content or focus."
        else:
            quality = "low"
            detail = "The answers appear to address different aspects or provide divergent information."
        
        explanation = (
            f"Similarity quality: {quality}. "
            f"{detail} "
            f"Semantic similarity: {semantic_sim:.2f}, Keyword overlap: {keyword_overlap:.2f}."
        )
        
        return explanation


# Global service instance
evaluation_service = EvaluationService()
