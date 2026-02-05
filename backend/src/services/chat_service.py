"""Chat service for conversational queries using indexed documents."""

from typing import List, Dict, Any, Optional
from ..storage.vector_store import vector_store


class ChatService:
    """
    Chat service that uses the same indexed document corpus as questionnaires.
    
    Key Design Decisions:
    1. Uses existing Layer 1 (answer index) for retrieval
    2. Uses existing Layer 2 (citation index) for precise references
    3. Operates independently - does NOT create projects or persist answers
    4. No conflict with questionnaire workflows
    """
    
    def __init__(self):
        self.vector_store = vector_store
    
    def generate_chat_response(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a chat response using indexed documents.
        
        Args:
            question: User's question
            document_ids: Optional list of document IDs to search (None = all docs)
            conversation_history: Previous conversation messages for context
        
        Returns:
            Dict with answer, citations, confidence_score, relevant_chunks
        """
        # Step 1: Search Layer 1 (answer index) for relevant chunks
        answer_results = self.vector_store.search_for_answer(
            query=question,
            document_ids=document_ids,
            top_k=5
        )
        
        if not answer_results:
            return {
                "answer": "I don't have enough information in the indexed documents to answer this question.",
                "citations": [],
                "confidence_score": 0.0,
                "relevant_chunks": 0
            }
        
        # Step 2: Generate answer from top chunks
        answer_text = self._synthesize_answer(answer_results, question)
        
        # Step 3: Search Layer 2 (citation index) for precise references
        citation_results = self.vector_store.search_for_citations(
            text=answer_text,
            document_ids=document_ids,
            top_k=10
        )
        
        # Step 4: Build citations
        citations = self._build_citations(citation_results)
        
        # Step 5: Calculate confidence
        confidence = self._calculate_confidence(answer_results)
        
        return {
            "answer": answer_text,
            "citations": citations,
            "confidence_score": confidence,
            "relevant_chunks": len(answer_results)
        }
    
    def _synthesize_answer(self, chunks: List[Dict], question: str) -> str:
        """
        Synthesize answer from retrieved chunks.
        
        In demo implementation: concatenate top chunks.
        In production: use LLM to generate coherent response.
        """
        # Take top 3 most relevant chunks
        top_chunks = chunks[:3]
        texts = [chunk["text"] for chunk in top_chunks]
        
        # Simple concatenation with ellipsis
        answer = " ... ".join(texts)
        
        # Truncate to reasonable length
        max_length = 500
        if len(answer) > max_length:
            answer = answer[:max_length] + "..."
        
        return answer
    
    def _build_citations(self, citation_chunks: List[Dict]) -> List[Dict]:
        """Build citation references from chunks."""
        citations = []
        seen_chunks = set()
        
        for chunk in citation_chunks:
            chunk_id = chunk["chunk_id"]
            if chunk_id in seen_chunks:
                continue
            
            seen_chunks.add(chunk_id)
            
            citations.append({
                "document_id": chunk["document_id"],
                "document_name": chunk["document_name"],
                "chunk_id": chunk_id,
                "page_number": chunk.get("page_number"),
                "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"]
            })
        
        return citations[:5]  # Return top 5 citations
    
    def _calculate_confidence(self, chunks: List[Dict]) -> float:
        """
        Calculate confidence score based on chunk relevance.
        
        Higher scores when:
        - Multiple relevant chunks found
        - High similarity scores
        """
        if not chunks:
            return 0.0
        
        # Average the relevance scores
        scores = [chunk.get("score", 0.5) for chunk in chunks]
        avg_score = sum(scores) / len(scores)
        
        # Boost confidence if multiple chunks agree
        chunk_bonus = min(len(chunks) * 0.05, 0.2)
        
        confidence = min(avg_score + chunk_bonus, 1.0)
        return round(confidence, 2)


# Global service instance
chat_service = ChatService()
