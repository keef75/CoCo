"""
Query Router: Intelligent Memory Routing System

Routes queries between Facts (perfect recall) and Simple RAG (semantic search)
based on query intent analysis.

Author: COCO Development Team
Date: October 24, 2025
Status: Phase 1 - Production
"""

from typing import Dict, List, Any, Optional


class QueryRouter:
    """Routes queries to facts or semantic memory based on intent"""

    def __init__(self, facts_memory, simple_rag):
        """
        Initialize query router

        Args:
            facts_memory: FactsMemory instance for perfect recall
            simple_rag: SimpleRAG instance for semantic search
        """
        self.facts_memory = facts_memory
        self.simple_rag = simple_rag

        # Keywords indicating need for exact/temporal facts (Personal Assistant Focus)
        self.exact_keywords = [
            # Personal assistant queries
            'who', 'what', 'when', 'where', 'which',
            'what was', 'who was', 'when was', 'where was',
            'show me', 'find', 'find the', 'show me the',
            'what email', 'what meeting', 'what appointment',
            'who did i', 'what did i', 'when did i',
            'specific', 'precisely', 'exact',
            # Technical queries (kept for backward compatibility)
            'command', 'code', 'file', 'that'
        ]

        self.temporal_keywords = [
            'yesterday', 'last week', 'earlier', 'ago',
            'recently', 'just now', 'before', 'when',
            'last time', 'previous', 'past'
        ]

        self.fact_type_keywords = {
            # Personal Assistant Fact Types (High Priority)
            'appointment': ['meeting', 'appointment', 'call', 'interview', 'event', 'conference', 'scheduled'],
            'contact': ['person', 'people', 'contact', 'email address', 'phone', 'colleague', 'friend'],
            'preference': ['prefer', 'like', 'favorite', 'want', 'love', 'hate', 'dislike', 'choice'],
            'task': ['task', 'todo', 'action item', 'reminder', 'need to', 'should', 'must'],
            'note': ['note', 'remember', 'important', 'reminder', 'don\'t forget', 'fyi'],
            'location': ['location', 'place', 'address', 'venue', 'where', 'office', 'restaurant'],
            'communication': ['email', 'message', 'text', 'chat', 'conversation', 'call', 'discussed'],
            'tool_use': ['created', 'generated', 'sent', 'uploaded', 'document', 'image', 'video'],

            # Technical Support Fact Types (Lower Priority)
            'command': ['command', 'cmd', 'shell', 'bash'],
            'code': ['code', 'function', 'script', 'snippet'],
            'file': ['file', 'path', 'directory', 'folder'],
            'url': ['url', 'link', 'website'],
            'error': ['error', 'exception', 'bug', 'issue'],
            'config': ['config', 'setting', 'configuration']
        }

    def route_query(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Route query to appropriate memory system

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            Dict with 'source' and 'results' keys
        """
        query_lower = query.lower()

        # Detect fact type from query
        fact_type = self._detect_fact_type(query_lower)

        # Check for temporal or exact needs
        needs_exact = (
            any(kw in query_lower for kw in self.exact_keywords) or
            any(kw in query_lower for kw in self.temporal_keywords) or
            fact_type is not None
        )

        if needs_exact:
            # Search facts first (perfect recall)
            facts = self.facts_memory.search_facts(
                query,
                fact_type=fact_type,
                limit=limit
            )

            if facts:
                return {
                    'source': 'facts',
                    'fact_type': fact_type,
                    'results': facts,
                    'count': len(facts)
                }

        # Fall back to semantic search
        if self.simple_rag:
            semantic_results = self.simple_rag.retrieve(query, k=limit)

            return {
                'source': 'semantic',
                'results': semantic_results,
                'count': len(semantic_results) if semantic_results else 0
            }

        # No results found
        return {
            'source': 'none',
            'results': [],
            'count': 0
        }

    def _detect_fact_type(self, query_lower: str) -> Optional[str]:
        """
        Detect fact type from query keywords

        Args:
            query_lower: Lowercased query string

        Returns:
            Fact type or None
        """
        for fact_type, keywords in self.fact_type_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return fact_type

        return None

    def get_routing_explanation(self, query: str) -> str:
        """
        Explain routing decision for transparency

        Args:
            query: Original query string

        Returns:
            Human-readable routing explanation
        """
        query_lower = query.lower()
        fact_type = self._detect_fact_type(query_lower)

        exact_matches = [kw for kw in self.exact_keywords if kw in query_lower]
        temporal_matches = [kw for kw in self.temporal_keywords if kw in query_lower]

        if fact_type:
            return f"Routed to Facts (detected type: {fact_type})"
        elif exact_matches:
            return f"Routed to Facts (exact keywords: {', '.join(exact_matches)})"
        elif temporal_matches:
            return f"Routed to Facts (temporal keywords: {', '.join(temporal_matches)})"
        else:
            return "Routed to Semantic Search (no exact/temporal indicators)"

    def get_query_confidence(self, query: str) -> float:
        """
        Calculate confidence score for whether query needs facts

        Args:
            query: User query string

        Returns:
            Confidence score (0.0-1.0) where:
            - 0.8+ = High confidence (strong factual query)
            - 0.6-0.8 = Medium confidence (likely factual)
            - 0.4-0.6 = Low confidence (ambiguous)
            - <0.4 = Very low (conceptual/semantic query)
        """
        query_lower = query.lower()
        confidence = 0.0

        # Check for exact keywords (0.4 weight)
        # These are strong indicators of factual queries
        exact_matches = [kw for kw in self.exact_keywords if kw in query_lower]
        if exact_matches:
            confidence += 0.4

        # Check for fact-type keywords (0.3 weight)
        # Indicates query is about specific fact types
        fact_type = self._detect_fact_type(query_lower)
        if fact_type:
            confidence += 0.3

        # Check for temporal keywords (0.3 weight)
        # Indicates query is about past events
        temporal_matches = [kw for kw in self.temporal_keywords if kw in query_lower]
        if temporal_matches:
            confidence += 0.3

        # Cap at 1.0 (in case all three match)
        return min(1.0, confidence)
