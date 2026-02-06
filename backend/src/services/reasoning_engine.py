"""Multi-step reasoning engine for complex query processing."""

from typing import List, Dict, Any, Optional
from .query_analyzer import query_analyzer, QueryComplexity, QueryType
from ..storage.vector_store import vector_store
from .llm_service import llm_service


class ReasoningStep:
    """Represents a single step in the reasoning process."""
    
    def __init__(self, step_number: int, question: str, step_type: str):
        self.step_number = step_number
        self.question = question
        self.step_type = step_type  # 'retrieval', 'synthesis', 'verification'
        self.retrieved_chunks: List[Dict] = []
        self.intermediate_answer: str = ""
        self.confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "question": self.question,
            "step_type": self.step_type,
            "chunks_used": len(self.retrieved_chunks),
            "answer": self.intermediate_answer,
            "confidence": self.confidence
        }


class ReasoningEngine:
    """
    Multi-step reasoning engine that breaks down complex questions and synthesizes answers.
    
    Key capabilities:
    1. Chain-of-thought reasoning for complex queries
    2. Sub-question decomposition and answering
    3. Information synthesis across multiple retrieval steps
    4. Self-verification and consistency checking
    """
    
    def __init__(self):
        self.vector_store = vector_store
        self.llm_service = llm_service
    
    def process_query(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        document_ids: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Process a query using multi-step reasoning if needed.
        
        Returns:
            Dict with final_answer, reasoning_steps, confidence, and sources
        """
        
        # For simple queries, use direct retrieval
        if not query_analysis.get("requires_multi_step", False):
            return self._simple_retrieval(query, query_analysis, document_ids)
        
        # For complex queries, use multi-step reasoning
        return self._multi_step_reasoning(
            query, query_analysis, document_ids, conversation_history
        )
    
    def _simple_retrieval(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Direct retrieval for simple queries."""
        
        strategy = query_analysis.get("retrieval_strategy", {})
        top_k = strategy.get("top_k_initial", 5)
        
        # Retrieve relevant chunks
        chunks = self.vector_store.search_for_answer(
            query=query,
            document_ids=document_ids,
            top_k=top_k
        )
        
        if not chunks:
            return {
                "final_answer": "I couldn't find relevant information to answer this question.",
                "reasoning_steps": [],
                "confidence": 0.0,
                "sources": [],
                "reasoning_type": "simple_retrieval"
            }
        
        # Re-rank if strategy requires it
        if strategy.get("enable_reranking", False):
            chunks = self._rerank_chunks(query, chunks)
        
        # Generate answer
        answer_result = self.llm_service.generate_answer(query, chunks)
        
        # Get citations
        citations = self._get_citations_for_chunks(chunks[:3])
        
        # Calculate confidence
        confidence = self.llm_service.calculate_enhanced_confidence(
            chunks, answer_result.get("answer", "")
        )
        
        return {
            "final_answer": answer_result.get("answer", ""),
            "reasoning_steps": [{
                "step_number": 1,
                "step_type": "retrieval",
                "chunks_used": len(chunks),
                "confidence": confidence
            }],
            "confidence": confidence,
            "sources": citations,
            "reasoning_type": "simple_retrieval"
        }
    
    def _multi_step_reasoning(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        document_ids: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Multi-step reasoning for complex queries."""
        
        reasoning_steps: List[ReasoningStep] = []
        all_chunks: List[Dict] = []
        
        # Get sub-questions from analysis
        sub_questions = query_analysis.get("sub_questions", [])
        
        if not sub_questions:
            # If no sub-questions, create retrieval steps based on complexity
            sub_questions = self._generate_retrieval_steps(query, query_analysis)
        
        # Step 1-N: Answer each sub-question
        for i, sub_q in enumerate(sub_questions, 1):
            step = ReasoningStep(i, sub_q, "retrieval")
            
            # Retrieve for this sub-question
            chunks = self.vector_store.search_for_answer(
                query=sub_q,
                document_ids=document_ids,
                top_k=5
            )
            
            if chunks:
                step.retrieved_chunks = chunks
                all_chunks.extend(chunks)
                
                # Generate intermediate answer
                answer_result = self.llm_service.generate_answer(sub_q, chunks)
                step.intermediate_answer = answer_result.get("answer", "")
                step.confidence = self.llm_service.calculate_enhanced_confidence(
                    chunks, step.intermediate_answer
                )
            
            reasoning_steps.append(step)
        
        # Step N+1: Synthesis - combine all intermediate answers
        synthesis_step = ReasoningStep(
            len(reasoning_steps) + 1,
            "Synthesize final answer",
            "synthesis"
        )
        
        final_answer = self._synthesize_final_answer(
            query, reasoning_steps, all_chunks
        )
        synthesis_step.intermediate_answer = final_answer
        reasoning_steps.append(synthesis_step)
        
        # Step N+2: Verification - check consistency
        verification_step = ReasoningStep(
            len(reasoning_steps) + 1,
            "Verify answer consistency",
            "verification"
        )
        
        is_consistent, verification_notes = self._verify_answer(
            query, final_answer, all_chunks
        )
        verification_step.intermediate_answer = verification_notes
        verification_step.confidence = 0.9 if is_consistent else 0.6
        reasoning_steps.append(verification_step)
        
        # Calculate overall confidence
        step_confidences = [s.confidence for s in reasoning_steps if s.confidence > 0]
        overall_confidence = sum(step_confidences) / len(step_confidences) if step_confidences else 0.5
        
        # Get top citations
        citations = self._get_citations_for_chunks(all_chunks[:5])
        
        return {
            "final_answer": final_answer,
            "reasoning_steps": [step.to_dict() for step in reasoning_steps],
            "confidence": round(overall_confidence, 2),
            "sources": citations,
            "reasoning_type": "multi_step",
            "total_chunks_analyzed": len(all_chunks)
        }
    
    def _generate_retrieval_steps(self, query: str, query_analysis: Dict[str, Any]) -> List[str]:
        """Generate retrieval steps for queries without sub-questions."""
        
        query_type = query_analysis.get("query_type")
        entities = query_analysis.get("entities", {})
        
        steps = []
        
        # Add entity-specific retrieval steps
        if entities.get("financial_terms"):
            steps.append(f"What financial information is available about {', '.join(entities['financial_terms'][:2])}?")
        
        if entities.get("organizations"):
            steps.append(f"What information is available about {entities['organizations'][0]}?")
        
        # Add query-type specific steps
        if query_type == "analytical":
            steps.append("What are the key facts and data points?")
            steps.append("What are the trends and patterns?")
            steps.append("What are the implications?")
        elif query_type == "comparative":
            steps.append("What are the characteristics of the first entity?")
            steps.append("What are the characteristics of the second entity?")
        else:
            # Generic broad retrieval
            steps.append(f"General information: {query}")
            steps.append(f"Detailed context: {query}")
        
        return steps[:4]  # Limit to 4 steps
    
    def _synthesize_final_answer(
        self,
        original_query: str,
        reasoning_steps: List[ReasoningStep],
        all_chunks: List[Dict]
    ) -> str:
        """Synthesize final answer from all reasoning steps."""
        
        # Collect all intermediate answers
        intermediate_answers = [
            step.intermediate_answer 
            for step in reasoning_steps 
            if step.step_type == "retrieval" and step.intermediate_answer
        ]
        
        if not intermediate_answers:
            return "Unable to generate a comprehensive answer based on available information."
        
        # Create synthesis context
        synthesis_context = "\n\n".join([
            f"Finding {i+1}: {answer}" 
            for i, answer in enumerate(intermediate_answers)
        ])
        
        # Use LLM to synthesize if available
        synthesis_prompt = f"""Based on the following findings, provide a comprehensive answer to: {original_query}

Findings:
{synthesis_context}

Provide a clear, well-structured answer that synthesizes these findings:"""
        
        # Create synthetic chunks for LLM
        synthetic_chunks = [{"text": synthesis_context, "metadata": {"source": "synthesis"}}]
        
        result = self.llm_service.generate_answer(original_query, synthetic_chunks)
        
        if result.get("success"):
            return result.get("answer", "")
        
        # Fallback: intelligent concatenation
        return self._intelligent_concatenation(intermediate_answers)
    
    def _intelligent_concatenation(self, answers: List[str]) -> str:
        """Intelligently concatenate multiple answers."""
        
        # Remove duplicates and very similar sentences
        unique_sentences = []
        seen_concepts = set()
        
        for answer in answers:
            # Split into sentences
            sentences = answer.split('. ')
            for sentence in sentences:
                # Extract key concepts (simple word extraction)
                words = set(sentence.lower().split())
                key_words = words - {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
                
                # Check if this adds new information
                if len(key_words & seen_concepts) < len(key_words) * 0.7:  # Less than 70% overlap
                    unique_sentences.append(sentence)
                    seen_concepts.update(key_words)
        
        # Reconstruct answer
        final_answer = '. '.join(unique_sentences)
        
        # Ensure proper ending
        if not final_answer.endswith('.'):
            final_answer += '.'
        
        return final_answer
    
    def _verify_answer(self, query: str, answer: str, chunks: List[Dict]) -> tuple[bool, str]:
        """Verify answer consistency with source chunks."""
        
        if not chunks or not answer:
            return False, "Insufficient information for verification"
        
        # Extract key claims from answer
        answer_sentences = answer.split('. ')
        
        # Check if answer sentences are supported by chunks
        supported_count = 0
        total_claims = len(answer_sentences)
        
        for sentence in answer_sentences:
            sentence_lower = sentence.lower()
            sentence_words = set(sentence_lower.split())
            
            # Check if any chunk supports this sentence
            for chunk in chunks[:5]:
                chunk_lower = chunk.get("text", "").lower()
                chunk_words = set(chunk_lower.split())
                
                # Calculate word overlap
                overlap = len(sentence_words & chunk_words)
                if overlap > len(sentence_words) * 0.3:  # 30% word overlap
                    supported_count += 1
                    break
        
        # Calculate verification score
        verification_ratio = supported_count / total_claims if total_claims > 0 else 0
        is_consistent = verification_ratio >= 0.6  # 60% of claims should be supported
        
        notes = f"Verified {supported_count}/{total_claims} claims against source documents. "
        if is_consistent:
            notes += "Answer is well-supported by sources."
        else:
            notes += "Answer may contain unsupported claims."
        
        return is_consistent, notes
    
    def _rerank_chunks(self, query: str, chunks: List[Dict]) -> List[Dict]:
        """Re-rank chunks using advanced relevance scoring."""
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for chunk in chunks:
            text_lower = chunk.get("text", "").lower()
            text_words = set(text_lower.split())
            
            # Calculate enhanced relevance score
            base_score = chunk.get("score", 0.0)
            
            # Boost for exact phrase matches
            phrase_boost = 0.2 if query_lower in text_lower else 0.0
            
            # Boost for high word overlap
            overlap_ratio = len(query_words & text_words) / len(query_words)
            overlap_boost = overlap_ratio * 0.15
            
            # Boost for position (earlier chunks might be more relevant)
            position_penalty = chunks.index(chunk) * 0.01
            
            # Calculate final score
            chunk["rerank_score"] = base_score + phrase_boost + overlap_boost - position_penalty
        
        # Sort by rerank score
        chunks.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        
        return chunks
    
    def _get_citations_for_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Extract citation information from chunks."""
        
        citations = []
        seen_chunks = set()
        
        for chunk in chunks:
            chunk_id = chunk.get("chunk_id", "")
            if chunk_id in seen_chunks:
                continue
            
            seen_chunks.add(chunk_id)
            
            # Get more detailed citation from citation index
            citation_chunks = self.vector_store.search_for_citations(
                text=chunk.get("text", ""),
                document_ids=[chunk.get("document_id")],
                top_k=1
            )
            
            if citation_chunks:
                cite = citation_chunks[0]
                citations.append({
                    "document_id": cite.get("document_id"),
                    "document_name": cite.get("metadata", {}).get("source", "Unknown"),
                    "chunk_id": cite.get("chunk_id"),
                    "page_number": cite.get("page_number"),
                    "text": cite.get("text", "")[:200] + "..." if len(cite.get("text", "")) > 200 else cite.get("text", ""),
                    "relevance_score": chunk.get("score", 0.0)
                })
        
        return citations[:5]  # Top 5 citations


# Global reasoning engine instance
reasoning_engine = ReasoningEngine()
