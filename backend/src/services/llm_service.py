"""LLM service for answer generation using Grok API."""

from typing import List, Dict, Any, Optional
import requests
from ..config import config


class LLMService:
    """Service for interacting with Grok LLM."""
    
    def __init__(self):
        self.api_key = config.GROK_API_KEY
        self.api_base = config.GROK_API_BASE
        self.model = config.GROK_MODEL
        self.temperature = config.TEMPERATURE
        self.max_tokens = config.MAX_TOKENS
    
    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer using Grok API with context chunks."""
        
        if not config.has_grok_api():
            # Fallback to enhanced simulated generation
            return self._generate_simulated_answer(question, context_chunks)
        
        try:
            # Build context from chunks
            context = self._build_context(context_chunks)
            
            # Create prompt
            prompt = self._create_prompt(question, context)
            
            # Call Grok API
            response = self._call_grok_api(prompt)
            
            return {
                "answer": response["answer"],
                "model": self.model,
                "success": True
            }
            
        except Exception as e:
            print(f"Grok API error: {e}")
            # Fallback to simulated
            return self._generate_simulated_answer(question, context_chunks)
    
    def _call_grok_api(self, prompt: str) -> Dict[str, Any]:
        """Make API call to Grok."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert analyst helping with due diligence questionnaires. Provide accurate, concise answers based on the provided context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        return {
            "answer": data["choices"][0]["message"]["content"],
            "usage": data.get("usage", {})
        }
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create a prompt for the LLM."""
        
        return f"""Based on the following context from due diligence documents, please answer the question accurately and concisely.

Context:
{context}

Question: {question}

Instructions:
1. Provide a direct, factual answer based only on the information in the context
2. If the context doesn't contain enough information, state that clearly
3. Be concise but thorough
4. Use professional language appropriate for due diligence

Answer:"""
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from chunks."""
        
        context_parts = []
        for i, chunk in enumerate(chunks[:5], 1):  # Top 5 chunks
            text = chunk.get("text", "")
            doc_name = chunk.get("metadata", {}).get("source", "Unknown")
            context_parts.append(f"[Source {i}: {doc_name}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _generate_simulated_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced simulated answer generation (fallback when no API key)."""
        
        if not context_chunks:
            return {
                "answer": "Based on the available documentation, I cannot provide a specific answer to this question as no relevant information was found.",
                "model": "simulated",
                "success": False
            }
        
        # Extract key information
        combined_text = " ".join([chunk.get("text", "")[:300] for chunk in context_chunks[:3]])
        
        # Create structured answer
        answer = f"Based on the available documentation: {combined_text[:500]}"
        
        # Add analysis based on question type
        question_lower = question.lower()
        
        if "what" in question_lower or "describe" in question_lower:
            answer += " The documents indicate relevant details about this topic."
        elif "how" in question_lower or "process" in question_lower:
            answer += " The process outlined in the documentation suggests a structured approach."
        elif "who" in question_lower or "team" in question_lower:
            answer += " The organizational structure as described shows key personnel involved."
        elif "when" in question_lower or "timeline" in question_lower:
            answer += " The timeline referenced in the materials provides specific dates and milestones."
        
        return {
            "answer": answer,
            "model": "simulated-enhanced",
            "success": True
        }
    
    def calculate_enhanced_confidence(self, chunks: List[Dict[str, Any]], answer: str) -> float:
        """Calculate enhanced confidence score."""
        
        if not chunks:
            return 0.0
        
        # Base score from chunk relevance
        avg_score = sum(chunk.get("score", 0.0) for chunk in chunks[:3]) / min(len(chunks), 3)
        
        # Boost if we have multiple sources
        source_boost = min(len(chunks) * 0.05, 0.2)
        
        # Boost if answer is substantial
        length_boost = 0.1 if len(answer) > 200 else 0.0
        
        # Penalize if using simulated model
        model_penalty = 0.1 if not config.has_grok_api() else 0.0
        
        final_score = min(avg_score + source_boost + length_boost - model_penalty, 1.0)
        
        return max(final_score, 0.0)
    
    def verify_answer_against_sources(
        self, 
        answer: str, 
        source_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify answer claims against source chunks for self-correction.
        
        Returns verification result with supported/unsupported claims.
        """
        
        if not answer or not source_chunks:
            return {
                "is_verified": False,
                "verification_score": 0.0,
                "supported_claims": 0,
                "total_claims": 0,
                "issues": ["Insufficient information for verification"]
            }
        
        # Split answer into claims (sentences)
        claims = [s.strip() for s in answer.split('.') if s.strip()]
        total_claims = len(claims)
        
        supported_claims = 0
        unsupported_claims = []
        issues = []
        
        # Check each claim against sources
        for claim in claims:
            claim_lower = claim.lower()
            claim_words = set(claim_lower.split())
            
            # Skip very short claims
            if len(claim_words) < 3:
                continue
            
            # Check if claim is supported by any chunk
            is_supported = False
            max_support_score = 0.0
            
            for chunk in source_chunks:
                chunk_text = chunk.get("text", "").lower()
                chunk_words = set(chunk_text.split())
                
                # Calculate support score
                overlap = len(claim_words & chunk_words)
                support_score = overlap / len(claim_words) if claim_words else 0.0
                
                # Check for exact phrase match (strong support)
                if claim_lower in chunk_text:
                    support_score = 1.0
                
                max_support_score = max(max_support_score, support_score)
                
                # Claim is supported if > 40% word overlap
                if support_score >= 0.4:
                    is_supported = True
                    break
            
            if is_supported:
                supported_claims += 1
            else:
                unsupported_claims.append({
                    "claim": claim,
                    "support_score": max_support_score
                })
        
        # Calculate verification score
        verification_score = supported_claims / total_claims if total_claims > 0 else 0.0
        
        # Determine if answer is verified
        is_verified = verification_score >= 0.6  # 60% threshold
        
        # Add issues for unsupported claims
        if unsupported_claims:
            for uc in unsupported_claims[:3]:  # Top 3 issues
                issues.append(f"Potentially unsupported claim: '{uc['claim'][:100]}...'")
        
        return {
            "is_verified": is_verified,
            "verification_score": round(verification_score, 2),
            "supported_claims": supported_claims,
            "total_claims": total_claims,
            "unsupported_claims": unsupported_claims,
            "issues": issues
        }
    
    def self_correct_answer(
        self,
        answer: str,
        verification_result: Dict[str, Any],
        source_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply self-correction to improve answer based on verification results.
        
        Returns corrected answer or original if verification passed.
        """
        
        # If answer is well-verified, return as is
        if verification_result.get("is_verified", False):
            return {
                "answer": answer,
                "corrected": False,
                "correction_notes": "Answer verified against sources"
            }
        
        # If answer has issues, attempt correction
        unsupported_claims = verification_result.get("unsupported_claims", [])
        
        if not unsupported_claims:
            return {
                "answer": answer,
                "corrected": False,
                "correction_notes": "No specific issues identified"
            }
        
        # Remove unsupported claims with very low support scores
        claims_to_keep = []
        claims_removed = []
        
        for sentence in answer.split('.'):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if this is an unsupported claim
            is_unsupported = any(
                uc["claim"].strip() == sentence and uc["support_score"] < 0.2
                for uc in unsupported_claims
            )
            
            if not is_unsupported:
                claims_to_keep.append(sentence)
            else:
                claims_removed.append(sentence[:50])
        
        # Reconstruct answer
        corrected_answer = '. '.join(claims_to_keep)
        if corrected_answer and not corrected_answer.endswith('.'):
            corrected_answer += '.'
        
        # Add disclaimer if significant corrections made
        if len(claims_removed) > 0:
            corrected_answer += " [Note: Some claims could not be fully verified against the source documents.]"
        
        return {
            "answer": corrected_answer if corrected_answer else answer,
            "corrected": len(claims_removed) > 0,
            "correction_notes": f"Removed {len(claims_removed)} unsupported claim(s)",
            "claims_removed": claims_removed
        }


# Global LLM service instance
llm_service = LLMService()
