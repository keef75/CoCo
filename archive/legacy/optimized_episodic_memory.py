#!/usr/bin/env python3
"""
Optimized Episodic Memory Manager - Layer 2
==========================================
Enhances the existing precision conversation memory system with intelligent
token budget management for the 4-layer architecture.

Integrates with:
- precision_conversation_memory.py (existing core system)
- unified_state.py (context continuity)
- episodic_memory_fix.py (temporal precision)

Optimizations:
- 350K token budget management
- Intelligent episode prioritization
- Metadata-driven compression
- Perfect temporal recall within budget constraints
"""

import re
import json
from pathlib import Path
from collections import deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

# Import existing precision memory components
try:
    from precision_conversation_memory import PrecisionConversationMemory, ConversationExchange
    from unified_state import UnifiedConversationState
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    IMPORTS_AVAILABLE = False

@dataclass
class OptimizedEpisode:
    """
    Enhanced episode structure optimized for token budget management.

    Combines the precision of ConversationExchange with intelligent
    metadata for budget-conscious storage and retrieval.
    """
    # Core conversation data
    exchange_id: str
    exchange_number: int
    timestamp: datetime
    user_input: str
    assistant_response: str

    # Token management
    token_count: int
    priority_score: float  # 0.0-1.0, higher = more important to keep

    # Enhanced metadata for intelligent retrieval
    tools_used: List[str]
    decisions_made: List[str]
    entities_mentioned: List[str]
    topics: List[str]
    importance_indicators: List[str]  # "user_feedback", "task_completion", "entity_definition"

    # Preference learning
    has_feedback: bool
    feedback_type: Optional[str]
    preference_signals: List[str]

    # Context relationships
    references_previous: List[str]  # Exchange IDs this episode references
    referenced_by: List[str]       # Exchange IDs that reference this episode

    # Compression readiness
    can_compress: bool  # False for key exchanges that should never compress
    compression_summary: Optional[str]  # Pre-computed summary for compression

class OptimizedEpisodicMemory:
    """
    Layer 2 episodic memory with intelligent token budget management.

    This system maintains perfect recent memory within a 350K token budget
    by using intelligent prioritization, metadata-driven compression, and
    dynamic episode management.
    """

    def __init__(self, max_tokens: int = 350000):
        self.max_tokens = max_tokens
        self.current_tokens = 0

        # Episode storage (no fixed size - managed by token budget)
        self.episodes: deque[OptimizedEpisode] = deque()
        self.episode_index: Dict[str, OptimizedEpisode] = {}

        # Integration with existing systems
        self.precision_memory = PrecisionConversationMemory() if IMPORTS_AVAILABLE else None
        self.unified_state = UnifiedConversationState() if IMPORTS_AVAILABLE else None

        # Priority calculation weights
        self.priority_weights = {
            'recency': 0.3,          # Recent episodes are important
            'user_feedback': 0.25,   # Episodes with feedback are crucial
            'task_completion': 0.2,  # Successful task completions matter
            'entity_definition': 0.15,  # Episodes that define entities
            'reference_count': 0.1   # Episodes referenced by others
        }

        # Token estimation settings
        self.tokens_per_char = 0.25  # Approximately 4 characters per token

        # Compression triggers
        self.compression_threshold = 0.9  # Compress when 90% of budget used

    def add_episode(self, user_input: str, assistant_response: str,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add new episode with intelligent token budget management.

        This method adds episodes and automatically manages the token budget
        through intelligent prioritization and compression.
        """

        # Generate episode ID
        exchange_id = f"ep_{len(self.episodes)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Calculate token count
        content = f"{user_input}\n{assistant_response}"
        token_count = self._estimate_tokens(content)

        # Extract metadata
        extracted_metadata = self._extract_episode_metadata(user_input, assistant_response)
        if metadata:
            extracted_metadata.update(metadata)

        # Calculate priority score
        priority_score = self._calculate_priority_score(
            user_input, assistant_response, extracted_metadata
        )

        # Create optimized episode
        episode = OptimizedEpisode(
            exchange_id=exchange_id,
            exchange_number=len(self.episodes),
            timestamp=datetime.now(),
            user_input=user_input,
            assistant_response=assistant_response,
            token_count=token_count,
            priority_score=priority_score,
            tools_used=extracted_metadata.get('tools_used', []),
            decisions_made=extracted_metadata.get('decisions_made', []),
            entities_mentioned=extracted_metadata.get('entities_mentioned', []),
            topics=extracted_metadata.get('topics', []),
            importance_indicators=extracted_metadata.get('importance_indicators', []),
            has_feedback=extracted_metadata.get('has_feedback', False),
            feedback_type=extracted_metadata.get('feedback_type'),
            preference_signals=extracted_metadata.get('preference_signals', []),
            references_previous=self._find_previous_references(user_input),
            referenced_by=[],
            can_compress=not extracted_metadata.get('never_compress', False),
            compression_summary=None
        )

        # Add to storage
        self.episodes.append(episode)
        self.episode_index[exchange_id] = episode
        self.current_tokens += token_count

        # Update reference relationships
        self._update_reference_relationships(episode)

        # Integrate with precision memory system
        if self.precision_memory:
            try:
                self.precision_memory.add_exchange(
                    session_id="current",
                    user_input=user_input,
                    assistant_response=assistant_response,
                    metadata={
                        'episode_id': exchange_id,
                        'priority_score': priority_score,
                        'tools_used': episode.tools_used
                    }
                )
            except Exception as e:
                print(f"⚠️ Precision memory integration error: {e}")

        # Manage token budget
        if self.current_tokens > self.max_tokens * self.compression_threshold:
            self._manage_token_budget()

        return exchange_id

    def retrieve_by_temporal_query(self, query: str, max_results: int = 5) -> List[OptimizedEpisode]:
        """
        Handle temporal queries with high precision.

        Optimized version of temporal retrieval that works within token constraints
        while maintaining perfect recall capabilities.
        """
        query_lower = query.lower()
        results = []

        # "First" queries - always available regardless of compression
        if any(word in query_lower for word in ['first', 'beginning', 'started', 'initial']):
            if self.episodes:
                # Find the first episode (might need to check compressed summaries)
                first_episode = min(self.episodes, key=lambda e: e.exchange_number)
                results.append(first_episode)

        # "Last" or "recent" queries - prioritize recent high-importance episodes
        elif any(word in query_lower for word in ['last', 'just', 'recent', 'previous', 'latest']):
            # Get last 5 episodes, sorted by recency and importance
            recent_candidates = sorted(
                list(self.episodes)[-10:],
                key=lambda e: (e.timestamp, e.priority_score),
                reverse=True
            )
            results.extend(recent_candidates[:max_results])

        # "Earlier" queries - find older episodes but prioritize important ones
        elif any(word in query_lower for word in ['earlier', 'before', 'previously']):
            # Get episodes from first half of conversation, prioritize by importance
            if self.episodes:
                midpoint = len(self.episodes) // 2
                earlier_episodes = list(self.episodes)[:midpoint]
                earlier_sorted = sorted(earlier_episodes, key=lambda e: e.priority_score, reverse=True)
                results.extend(earlier_sorted[:max_results])

        # Specific time references
        elif 'today' in query_lower:
            today = datetime.now().date()
            today_episodes = [e for e in self.episodes if e.timestamp.date() == today]
            results.extend(sorted(today_episodes, key=lambda e: e.priority_score, reverse=True))

        return results[:max_results]

    def search_episodes_optimized(self, search_query: str, max_results: int = 5) -> List[OptimizedEpisode]:
        """
        Optimized episode search that leverages metadata for fast retrieval.

        Uses extracted metadata (entities, topics, tools) for efficient searching
        without scanning full episode content.
        """
        search_lower = search_query.lower()
        scored_results = []

        for episode in self.episodes:
            score = 0.0

            # High-value metadata searches (fast)
            if any(search_lower in entity.lower() for entity in episode.entities_mentioned):
                score += 10.0

            if any(search_lower in topic.lower() for topic in episode.topics):
                score += 8.0

            if any(search_lower in tool.lower() for tool in episode.tools_used):
                score += 6.0

            # Content search (slower, but weighted by importance)
            if (search_lower in episode.user_input.lower() or
                search_lower in episode.assistant_response.lower()):
                score += 5.0 * episode.priority_score

            # Boost score for high-priority episodes
            score *= (1.0 + episode.priority_score)

            if score > 0:
                scored_results.append((episode, score))

        # Sort by score and return top results
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return [episode for episode, score in scored_results[:max_results]]

    def get_context_for_injection(self, max_tokens: int = None) -> str:
        """
        Generate optimized context for injection into COCO's context window.

        Creates the most valuable episodic context within token constraints,
        prioritizing high-importance episodes and recent interactions.
        """
        if max_tokens is None:
            max_tokens = self.max_tokens

        context_parts = [
            "=== LAYER 2: OPTIMIZED EPISODIC MEMORY ===",
            f"Total Episodes: {len(self.episodes)}",
            f"Token Budget: {self.current_tokens:,} / {self.max_tokens:,} ({self.current_tokens/self.max_tokens*100:.1f}%)",
            f"Time Range: {self._get_time_range()}",
            ""
        ]

        # Estimate header tokens
        header_text = "\n".join(context_parts)
        used_tokens = self._estimate_tokens(header_text)

        # Select episodes for inclusion using priority-based selection
        selected_episodes = self._select_episodes_for_context(max_tokens - used_tokens)

        # Format selected episodes
        for episode in selected_episodes:
            episode_text = self._format_episode_for_context(episode)
            episode_tokens = self._estimate_tokens(episode_text)

            if used_tokens + episode_tokens <= max_tokens:
                context_parts.append(episode_text)
                used_tokens += episode_tokens
            else:
                # Truncate the last episode to fit budget
                remaining_tokens = max_tokens - used_tokens - 100  # Buffer
                truncated_text = self._truncate_episode(episode, remaining_tokens)
                context_parts.append(truncated_text)
                context_parts.append("[Additional episodes truncated due to token budget]")
                break

        return "\n".join(context_parts)

    def _extract_episode_metadata(self, user_input: str, assistant_response: str) -> Dict[str, Any]:
        """
        Extract rich metadata from episode content for efficient retrieval.

        This metadata enables fast searching and intelligent prioritization
        without full content analysis.
        """
        metadata = {
            'tools_used': [],
            'decisions_made': [],
            'entities_mentioned': [],
            'topics': [],
            'importance_indicators': [],
            'has_feedback': False,
            'feedback_type': None,
            'preference_signals': [],
            'never_compress': False
        }

        combined_text = f"{user_input} {assistant_response}"
        user_lower = user_input.lower()

        # Extract tools used (from assistant response)
        tool_patterns = [
            r'send_email', r'create_video', r'generate_image', r'search_web',
            r'read_file', r'write_file', r'check_calendar', r'add_calendar_event',
            r'analyze_image', r'generate_music'
        ]
        for pattern in tool_patterns:
            if re.search(pattern, assistant_response, re.IGNORECASE):
                metadata['tools_used'].append(pattern)

        # Extract decisions (look for decision language)
        decision_patterns = [
            r"I'll", r"I will", r"Let me", r"I should", r"I need to",
            r"decided to", r"choosing to", r"going to"
        ]
        for pattern in decision_patterns:
            matches = re.findall(f"{pattern}[^.!?]*", assistant_response, re.IGNORECASE)
            metadata['decisions_made'].extend(matches[:3])  # Limit to avoid bloat

        # Extract entities (capitalized words, names)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', combined_text)
        # Filter out common words
        common_words = {'The', 'This', 'That', 'Here', 'There', 'When', 'Where', 'What', 'How'}
        entities = [e for e in entities if e not in common_words]
        metadata['entities_mentioned'] = list(set(entities))[:10]  # Dedupe and limit

        # Extract topics (noun phrases and key terms)
        # This is a simplified version - could be enhanced with NLP
        topic_candidates = re.findall(r'\b(?:project|task|research|analysis|report|email|video|system)\b',
                                     combined_text.lower())
        metadata['topics'] = list(set(topic_candidates))

        # Detect importance indicators
        if any(word in user_lower for word in ['important', 'urgent', 'priority', 'asap']):
            metadata['importance_indicators'].append('user_priority')

        if any(word in user_lower for word in ['great', 'perfect', 'excellent', 'amazing']):
            metadata['importance_indicators'].append('user_feedback')
            metadata['has_feedback'] = True
            metadata['feedback_type'] = 'positive'

        if len(metadata['tools_used']) > 0:
            metadata['importance_indicators'].append('tool_usage')

        if len(metadata['decisions_made']) > 0:
            metadata['importance_indicators'].append('decision_making')

        # Detect preference signals
        preference_words = ['always', 'never', 'prefer', 'like', 'format', 'style']
        if any(word in user_lower for word in preference_words):
            metadata['preference_signals'] = [user_input]

        # Mark episodes that should never be compressed
        never_compress_indicators = ['first', 'remember this', 'important decision']
        if any(indicator in user_lower for indicator in never_compress_indicators):
            metadata['never_compress'] = True

        return metadata

    def _calculate_priority_score(self, user_input: str, assistant_response: str,
                                 metadata: Dict[str, Any]) -> float:
        """
        Calculate priority score (0.0-1.0) for token budget management.

        Higher priority episodes are kept longer when budget constraints require
        compression or removal of older episodes.
        """
        score = 0.0

        # Base recency score (newer = higher priority)
        score += self.priority_weights['recency'] * 0.5  # Base recency

        # User feedback bonus
        if metadata.get('has_feedback'):
            score += self.priority_weights['user_feedback']

        # Task completion bonus
        if metadata.get('tools_used'):
            tool_bonus = min(len(metadata['tools_used']) * 0.1, 0.3)
            score += self.priority_weights['task_completion'] * tool_bonus

        # Entity definition bonus (episodes that introduce new entities)
        if metadata.get('entities_mentioned'):
            entity_bonus = min(len(metadata['entities_mentioned']) * 0.05, 0.2)
            score += self.priority_weights['entity_definition'] * entity_bonus

        # Decision making bonus
        if metadata.get('decisions_made'):
            score += 0.1 * min(len(metadata['decisions_made']), 3)

        # Importance indicators
        for indicator in metadata.get('importance_indicators', []):
            if indicator == 'user_priority':
                score += 0.2
            elif indicator == 'user_feedback':
                score += 0.15
            elif indicator == 'tool_usage':
                score += 0.1

        # Never compress episodes get maximum priority
        if metadata.get('never_compress'):
            score = 1.0

        return min(score, 1.0)  # Cap at 1.0

    def _manage_token_budget(self):
        """
        Manage token budget through intelligent episode compression/removal.

        Uses priority scores to determine which episodes to compress or remove
        when approaching token budget limits.
        """
        if self.current_tokens <= self.max_tokens:
            return

        print(f"🔄 Managing token budget: {self.current_tokens:,} / {self.max_tokens:,}")

        # Sort episodes by priority (lowest first for removal)
        episodes_by_priority = sorted(self.episodes, key=lambda e: e.priority_score)

        tokens_to_free = self.current_tokens - int(self.max_tokens * 0.8)  # Target 80% usage
        tokens_freed = 0
        compressed_count = 0
        removed_count = 0

        for episode in episodes_by_priority:
            if tokens_freed >= tokens_to_free:
                break

            if episode.can_compress and episode.priority_score < 0.5:
                # Compress low-priority episodes
                if not episode.compression_summary:
                    episode.compression_summary = self._create_compression_summary(episode)
                    # Clear detailed content but keep metadata and summary
                    saved_tokens = episode.token_count - self._estimate_tokens(episode.compression_summary)
                    tokens_freed += saved_tokens
                    compressed_count += 1

            elif episode.priority_score < 0.2:
                # Remove very low priority episodes
                self.episodes.remove(episode)
                del self.episode_index[episode.exchange_id]
                tokens_freed += episode.token_count
                removed_count += 1

        # Recalculate current token usage
        self._recalculate_token_usage()

        print(f"✅ Budget management complete:")
        print(f"   Compressed: {compressed_count} episodes")
        print(f"   Removed: {removed_count} episodes")
        print(f"   New usage: {self.current_tokens:,} / {self.max_tokens:,}")

    def _create_compression_summary(self, episode: OptimizedEpisode) -> str:
        """
        Create compressed summary of an episode preserving key information.

        Maintains searchability while dramatically reducing token usage.
        """
        summary_parts = [
            f"[{episode.timestamp.strftime('%Y-%m-%d %H:%M')}]",
            f"Priority: {episode.priority_score:.2f}"
        ]

        # Preserve key elements
        if episode.entities_mentioned:
            summary_parts.append(f"Entities: {', '.join(episode.entities_mentioned[:5])}")

        if episode.tools_used:
            summary_parts.append(f"Tools: {', '.join(episode.tools_used)}")

        if episode.topics:
            summary_parts.append(f"Topics: {', '.join(episode.topics)}")

        if episode.has_feedback:
            summary_parts.append(f"Feedback: {episode.feedback_type}")

        # Truncated content
        user_summary = episode.user_input[:100] + "..." if len(episode.user_input) > 100 else episode.user_input
        assistant_summary = episode.assistant_response[:100] + "..." if len(episode.assistant_response) > 100 else episode.assistant_response

        summary_parts.extend([
            f"User: {user_summary}",
            f"Assistant: {assistant_summary}"
        ])

        return " | ".join(summary_parts)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count using character-based heuristic."""
        return int(len(text) * self.tokens_per_char)

    def _recalculate_token_usage(self):
        """Recalculate total token usage after compression/removal operations."""
        total_tokens = 0
        for episode in self.episodes:
            if episode.compression_summary:
                total_tokens += self._estimate_tokens(episode.compression_summary)
            else:
                total_tokens += episode.token_count
        self.current_tokens = total_tokens

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the optimized episodic memory."""
        if not self.episodes:
            return {'status': 'no_episodes'}

        # Calculate priority distribution
        priorities = [e.priority_score for e in self.episodes]
        avg_priority = sum(priorities) / len(priorities)
        high_priority_count = sum(1 for p in priorities if p >= 0.7)

        # Calculate compression stats
        compressed_count = sum(1 for e in self.episodes if e.compression_summary)

        # Tool usage stats
        all_tools = []
        for e in self.episodes:
            all_tools.extend(e.tools_used)
        tool_counts = {}
        for tool in all_tools:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

        return {
            'total_episodes': len(self.episodes),
            'token_usage': f"{self.current_tokens:,} / {self.max_tokens:,}",
            'budget_utilization': f"{self.current_tokens/self.max_tokens*100:.1f}%",
            'average_priority': round(avg_priority, 3),
            'high_priority_episodes': high_priority_count,
            'compressed_episodes': compressed_count,
            'time_span': self._get_time_range(),
            'top_tools': sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'entities_tracked': sum(len(e.entities_mentioned) for e in self.episodes),
            'feedback_episodes': sum(1 for e in self.episodes if e.has_feedback)
        }

# Test the optimized episodic memory system
if __name__ == "__main__":
    print("🧠 Testing Optimized Episodic Memory System")
    print("=" * 60)

    # Initialize manager
    memory = OptimizedEpisodicMemory(max_tokens=350000)

    # Test episode addition with various priorities
    test_episodes = [
        ("What's the weather like today?", "I don't have access to real-time weather data, but I can help you find weather information."),
        ("Great job on that explanation!", "Thank you! I'm glad the explanation was helpful."),
        ("Send an email to Katie about the project update", "I'll send an email to Katie about the project update using the send_email tool."),
        ("Always use bullet points when listing items", "I'll remember to use bullet points for lists going forward."),
        ("Create a video about consciousness", "I'll create a video about consciousness using the create_video tool.")
    ]

    episode_ids = []
    for user_input, assistant_response in test_episodes:
        episode_id = memory.add_episode(user_input, assistant_response)
        episode_ids.append(episode_id)
        print(f"✅ Added episode {episode_id}")

    # Test temporal queries
    print(f"\n🔍 Testing temporal queries:")
    first_results = memory.retrieve_by_temporal_query("what was the first thing I asked?")
    print(f"First thing query: {len(first_results)} results")

    recent_results = memory.retrieve_by_temporal_query("what did I just say?")
    print(f"Recent query: {len(recent_results)} results")

    # Test optimized search
    print(f"\n🔍 Testing optimized search:")
    search_results = memory.search_episodes_optimized("Katie project")
    print(f"Katie project search: {len(search_results)} results")

    # Test context generation
    context = memory.get_context_for_injection(max_tokens=5000)
    token_estimate = memory._estimate_tokens(context)
    print(f"\n📋 Generated context: {token_estimate:,} tokens")

    # Test statistics
    stats = memory.get_memory_statistics()
    print(f"\n📊 Memory Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print(f"\n🎯 Optimized episodic memory system ready!")