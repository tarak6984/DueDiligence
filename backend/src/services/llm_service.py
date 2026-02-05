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


# Global LLM service instance
llm_service = LLMService()
