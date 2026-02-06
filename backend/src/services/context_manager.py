"""Intelligent context manager for conversation history."""

from typing import List, Dict, Any, Optional
from datetime import datetime


class ContextManager:
    """
    Manages conversation context to provide intelligent, context-aware responses.
    
    Features:
    1. Maintains conversation memory
    2. Resolves references (pronouns, "it", "that", etc.)
    3. Tracks discussed topics
    4. Provides relevant context for queries
    """
    
    def __init__(self, max_history_length: int = 20):
        self.max_history_length = max_history_length
    
    def prepare_context(
        self,
        current_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Prepare contextual information for query processing.
        
        Returns:
            Dict with augmented_query, relevant_history, and context_entities
        """
        
        if not conversation_history or len(conversation_history) == 0:
            return {
                "augmented_query": current_query,
                "relevant_history": [],
                "context_entities": [],
                "needs_clarification": False
            }
        
        # Trim history to max length
        trimmed_history = conversation_history[-self.max_history_length:]
        
        # Check if current query references previous context
        references_previous = self._check_references(current_query)
        
        # Extract entities from history
        context_entities = self._extract_context_entities(trimmed_history)
        
        # Resolve references if present
        augmented_query = current_query
        if references_previous:
            augmented_query = self._resolve_references(
                current_query, trimmed_history, context_entities
            )
        
        # Find most relevant history for context
        relevant_history = self._find_relevant_history(
            current_query, trimmed_history
        )
        
        # Check if clarification needed
        needs_clarification = self._needs_clarification(
            current_query, augmented_query, context_entities
        )
        
        return {
            "augmented_query": augmented_query,
            "relevant_history": relevant_history,
            "context_entities": context_entities,
            "needs_clarification": needs_clarification,
            "has_references": references_previous
        }
    
    def _check_references(self, query: str) -> bool:
        """Check if query contains references to previous context."""
        
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Reference pronouns and words
        reference_words = {
            'it', 'this', 'that', 'these', 'those', 'them', 'they',
            'its', 'their', 'theirs', 'he', 'she', 'his', 'her'
        }
        
        # Check if reference words appear early in query (first 3 words)
        early_words = set(query_words[:3])
        if early_words & reference_words:
            return True
        
        # Check for continuation phrases
        continuation_phrases = [
            'also', 'what about', 'how about', 'tell me more',
            'more details', 'elaborate', 'further', 'additionally'
        ]
        
        return any(phrase in query_lower for phrase in continuation_phrases)
    
    def _extract_context_entities(self, history: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Extract key entities mentioned in conversation history."""
        
        entities = []
        
        for i, exchange in enumerate(history):
            role = exchange.get("role", "")
            content = exchange.get("content", "")
            
            if role == "user":
                # Extract potential entities (capitalized words, numbers, dates)
                import re
                
                # Organizations/proper nouns
                proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', content)
                
                # Financial terms and numbers
                numbers = re.findall(r'\$?[\d,]+\.?\d*[MBK]?', content)
                
                # Dates
                dates = re.findall(r'\b\d{4}\b|Q[1-4]|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b', content)
                
                for noun in proper_nouns:
                    entities.append({
                        "text": noun,
                        "type": "proper_noun",
                        "position": i,
                        "recency": len(history) - i
                    })
                
                for num in numbers:
                    entities.append({
                        "text": num,
                        "type": "number",
                        "position": i,
                        "recency": len(history) - i
                    })
                
                for date in dates:
                    entities.append({
                        "text": date,
                        "type": "date",
                        "position": i,
                        "recency": len(history) - i
                    })
        
        # Deduplicate and sort by recency
        unique_entities = {}
        for entity in entities:
            key = entity["text"].lower()
            if key not in unique_entities or entity["recency"] < unique_entities[key]["recency"]:
                unique_entities[key] = entity
        
        return list(unique_entities.values())
    
    def _resolve_references(
        self,
        query: str,
        history: List[Dict[str, str]],
        entities: List[Dict[str, Any]]
    ) -> str:
        """Resolve references in query using conversation context."""
        
        query_lower = query.lower()
        
        # Get the most recent assistant response
        recent_responses = [
            h.get("content", "") for h in history[-3:] 
            if h.get("role") == "assistant"
        ]
        
        if not recent_responses:
            return query
        
        last_response = recent_responses[-1]
        
        # If query starts with reference word, try to determine what it refers to
        query_words = query.split()
        first_word = query_words[0].lower() if query_words else ""
        
        reference_pronouns = {'it', 'this', 'that'}
        
        if first_word in reference_pronouns:
            # Find the main subject in last response
            subject = self._extract_main_subject(last_response, entities)
            
            if subject:
                # Replace pronoun with subject
                augmented = query.replace(first_word, subject, 1)
                return augmented
        
        # Handle "also" or "additionally" - append context
        if query_lower.startswith('also') or query_lower.startswith('additionally'):
            # Find last question asked
            recent_questions = [
                h.get("content", "") for h in history[-5:]
                if h.get("role") == "user"
            ]
            
            if len(recent_questions) >= 2:
                last_question = recent_questions[-2]
                # Extract main topic
                topic = self._extract_main_subject(last_question, entities)
                if topic:
                    return f"{query} about {topic}"
        
        # Handle "what about X" - provide context from previous discussion
        if "what about" in query_lower or "how about" in query_lower:
            # This is inherently contextual, add previous topic
            recent_topics = self._extract_discussed_topics(history[-4:])
            if recent_topics:
                return f"{query} (in context of {recent_topics[0]})"
        
        return query
    
    def _extract_main_subject(self, text: str, entities: List[Dict[str, Any]]) -> Optional[str]:
        """Extract the main subject from a text."""
        
        # Look for entities that appear in this text
        text_lower = text.lower()
        
        # Prioritize proper nouns (organizations, names)
        for entity in entities:
            if entity["type"] == "proper_noun" and entity["text"].lower() in text_lower:
                return entity["text"]
        
        # Try to extract subject from first sentence
        first_sentence = text.split('.')[0]
        words = first_sentence.split()
        
        # Look for capitalized words after common verbs
        verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'shows', 'indicates']
        for i, word in enumerate(words):
            if word.lower() in verbs and i + 1 < len(words):
                # Get the next few words (potential subject)
                subject_words = words[i+1:min(i+4, len(words))]
                subject = ' '.join(subject_words)
                return subject
        
        return None
    
    def _extract_discussed_topics(self, history: List[Dict[str, str]]) -> List[str]:
        """Extract main topics discussed in conversation."""
        
        topics = []
        
        for exchange in history:
            if exchange.get("role") == "user":
                content = exchange.get("content", "")
                
                # Extract key phrases (simple noun extraction)
                import re
                # Look for patterns like "about X", "regarding X"
                about_pattern = r'(?:about|regarding|concerning|for)\s+([a-zA-Z\s]+?)(?:\?|,|\.|\s+and\s+)'
                matches = re.findall(about_pattern, content, re.IGNORECASE)
                
                topics.extend([m.strip() for m in matches])
        
        return topics[:3]  # Return top 3 recent topics
    
    def _find_relevant_history(
        self,
        query: str,
        history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Find most relevant history exchanges for current query."""
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score each history item by relevance
        scored_history = []
        
        for exchange in history:
            content = exchange.get("content", "").lower()
            content_words = set(content.split())
            
            # Calculate word overlap
            overlap = len(query_words & content_words)
            relevance_score = overlap / len(query_words) if query_words else 0
            
            if relevance_score > 0.1:  # At least 10% overlap
                scored_history.append({
                    "exchange": exchange,
                    "score": relevance_score
                })
        
        # Sort by score and return top 3
        scored_history.sort(key=lambda x: x["score"], reverse=True)
        
        return [item["exchange"] for item in scored_history[:3]]
    
    def _needs_clarification(
        self,
        original_query: str,
        augmented_query: str,
        entities: List[Dict[str, Any]]
    ) -> bool:
        """Determine if query needs clarification."""
        
        query_lower = original_query.lower()
        
        # Check if query is very vague
        vague_queries = [
            "what about it", "tell me more", "and that", "anything else",
            "what else", "more info", "details"
        ]
        
        if any(vague in query_lower for vague in vague_queries):
            # If we couldn't resolve references, clarification needed
            if original_query == augmented_query and not entities:
                return True
        
        # Check if query is too short and ambiguous
        if len(original_query.split()) <= 3 and not entities:
            # Very short queries might need clarification
            return True
        
        return False
    
    def format_context_for_llm(
        self,
        current_query: str,
        context_info: Dict[str, Any]
    ) -> str:
        """Format conversation context for LLM prompt."""
        
        relevant_history = context_info.get("relevant_history", [])
        augmented_query = context_info.get("augmented_query", current_query)
        
        if not relevant_history:
            return augmented_query
        
        # Build context string
        context_parts = ["Conversation context:"]
        
        for exchange in relevant_history:
            role = exchange.get("role", "")
            content = exchange.get("content", "")
            
            if role == "user":
                context_parts.append(f"Previous question: {content}")
            elif role == "assistant":
                # Truncate long responses
                short_content = content[:150] + "..." if len(content) > 150 else content
                context_parts.append(f"Previous answer: {short_content}")
        
        context_parts.append(f"\nCurrent question: {augmented_query}")
        
        return "\n".join(context_parts)


# Global context manager instance
context_manager = ContextManager()
