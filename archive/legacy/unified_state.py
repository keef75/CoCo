#!/usr/bin/env python3
"""
Unified Conversation State - Critical Memory Fragmentation Fix
============================================================
Solves the critical memory fragmentation issue where COCO loses context
across tool operations, file operations, and memory recalls.

This provides a single source of truth for ALL conversation state that
persists across every operation and maintains context continuity.
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import deque


@dataclass
class ConversationExchange:
    """Single exchange in conversation stream"""
    user_input: str
    assistant_response: str
    timestamp: datetime
    exchange_id: int
    extracted_facts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActiveOperation:
    """Track active operations to maintain context"""
    operation_type: str
    details: Dict[str, Any]
    started_at: datetime
    context_snapshot: Dict[str, Any]


class FactExtractor:
    """Intelligent fact extraction from conversation"""

    def __init__(self):
        # Pattern matching for common fact types
        self.patterns = {
            'personal_relationships': [
                (r'(?:my\s+)?wife(?:\'s)?\s+(?:is\s+|name\s+is\s+|named\s+|called\s+)(\w+)', 'wife_name'),
                (r'(?:my\s+)?husband.*?(?:is\s+|named\s+|called\s+)(\w+)', 'husband_name'),
                (r'(?:my\s+)?(?:son|daughter).*?(?:is\s+|named\s+|called\s+)(\w+)', 'child_name'),
                (r'(?:my\s+)?(?:mother|mom).*?(?:is\s+|named\s+|called\s+)(\w+)', 'mother_name'),
                (r'(?:my\s+)?(?:father|dad).*?(?:is\s+|named\s+|called\s+)(\w+)', 'father_name'),
            ],
            'personal_info': [
                (r'(?:i\s+am\s+|my\s+name\s+is\s+|call\s+me\s+)(\w+)', 'user_name'),
                (r'i\s+(?:work\s+at|am\s+at)\s+([^,\.\!]+)', 'workplace'),
                (r'i\s+live\s+in\s+([^,\.\!]+)', 'location'),
                (r'my\s+email\s+is\s+([\w\.-]+@[\w\.-]+)', 'email'),
            ],
            'preferences': [
                (r'i\s+(?:like|love|prefer)\s+([^,\.\!]+)', 'likes'),
                (r'i\s+(?:hate|dislike|avoid)\s+([^,\.\!]+)', 'dislikes'),
                (r'my\s+favorite\s+(\w+)\s+is\s+([^,\.\!]+)', 'favorite'),
            ],
            'projects_tasks': [
                (r'(?:working\s+on|building|creating)\s+([^,\.\!]+)', 'current_project'),
                (r'need\s+to\s+(?:do|complete|finish)\s+([^,\.\!]+)', 'task'),
            ]
        }

    def extract_facts(self, text: str) -> Dict[str, Any]:
        """Extract facts from text using pattern matching"""
        facts = {}
        text_lower = text.lower().strip()

        for category, patterns in self.patterns.items():
            for pattern, fact_type in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    # Handle multiple matches
                    if fact_type in facts:
                        if isinstance(facts[fact_type], list):
                            if '_name' in fact_type:
                                facts[fact_type].extend([m.capitalize() for m in matches])
                            else:
                                facts[fact_type].extend(matches)
                        else:
                            if '_name' in fact_type:
                                facts[fact_type] = [facts[fact_type]] + [m.capitalize() for m in matches]
                            else:
                                facts[fact_type] = [facts[fact_type]] + list(matches)
                    else:
                        # Capitalize first letter for names
                        if '_name' in fact_type:
                            fact_value = matches[0].capitalize() if len(matches) == 1 else [m.capitalize() for m in matches]
                        else:
                            fact_value = matches[0] if len(matches) == 1 else matches
                        facts[fact_type] = fact_value

        return facts


class UnifiedConversationState:
    """
    Single source of truth for ALL conversation state.

    This class solves the critical memory fragmentation issue by maintaining
    persistent context across all operations including:
    - Tool executions
    - File operations
    - Memory recalls
    - Search operations
    - Any other COCO operations

    The key innovation is that EVERY operation receives conversation context,
    ensuring continuity and preventing the "context bubble" problem.
    """

    def __init__(self, window_size: int = 20):
        # Core conversation state
        self.conversation_stream: List[ConversationExchange] = []
        self.working_memory_window: deque = deque(maxlen=window_size)

        # Extracted facts from conversation
        self.current_facts: Dict[str, Any] = {}
        self.fact_confidence: Dict[str, float] = {}

        # Backward compatibility alias
        self.facts_extracted = self.current_facts

        # Persistent context that follows through operations
        self.persistent_context: str = ""
        self.context_summary: str = ""

        # Operation tracking
        self.operation_stack: List[ActiveOperation] = []
        self.operation_history: List[ActiveOperation] = []

        # Fact extraction
        self.fact_extractor = FactExtractor()

        # State management
        self.last_update: datetime = datetime.now()
        self.context_dirty: bool = False

    def add_exchange(self, user_input: str, assistant_response: str = "") -> ConversationExchange:
        """
        Add exchange and extract facts - THE CRITICAL METHOD

        This is called after every conversation exchange and ensures
        the unified state is always up to date.
        """
        exchange_id = len(self.conversation_stream)
        timestamp = datetime.now()

        # Extract facts from user input
        extracted_facts = self.fact_extractor.extract_facts(user_input)

        # Create exchange record
        exchange = ConversationExchange(
            user_input=user_input,
            assistant_response=assistant_response,
            timestamp=timestamp,
            exchange_id=exchange_id,
            extracted_facts=extracted_facts
        )

        # Add to streams
        self.conversation_stream.append(exchange)
        self.working_memory_window.append(exchange)

        # Update facts with confidence scoring
        self._update_facts(extracted_facts)

        # For backward compatibility, also update facts_extracted alias
        self.facts_extracted = self.current_facts

        # Mark context as dirty for rebuild
        self.context_dirty = True
        self.last_update = timestamp

        return exchange

    def _update_facts(self, new_facts: Dict[str, Any]):
        """Update facts with confidence tracking"""
        for fact_type, value in new_facts.items():
            # Simple confidence: more recent = higher confidence
            confidence = 1.0  # Start with full confidence for new facts

            if fact_type in self.current_facts:
                # If fact already exists, average confidence
                old_confidence = self.fact_confidence.get(fact_type, 0.5)
                confidence = (old_confidence + 1.0) / 2

            self.current_facts[fact_type] = value
            self.fact_confidence[fact_type] = confidence

    def get_context_for_tool(self, tool_name: str, additional_context: Dict = None) -> Dict[str, Any]:
        """
        Get complete context for tool execution - THE FIX

        This method ensures EVERY tool operation has access to:
        - Current conversation facts
        - Recent exchanges
        - Ongoing operation context
        - Persistent context

        No more isolated tool execution!
        """
        # Rebuild context if dirty
        if self.context_dirty:
            self._rebuild_persistent_context()

        # CRITICAL FIX: Filter facts by current conversation relevance
        current_input = additional_context.get('current_input', '') if additional_context else ''
        relevant_facts = self._filter_relevant_facts(current_input)

        context = {
            # UPDATED: Only include relevant facts, not all facts
            'facts': relevant_facts,
            'fact_confidence': {k: v for k, v in self.fact_confidence.items() if k in relevant_facts},

            # Recent conversation exchanges (limited to recent window)
            'recent_exchanges': self._format_recent_exchanges(count=5),  # Only last 5 exchanges
            'working_memory': [ex.user_input for ex in list(self.working_memory_window)[-5:]],  # Only recent

            # Formatted context string
            'persistent_context': self.persistent_context,
            'context_summary': self.context_summary,

            # Operation tracking
            'current_operation': self.operation_stack[-1] if self.operation_stack else None,
            'operation_history': [op.operation_type for op in self.operation_history[-5:]],

            # Tool-specific context
            'tool_name': tool_name,
            'conversation_length': len(self.conversation_stream),
            'last_update': self.last_update.isoformat(),
        }

        # Merge additional context if provided
        if additional_context:
            context.update(additional_context)

        return context

    def _filter_relevant_facts(self, current_input: str) -> Dict[str, Any]:
        """Filter facts to only include those relevant to current conversation context"""
        if not current_input or not self.current_facts:
            return {}

        current_input_lower = current_input.lower()
        relevant_facts = {}

        # If current input mentions specific people/topics, include related facts
        for fact_type, value in self.current_facts.items():
            value_str = str(value).lower()

            # Check if current input is related to this fact
            is_relevant = False

            # Name-based relevance
            if '_name' in fact_type:
                name = value_str if isinstance(value, str) else (value[0] if isinstance(value, list) and value else '')
                if name and name in current_input_lower:
                    is_relevant = True

            # Topic-based relevance
            elif any(topic in current_input_lower for topic in ['wife', 'husband', 'family', 'profile'] if topic in fact_type):
                is_relevant = True

            # Project/task relevance
            elif any(topic in current_input_lower for topic in ['project', 'task', 'work'] if topic in fact_type):
                is_relevant = True

            # Recent fact relevance (facts from last 3 exchanges are always relevant)
            elif len(self.working_memory_window) <= 3:
                is_relevant = True

            if is_relevant:
                relevant_facts[fact_type] = value

        return relevant_facts

    def _format_recent_exchanges(self, count: int = 10) -> str:
        """Format recent exchanges for context injection"""
        lines = []
        recent = list(self.working_memory_window)[-count:]

        for ex in recent:
            lines.append(f"User: {ex.user_input[:200]}")
            if ex.assistant_response:
                lines.append(f"COCO: {ex.assistant_response[:200]}")
            lines.append("")  # Blank line for readability

        return "\n".join(lines)

    def _rebuild_persistent_context(self):
        """Build persistent context string for system prompts"""
        context_parts = [
            "=== CURRENT CONVERSATION CONTEXT ===",
            f"Conversation Length: {len(self.conversation_stream)} exchanges",
            f"Last Updated: {self.last_update.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # Add facts if available
        if self.current_facts:
            context_parts.append("FACTS LEARNED THIS CONVERSATION:")
            for fact_type, value in self.current_facts.items():
                confidence = self.fact_confidence.get(fact_type, 1.0)
                context_parts.append(f"  • {fact_type}: {value} (confidence: {confidence:.1f})")
            context_parts.append("")

        # Add recent exchanges
        if self.working_memory_window:
            context_parts.append("=== RECENT CONVERSATION ===")
            for ex in list(self.working_memory_window)[-5:]:
                context_parts.append(f"User: {ex.user_input[:150]}")
                if ex.assistant_response:
                    context_parts.append(f"COCO: {ex.assistant_response[:150]}")
                context_parts.append("")

        # Add operation context
        if self.operation_stack:
            current_op = self.operation_stack[-1]
            context_parts.append(f"=== CURRENT OPERATION ===")
            context_parts.append(f"Type: {current_op.operation_type}")
            context_parts.append(f"Started: {current_op.started_at.strftime('%H:%M:%S')}")
            context_parts.append("")

        self.persistent_context = "\n".join(context_parts)
        self.context_dirty = False

        # Generate summary
        self._generate_context_summary()

    def _generate_context_summary(self):
        """Generate a concise summary of current context"""
        parts = []

        if self.current_facts:
            fact_count = len(self.current_facts)
            parts.append(f"{fact_count} facts learned")

        if self.working_memory_window:
            parts.append(f"{len(self.working_memory_window)} recent exchanges")

        if self.operation_stack:
            parts.append(f"active: {self.operation_stack[-1].operation_type}")

        self.context_summary = ", ".join(parts) if parts else "new conversation"

    def push_operation(self, operation_type: str, details: Dict[str, Any] = None):
        """Track operation start with context snapshot"""
        if details is None:
            details = {}

        operation = ActiveOperation(
            operation_type=operation_type,
            details=details,
            started_at=datetime.now(),
            context_snapshot=self.current_facts.copy()
        )

        self.operation_stack.append(operation)
        return operation

    def pop_operation(self) -> Optional[ActiveOperation]:
        """Complete operation and archive"""
        if self.operation_stack:
            completed_op = self.operation_stack.pop()
            self.operation_history.append(completed_op)
            return completed_op
        return None

    def search_working_memory(self, query: str) -> str:
        """Search recent conversation for specific content - CONTEXT AWARE"""
        query_lower = query.lower()

        # CRITICAL FIX: Only search recent working memory window, not all conversations
        # This prevents pulling irrelevant context from distant conversations
        recent_exchanges = list(self.working_memory_window)[-10:]  # Only last 10 exchanges

        # Search backward through RECENT memory only for most relevant match
        for exchange in reversed(recent_exchanges):
            if query_lower in exchange.user_input.lower():
                return f"From current conversation: User said: {exchange.user_input}"
            if query_lower in exchange.assistant_response.lower():
                return f"From current conversation: Assistant said: {exchange.assistant_response}"

        return None

    def get_fact(self, fact_type: str, default: Any = None) -> Any:
        """Get a specific fact with confidence"""
        return self.current_facts.get(fact_type, default)

    def has_fact(self, fact_type: str, min_confidence: float = 0.5) -> bool:
        """Check if fact exists with minimum confidence"""
        return (fact_type in self.current_facts and
                self.fact_confidence.get(fact_type, 0.0) >= min_confidence)

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the entire conversation state"""
        return {
            'total_exchanges': len(self.conversation_stream),
            'facts_learned': len(self.current_facts),
            'recent_window_size': len(self.working_memory_window),
            'active_operations': len(self.operation_stack),
            'context_summary': self.context_summary,
            'last_update': self.last_update.isoformat(),
            'facts': self.current_facts.copy(),
        }

    def clear_context(self):
        """Reset context (emergency use only)"""
        self.current_facts.clear()
        self.fact_confidence.clear()
        self.persistent_context = ""
        self.context_summary = ""
        self.context_dirty = True

    def export_state(self) -> Dict[str, Any]:
        """Export complete state for debugging/persistence"""
        return {
            'conversation_stream': [
                {
                    'user_input': ex.user_input,
                    'assistant_response': ex.assistant_response,
                    'timestamp': ex.timestamp.isoformat(),
                    'exchange_id': ex.exchange_id,
                    'extracted_facts': ex.extracted_facts
                }
                for ex in self.conversation_stream
            ],
            'current_facts': self.current_facts,
            'fact_confidence': self.fact_confidence,
            'context_summary': self.context_summary,
            'operation_history': [
                {
                    'type': op.operation_type,
                    'started': op.started_at.isoformat()
                }
                for op in self.operation_history
            ]
        }