"""Chat service for conversational queries using indexed documents."""

from typing import List, Dict, Any, Optional
from ..storage.vector_store import vector_store
from .query_analyzer import query_analyzer
from .reasoning_engine import reasoning_engine
from .context_manager import context_manager
from .llm_service import llm_service


class ChatService:
    """
    Intelligent chat service with advanced query understanding and multi-step reasoning.
    
    Key Features:
    1. Query analysis to understand intent and complexity
    2. Multi-step reasoning for complex queries
    3. Context-aware conversation handling
    4. Answer verification and self-correction
    5. Uses existing Layer 1 (answer index) and Layer 2 (citation index)
    
    Design:
    - Operates independently - does NOT create projects or persist answers
    - No conflict with questionnaire workflows
    """
    
    def __init__(self):
        self.vector_store = vector_store
        self.query_analyzer = query_analyzer
        self.reasoning_engine = reasoning_engine
        self.context_manager = context_manager
        self.llm_service = llm_service
    
    def generate_chat_response(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate an intelligent chat response using advanced query understanding.
        
        Args:
            question: User's question
            document_ids: Optional list of document IDs to search (None = all docs)
            conversation_history: Previous conversation messages for context
        
        Returns:
            Dict with answer, citations, confidence_score, relevant_chunks, and reasoning details
        """
        # Step 1: Prepare conversation context
        context_info = self.context_manager.prepare_context(
            current_query=question,
            conversation_history=conversation_history
        )
        
        # Check if clarification is needed
        if context_info.get("needs_clarification", False):
            return {
                "answer": "I need more context to answer that question accurately. Could you please provide more details or rephrase your question?",
                "citations": [],
                "confidence_score": 0.0,
                "relevant_chunks": 0,
                "needs_clarification": True
            }
        
        # Use augmented query (with resolved references)
        augmented_query = context_info.get("augmented_query", question)
        
        # Step 2: Analyze the query
        query_analysis = self.query_analyzer.analyze(
            query=augmented_query,
            conversation_history=conversation_history
        )
        
        # Step 3: Process query with reasoning engine
        reasoning_result = self.reasoning_engine.process_query(
            query=augmented_query,
            query_analysis=query_analysis,
            document_ids=document_ids,
            conversation_history=conversation_history
        )
        
        # Step 4: Verify and self-correct answer if needed
        final_answer = reasoning_result.get("final_answer", "")
        sources = reasoning_result.get("sources", [])
        
        # Extract source chunks for verification
        source_chunks = []
        if reasoning_result.get("reasoning_steps"):
            for step in reasoning_result["reasoning_steps"]:
                if step.get("step_type") == "retrieval":
                    # Get chunks from reasoning steps
                    pass  # Already included in reasoning
        
        # Perform verification if we have a substantial answer
        if final_answer and len(final_answer) > 50:
            # Get chunks for verification (search again with final answer)
            verification_chunks = self.vector_store.search_for_answer(
                query=augmented_query,
                document_ids=document_ids,
                top_k=5
            )
            
            if verification_chunks:
                verification_result = self.llm_service.verify_answer_against_sources(
                    answer=final_answer,
                    source_chunks=verification_chunks
                )
                
                # Apply self-correction if verification failed
                if not verification_result.get("is_verified", False):
                    correction_result = self.llm_service.self_correct_answer(
                        answer=final_answer,
                        verification_result=verification_result,
                        source_chunks=verification_chunks
                    )
                    
                    if correction_result.get("corrected", False):
                        final_answer = correction_result.get("answer", final_answer)
                        # Add verification metadata
                        reasoning_result["self_corrected"] = True
                        reasoning_result["correction_notes"] = correction_result.get("correction_notes", "")
        
        # Step 5: Format response
        return {
            "answer": final_answer,
            "citations": sources,
            "confidence_score": reasoning_result.get("confidence", 0.0),
            "relevant_chunks": reasoning_result.get("total_chunks_analyzed", 0),
            "reasoning_type": reasoning_result.get("reasoning_type", "simple"),
            "query_type": query_analysis.get("query_type"),
            "complexity": query_analysis.get("complexity"),
            "reasoning_steps": reasoning_result.get("reasoning_steps", []),
            "context_used": context_info.get("has_references", False),
            "needs_clarification": False
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
