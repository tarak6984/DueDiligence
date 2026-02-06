"""Advanced query analyzer for intelligent question understanding."""

from typing import Dict, List, Any, Optional
from enum import Enum
import re


class QueryType(Enum):
    """Types of queries the system can handle."""
    FACTUAL = "factual"  # Direct fact retrieval
    ANALYTICAL = "analytical"  # Requires analysis/comparison
    PROCEDURAL = "procedural"  # How-to or process questions
    NUMERICAL = "numerical"  # Financial/numerical data
    TEMPORAL = "temporal"  # Time-related questions
    COMPARATIVE = "comparative"  # Comparing entities
    EXPLANATORY = "explanatory"  # Why/explanation questions
    MULTI_PART = "multi_part"  # Complex multi-part questions


class QueryComplexity(Enum):
    """Complexity levels for queries."""
    SIMPLE = "simple"  # Single fact lookup
    MODERATE = "moderate"  # Requires 2-3 sources
    COMPLEX = "complex"  # Requires multi-step reasoning
    VERY_COMPLEX = "very_complex"  # Requires synthesis across many sources


class QueryAnalyzer:
    """
    Analyzes user queries to understand intent, complexity, and optimal retrieval strategy.
    
    This enables the chat system to:
    1. Route queries to appropriate handlers
    2. Determine how many retrieval steps needed
    3. Extract key entities and concepts
    4. Break down complex questions into sub-questions
    """
    
    def __init__(self):
        # Patterns for query classification
        self.factual_patterns = [
            r'\bwhat is\b', r'\bwho is\b', r'\bwhere is\b', r'\bwhen (was|did|is)\b',
            r'\bdefine\b', r'\blist\b', r'\bname\b'
        ]
        
        self.analytical_patterns = [
            r'\banalyze\b', r'\bevaluate\b', r'\bassess\b', r'\bcompare\b',
            r'\bcontrast\b', r'\bdifference\b', r'\bsimilarity\b'
        ]
        
        self.procedural_patterns = [
            r'\bhow to\b', r'\bhow do\b', r'\bprocess\b', r'\bsteps\b',
            r'\bprocedure\b', r'\bmethod\b', r'\bapproach\b'
        ]
        
        self.explanatory_patterns = [
            r'\bwhy\b', r'\bexplain\b', r'\breason\b', r'\bcause\b',
            r'\bjustify\b', r'\brationale\b'
        ]
        
        self.numerical_patterns = [
            r'\bhow much\b', r'\bhow many\b', r'\bcost\b', r'\bprice\b',
            r'\brevenue\b', r'\bprofit\b', r'\bfinancial\b', r'\bnumber\b',
            r'\bpercentage\b', r'\brate\b', r'\bamount\b'
        ]
    
    def analyze(self, query: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive query analysis.
        
        Returns:
            Dict with query_type, complexity, entities, sub_questions, and retrieval_strategy
        """
        query_lower = query.lower()
        
        # Determine query type
        query_type = self._classify_query_type(query_lower)
        
        # Assess complexity
        complexity = self._assess_complexity(query, query_type)
        
        # Extract key entities and concepts
        entities = self._extract_entities(query)
        
        # Break down into sub-questions if complex
        sub_questions = self._decompose_query(query, query_type, complexity)
        
        # Determine optimal retrieval strategy
        retrieval_strategy = self._determine_retrieval_strategy(
            query_type, complexity, entities
        )
        
        # Analyze conversation context if provided
        context_analysis = self._analyze_context(query, conversation_history)
        
        return {
            "query": query,
            "query_type": query_type.value,
            "complexity": complexity.value,
            "entities": entities,
            "sub_questions": sub_questions,
            "retrieval_strategy": retrieval_strategy,
            "context_analysis": context_analysis,
            "requires_multi_step": complexity in [QueryComplexity.COMPLEX, QueryComplexity.VERY_COMPLEX],
            "estimated_chunks_needed": self._estimate_chunks_needed(complexity)
        }
    
    def _classify_query_type(self, query_lower: str) -> QueryType:
        """Classify the type of query."""
        
        # Check for multi-part (contains "and" or multiple question words)
        question_words = len(re.findall(r'\b(what|who|where|when|why|how)\b', query_lower))
        if question_words > 1 or ' and ' in query_lower:
            return QueryType.MULTI_PART
        
        # Check patterns in priority order
        if any(re.search(pattern, query_lower) for pattern in self.numerical_patterns):
            return QueryType.NUMERICAL
        
        if any(re.search(pattern, query_lower) for pattern in self.analytical_patterns):
            if 'compare' in query_lower or 'difference' in query_lower:
                return QueryType.COMPARATIVE
            return QueryType.ANALYTICAL
        
        if any(re.search(pattern, query_lower) for pattern in self.explanatory_patterns):
            return QueryType.EXPLANATORY
        
        if any(re.search(pattern, query_lower) for pattern in self.procedural_patterns):
            return QueryType.PROCEDURAL
        
        if any(re.search(pattern, query_lower) for pattern in self.factual_patterns):
            return QueryType.FACTUAL
        
        # Check for temporal indicators
        temporal_words = ['when', 'timeline', 'schedule', 'date', 'period', 'duration']
        if any(word in query_lower for word in temporal_words):
            return QueryType.TEMPORAL
        
        # Default to factual
        return QueryType.FACTUAL
    
    def _assess_complexity(self, query: str, query_type: QueryType) -> QueryComplexity:
        """Assess query complexity based on structure and type."""
        
        query_lower = query.lower()
        
        # Multi-part questions are at least moderate
        if query_type == QueryType.MULTI_PART:
            return QueryComplexity.COMPLEX
        
        # Analytical and comparative are typically moderate to complex
        if query_type in [QueryType.ANALYTICAL, QueryType.COMPARATIVE]:
            return QueryComplexity.MODERATE if len(query.split()) < 15 else QueryComplexity.COMPLEX
        
        # Count complexity indicators
        complexity_score = 0
        
        # Long questions are more complex
        word_count = len(query.split())
        if word_count > 20:
            complexity_score += 2
        elif word_count > 12:
            complexity_score += 1
        
        # Multiple clauses
        clause_indicators = [' and ', ' or ', ' but ', ' because ', ' if ', ' when ']
        complexity_score += sum(1 for indicator in clause_indicators if indicator in query_lower)
        
        # Specific complexity keywords
        complex_keywords = ['comprehensive', 'detailed', 'thorough', 'complete', 'entire', 'all']
        complexity_score += sum(1 for keyword in complex_keywords if keyword in query_lower)
        
        # Aggregation/synthesis keywords
        synthesis_keywords = ['overall', 'total', 'summary', 'synthesize', 'aggregate', 'combine']
        complexity_score += sum(2 for keyword in synthesis_keywords if keyword in query_lower)
        
        # Map score to complexity
        if complexity_score >= 5:
            return QueryComplexity.VERY_COMPLEX
        elif complexity_score >= 3:
            return QueryComplexity.COMPLEX
        elif complexity_score >= 1:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract key entities and concepts from the query."""
        
        entities = {
            "financial_terms": [],
            "temporal_references": [],
            "organizations": [],
            "metrics": [],
            "general_concepts": []
        }
        
        query_lower = query.lower()
        
        # Financial terms
        financial_terms = [
            'revenue', 'profit', 'loss', 'ebitda', 'cash flow', 'assets', 'liabilities',
            'equity', 'valuation', 'investment', 'funding', 'capital', 'debt', 'margin',
            'earnings', 'income', 'expense', 'cost', 'roi', 'irr', 'multiple'
        ]
        entities["financial_terms"] = [term for term in financial_terms if term in query_lower]
        
        # Temporal references
        temporal_refs = re.findall(r'\b(20\d{2}|Q[1-4]|quarter|year|month|fy\d{2})\b', query_lower)
        entities["temporal_references"] = list(set(temporal_refs))
        
        # Metrics (numbers with units)
        metrics = re.findall(r'\b\d+[\.,]?\d*\s?(%|million|billion|thousand|m|b|k)\b', query_lower)
        entities["metrics"] = metrics
        
        # Capitalized words (potential organization names)
        capitalized = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', query)
        entities["organizations"] = [word for word in capitalized if len(word) > 3]
        
        # Important business concepts
        business_concepts = [
            'strategy', 'risk', 'compliance', 'governance', 'management', 'operations',
            'market', 'competition', 'customer', 'product', 'service', 'team', 'technology',
            'growth', 'performance', 'due diligence', 'audit', 'valuation'
        ]
        entities["general_concepts"] = [concept for concept in business_concepts if concept in query_lower]
        
        return entities
    
    def _decompose_query(self, query: str, query_type: QueryType, complexity: QueryComplexity) -> List[str]:
        """Break down complex queries into simpler sub-questions."""
        
        sub_questions = []
        
        # Only decompose complex queries
        if complexity not in [QueryComplexity.COMPLEX, QueryComplexity.VERY_COMPLEX]:
            return sub_questions
        
        query_lower = query.lower()
        
        # Handle multi-part questions (split by 'and')
        if ' and ' in query_lower and query_type == QueryType.MULTI_PART:
            parts = query.split(' and ')
            sub_questions = [part.strip() + '?' if not part.strip().endswith('?') else part.strip() 
                           for part in parts]
            return sub_questions
        
        # Handle comparative questions
        if query_type == QueryType.COMPARATIVE:
            # Extract what's being compared
            if 'difference between' in query_lower or 'compare' in query_lower:
                sub_questions.append("What are the key characteristics of the first entity?")
                sub_questions.append("What are the key characteristics of the second entity?")
                sub_questions.append("What are the main differences?")
        
        # Handle analytical questions - break into components
        elif query_type == QueryType.ANALYTICAL:
            sub_questions.append(f"What are the relevant facts about {query_lower.split('analyze')[-1].strip()}?")
            sub_questions.append("What are the key metrics and indicators?")
            sub_questions.append("What are the implications or conclusions?")
        
        # Handle procedural questions
        elif query_type == QueryType.PROCEDURAL:
            sub_questions.append("What is the overall process?")
            sub_questions.append("What are the key steps involved?")
            sub_questions.append("What are the requirements or prerequisites?")
        
        return sub_questions
    
    def _determine_retrieval_strategy(
        self, 
        query_type: QueryType, 
        complexity: QueryComplexity,
        entities: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Determine the optimal retrieval strategy."""
        
        strategy = {
            "approach": "single_pass",  # single_pass, multi_pass, hierarchical
            "top_k_initial": 5,
            "enable_reranking": False,
            "expand_context": False,
            "cross_document": False
        }
        
        # Complex queries need multi-pass retrieval
        if complexity in [QueryComplexity.COMPLEX, QueryComplexity.VERY_COMPLEX]:
            strategy["approach"] = "multi_pass"
            strategy["top_k_initial"] = 10
            strategy["enable_reranking"] = True
            strategy["expand_context"] = True
        
        # Comparative and analytical need cross-document analysis
        if query_type in [QueryType.COMPARATIVE, QueryType.ANALYTICAL]:
            strategy["cross_document"] = True
            strategy["top_k_initial"] = 8
        
        # Numerical queries need precise retrieval
        if query_type == QueryType.NUMERICAL:
            strategy["enable_reranking"] = True
            strategy["top_k_initial"] = 7
        
        # Multi-part questions need broader retrieval
        if query_type == QueryType.MULTI_PART:
            strategy["approach"] = "hierarchical"
            strategy["top_k_initial"] = 12
        
        return strategy
    
    def _analyze_context(self, query: str, conversation_history: Optional[List[Dict]]) -> Dict[str, Any]:
        """Analyze conversational context."""
        
        context_info = {
            "has_context": False,
            "references_previous": False,
            "continuation": False,
            "relevant_history": []
        }
        
        if not conversation_history or len(conversation_history) == 0:
            return context_info
        
        context_info["has_context"] = True
        query_lower = query.lower()
        
        # Check for reference words
        reference_words = ['it', 'this', 'that', 'these', 'those', 'them', 'they', 'also', 'additionally']
        context_info["references_previous"] = any(word in query_lower.split()[:3] for word in reference_words)
        
        # Check for continuation words
        continuation_words = ['also', 'and', 'furthermore', 'moreover', 'additionally', 'what about']
        context_info["continuation"] = any(word in query_lower for word in continuation_words)
        
        # Extract relevant history (last 3 exchanges)
        recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        context_info["relevant_history"] = recent_history
        
        return context_info
    
    def _estimate_chunks_needed(self, complexity: QueryComplexity) -> int:
        """Estimate number of chunks needed based on complexity."""
        
        mapping = {
            QueryComplexity.SIMPLE: 3,
            QueryComplexity.MODERATE: 5,
            QueryComplexity.COMPLEX: 8,
            QueryComplexity.VERY_COMPLEX: 12
        }
        
        return mapping.get(complexity, 5)


# Global query analyzer instance
query_analyzer = QueryAnalyzer()
