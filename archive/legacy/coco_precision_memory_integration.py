#!/usr/bin/env python3
"""
COCO Precision Memory Integration
================================
Integration layer to connect the precision memory system with COCO's existing architecture.
This provides the bridge between the new precision memory and the existing memory systems.

Integration Strategy:
1. Wraps existing HierarchicalMemorySystem
2. Adds precision recall capabilities
3. Maintains backward compatibility
4. Provides memory-aware function calling tools
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Import the precision memory system
from precision_conversation_memory import COCOMemoryInterface, PrecisionConversationMemory

# Rich UI for beautiful memory displays
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rich_print

logger = logging.getLogger(__name__)


class EnhancedMemorySystem:
    """
    Enhanced memory system that integrates precision conversation memory
    with COCO's existing hierarchical memory architecture.

    This becomes the new foundation for COCO's memory capabilities.
    """

    def __init__(self, config, existing_hierarchical_memory=None):
        self.config = config
        self.console = Console()

        # Initialize precision memory interface
        self.precision_interface = COCOMemoryInterface()

        # Keep reference to existing system for backward compatibility
        self.hierarchical_memory = existing_hierarchical_memory

        # Memory-aware tool calling handlers
        self.memory_tools = {
            'recall_memory': self._handle_recall_memory,
            'memory_search': self._handle_memory_search,
            'memory_stats': self._handle_memory_stats,
            'conversation_summary': self._handle_conversation_summary
        }

        logger.info("Enhanced memory system initialized with precision recall")

    def add_interaction(self, user_input: str, assistant_response: str,
                       metadata: Optional[Dict[str, Any]] = None):
        """
        Add a new interaction to both precision and hierarchical memory systems.
        This is the main integration point.
        """
        # Add to precision memory (this gives us perfect episodic recall)
        exchange_id = self.precision_interface.process_interaction(user_input, assistant_response)

        # Also add to existing hierarchical memory for backward compatibility
        if self.hierarchical_memory:
            try:
                self.hierarchical_memory.add_interaction(user_input, assistant_response)
            except Exception as e:
                logger.warning(f"Failed to add to hierarchical memory: {e}")

        # Log for debugging
        if self.config.debug_memory:
            self.console.print(f"[dim]Memory: Stored exchange {exchange_id}[/dim]")

        return exchange_id

    def handle_memory_query(self, query: str) -> Optional[str]:
        """
        Handle memory queries with precision recall.
        This is what gets called when user asks about previous conversations.
        """
        return self.precision_interface.handle_memory_query(query)

    def get_conversation_context_for_llm(self, max_tokens: int = 4000) -> str:
        """
        Get conversation context formatted for LLM injection.
        This replaces the existing context generation with precision memory.
        """
        context = self.precision_interface.get_conversation_context(max_tokens)

        # Add a header to help the LLM understand the context
        if context:
            header = "=== CONVERSATION MEMORY (Perfect Episodic Recall) ===\n"
            footer = "\n=== END CONVERSATION MEMORY ===\n"
            return header + context + footer

        return ""

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        precision_stats = self.precision_interface.get_memory_statistics()

        # Combine with hierarchical memory stats if available
        if self.hierarchical_memory and hasattr(self.hierarchical_memory, 'get_statistics'):
            hierarchical_stats = self.hierarchical_memory.get_statistics()
            precision_stats['hierarchical_memory'] = hierarchical_stats

        return precision_stats

    # === FUNCTION CALLING TOOL HANDLERS ===

    def _handle_recall_memory(self, query: str, max_results: int = 3) -> str:
        """
        Function calling tool for memory recall.
        This provides the crisp episodic recall capability.
        """
        try:
            # Use precision memory for retrieval
            response = self.precision_interface.handle_memory_query(query)

            if response:
                # Format for function calling response
                return f"🧠 **Memory Recall Results**\n\n{response}"
            else:
                return f"🔍 No specific memories found for: '{query}'\n\nThis might not be a memory query, or the topic wasn't discussed in our current conversation."

        except Exception as e:
            logger.error(f"Memory recall error: {e}")
            return f"❌ Memory recall failed: {str(e)}"

    def _handle_memory_search(self, query: str, max_results: int = 5) -> str:
        """
        Advanced memory search with debug information.
        Shows the retrieval process for debugging.
        """
        try:
            # Get debug information about the retrieval
            debug_info = self.precision_interface.debug_retrieve(query)

            if not debug_info:
                return f"🔍 No matches found for: '{query}'"

            # Format detailed results
            result = f"🔍 **Memory Search Results for**: '{query}'\n\n"
            result += f"Found {len(debug_info)} matches:\n\n"

            for i, info in enumerate(debug_info[:max_results], 1):
                result += f"**{i}. Turn {info['turn_number']}** ({info['timestamp'][:19]})\n"
                result += f"   User: {info['user_input']}\n"
                result += f"   Topics: {', '.join(info['topics']) if info['topics'] else 'None'}\n"
                result += f"   Importance: {info['importance_score']:.2f}\n"
                if info['context_markers']:
                    result += f"   Context: {', '.join(info['context_markers'])}\n"
                result += "\n"

            return result

        except Exception as e:
            logger.error(f"Memory search error: {e}")
            return f"❌ Memory search failed: {str(e)}"

    def _handle_memory_stats(self) -> str:
        """
        Get formatted memory statistics.
        Useful for debugging and system monitoring.
        """
        try:
            stats = self.get_memory_statistics()

            # Format as a nice table
            result = "📊 **Memory System Statistics**\n\n"

            # Basic stats
            result += f"**Session**: {stats.get('session_id', 'Unknown')}\n"
            result += f"**Total Exchanges**: {stats.get('total_exchanges', 0)}\n"
            result += f"**Average Importance**: {stats.get('average_importance', 0)}\n"
            result += f"**Questions Asked**: {stats.get('questions_asked', 0)}\n"
            result += f"**Exchanges with Code**: {stats.get('exchanges_with_code', 0)}\n"
            result += f"**Unique Topics**: {stats.get('unique_topics', 0)}\n\n"

            # Top topics
            if stats.get('top_topics'):
                result += "**Top Discussion Topics**:\n"
                for topic, count in stats['top_topics'][:5]:
                    result += f"  • {topic}: {count} times\n"
                result += "\n"

            # Index sizes
            if 'memory_indices' in stats:
                indices = stats['memory_indices']
                result += "**Memory Index Sizes**:\n"
                result += f"  • Topic Index: {indices.get('topic_index_size', 0)} topics\n"
                result += f"  • Keyword Index: {indices.get('keyword_index_size', 0)} keywords\n"
                result += f"  • Context Links: {indices.get('context_links', 0)} connections\n"

            return result

        except Exception as e:
            logger.error(f"Memory stats error: {e}")
            return f"❌ Failed to get memory statistics: {str(e)}"

    def _handle_conversation_summary(self, max_exchanges: int = 20) -> str:
        """
        Generate a formatted summary of the current conversation.
        """
        try:
            context = self.precision_interface.get_conversation_context(max_tokens=8000)

            if not context:
                return "📝 No conversation history available."

            # Add header and formatting
            result = f"📝 **Conversation Summary** (Recent {max_exchanges} exchanges)\n\n"
            result += context

            # Add statistics
            stats = self.precision_interface.get_memory_statistics()
            result += f"\n\n---\n**Session Stats**: {stats.get('total_exchanges', 0)} total exchanges"

            return result

        except Exception as e:
            logger.error(f"Conversation summary error: {e}")
            return f"❌ Failed to generate conversation summary: {str(e)}"

    # === INTEGRATION HELPERS ===

    def is_memory_query(self, user_input: str) -> bool:
        """
        Check if user input is a memory-related query.
        Used by COCO to decide whether to use memory tools.
        """
        memory_patterns = [
            r'what did (?:i|we|you) (?:say|discuss|mention)',
            r'remind me',
            r'(?:do you )?remember',
            r'(?:earlier|before)',
            r'(?:first|last) (?:thing|time)',
            r'recall',
            r'you (?:said|mentioned)',
            r'we (?:discussed|talked)'
        ]

        import re
        return any(re.search(pattern, user_input.lower()) for pattern in memory_patterns)

    def should_inject_context(self, user_input: str) -> bool:
        """
        Determine if conversation context should be injected into the LLM prompt.
        """
        # Always inject context unless it's a very simple greeting
        simple_greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening']

        return user_input.lower().strip() not in simple_greetings

    def display_memory_status(self):
        """
        Display a rich status panel showing memory system health.
        Useful for debugging and system monitoring.
        """
        try:
            stats = self.get_memory_statistics()

            # Create a status table
            table = Table(title="🧠 Memory System Status", show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")

            table.add_row("Session ID", stats.get('session_id', 'Unknown')[:16] + "...")
            table.add_row("Total Exchanges", str(stats.get('total_exchanges', 0)))
            table.add_row("Average Importance", f"{stats.get('average_importance', 0):.3f}")
            table.add_row("Questions Asked", str(stats.get('questions_asked', 0)))
            table.add_row("Code Exchanges", str(stats.get('exchanges_with_code', 0)))
            table.add_row("Unique Topics", str(stats.get('unique_topics', 0)))

            if 'memory_indices' in stats:
                indices = stats['memory_indices']
                table.add_row("Topic Index Size", str(indices.get('topic_index_size', 0)))
                table.add_row("Keyword Index Size", str(indices.get('keyword_index_size', 0)))
                table.add_row("Context Links", str(indices.get('context_links', 0)))

            self.console.print(table)

            # Show top topics if available
            if stats.get('top_topics'):
                self.console.print("\n🏷️ **Top Discussion Topics**:")
                for topic, count in stats['top_topics'][:5]:
                    self.console.print(f"  • [cyan]{topic}[/cyan]: {count} times")

        except Exception as e:
            self.console.print(f"[red]❌ Failed to display memory status: {e}[/red]")


class COCOMemoryConfig:
    """Configuration for the enhanced memory system"""

    def __init__(self):
        # Enable debug logging
        self.debug_memory = os.getenv("COCO_MEMORY_DEBUG", "false").lower() == "true"

        # Memory limits (0 = unlimited for eternal consciousness)
        self.memory_buffer_size = int(os.getenv("MEMORY_BUFFER_SIZE", "0"))
        self.memory_summary_buffer_size = int(os.getenv("MEMORY_SUMMARY_BUFFER_SIZE", "0"))

        # Context injection settings
        self.max_context_tokens = int(os.getenv("MAX_CONTEXT_TOKENS", "4000"))
        self.always_inject_context = os.getenv("ALWAYS_INJECT_CONTEXT", "true").lower() == "true"

        # Precision memory settings
        self.precision_db_path = os.getenv("PRECISION_MEMORY_DB", "./coco_workspace/precision_memory.db")
        self.importance_threshold = float(os.getenv("MEMORY_IMPORTANCE_THRESHOLD", "0.3"))


def create_enhanced_memory_system(existing_memory=None) -> EnhancedMemorySystem:
    """
    Factory function to create the enhanced memory system.
    This is what COCO calls to initialize the new memory architecture.
    """
    config = COCOMemoryConfig()

    return EnhancedMemorySystem(
        config=config,
        existing_hierarchical_memory=existing_memory
    )


# === FUNCTION CALLING INTEGRATION ===

def get_memory_function_schemas() -> List[Dict[str, Any]]:
    """
    Return function schemas for COCO's function calling system.
    These tools provide the memory interface to the LLM.
    """
    return [
        {
            "name": "recall_memory",
            "description": "Recall specific information from the current conversation with perfect precision. Use this when the user asks about something discussed earlier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The memory query - what to recall from the conversation"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of memory matches to return",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "memory_search",
            "description": "Advanced memory search with detailed debugging information. Use for complex memory queries or when debugging memory issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for conversation memory"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "memory_stats",
            "description": "Get detailed statistics about the conversation memory system. Useful for debugging and monitoring.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "conversation_summary",
            "description": "Get a formatted summary of the current conversation including recent exchanges and statistics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_exchanges": {
                        "type": "integer",
                        "description": "Maximum number of recent exchanges to include in summary",
                        "default": 20
                    }
                },
                "required": []
            }
        }
    ]


if __name__ == "__main__":
    # Test the integration system
    print("🧠 Testing COCO Precision Memory Integration")
    print("=" * 60)

    # Create enhanced memory system
    enhanced_memory = create_enhanced_memory_system()

    # Test adding interactions
    test_interactions = [
        ("I want to optimize COCO's memory system",
         "Great! Memory optimization is crucial. We should focus on episodic recall first."),
        ("What's the current architecture?",
         "COCO uses a hierarchical memory system with episodic and summary buffers."),
        ("How can we make it more precise?",
         "We need multi-strategy retrieval with keyword, topic, and temporal search capabilities.")
    ]

    for user_input, assistant_response in test_interactions:
        exchange_id = enhanced_memory.add_interaction(user_input, assistant_response)
        print(f"✅ Added: {exchange_id}")

    # Test memory queries
    print(f"\n🔍 Testing Memory Queries:")

    test_queries = [
        "what did I say about optimization?",
        "remind me about the architecture",
        "what was the first thing I asked?"
    ]

    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        response = enhanced_memory.handle_memory_query(query)
        if response:
            print(f"💭 Response: {response[:150]}...")
        else:
            print("❌ No memory response")

    # Show memory status
    print(f"\n📊 Memory Status:")
    enhanced_memory.display_memory_status()

    print(f"\n🎯 Integration test completed!")