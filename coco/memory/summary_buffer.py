"""
Layer 2 conversation summary buffer memory.

Provides precision-preserved conversation summaries for cross-session
consciousness continuity. Two main classes:

  - ConversationSummary: data model for a single conversation summary
  - SummaryBufferMemory: manages a FIFO buffer of N recent summaries,
    handles serialisation/deserialisation, search, and LLM context injection

Extracted from the monolithic cocoa.py ConversationSummary and
SummaryBufferMemory classes.
"""

from __future__ import annotations

import json
import os
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from coco.config.settings import Config


class ConversationSummary:
    """
    Precision-preserved conversation summary for Layer 2 memory system.
    Maintains granular detail for cross-session consciousness continuity.
    """

    def __init__(self):
        self.schema_version: str = "1.0"
        self.conversation_id: str = ""
        self.timestamp_start: datetime = datetime.now()
        self.timestamp_end: datetime = datetime.now()
        self.total_exchanges: int = 0

        # Preserved Exchanges
        self.opening_exchange: Dict[str, str] = {"user": "", "assistant": ""}
        self.closing_exchange: Dict[str, str] = {"user": "", "assistant": ""}
        self.key_exchanges: List[Dict[str, Any]] = []

        # Structured Extraction
        self.key_points: List[str] = []
        self.insights: List[str] = []
        self.progress_made: List[str] = []
        self.people_mentioned: Dict[str, str] = {}
        self.topics_discussed: List[str] = []
        self.technical_solutions: List[str] = []
        self.creative_outputs: List[str] = []
        self.emotional_moments: List[str] = []
        self.decisions_made: List[str] = []
        self.unfinished_threads: List[str] = []

        # Searchable Metadata
        self.search_index: Dict[str, List[str]] = {
            "topics": [],
            "entities": [],
            "temporal_references": [],
            "technical_terms": [],
        }

        # Relationship Dynamics
        self.trust_indicators: List[str] = []
        self.collaboration_patterns: List[str] = []
        self.communication_style: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to dictionary for JSON serialization"""
        return {
            "schema_version": self.schema_version,
            "conversation_id": self.conversation_id,
            "timestamp_start": self.timestamp_start.isoformat(),
            "timestamp_end": self.timestamp_end.isoformat(),
            "total_exchanges": self.total_exchanges,
            "opening_exchange": self.opening_exchange,
            "closing_exchange": self.closing_exchange,
            "key_exchanges": self.key_exchanges,
            "key_points": self.key_points,
            "insights": self.insights,
            "progress_made": self.progress_made,
            "people_mentioned": self.people_mentioned,
            "topics_discussed": self.topics_discussed,
            "technical_solutions": self.technical_solutions,
            "creative_outputs": self.creative_outputs,
            "emotional_moments": self.emotional_moments,
            "decisions_made": self.decisions_made,
            "unfinished_threads": self.unfinished_threads,
            "search_index": self.search_index,
            "trust_indicators": self.trust_indicators,
            "collaboration_patterns": self.collaboration_patterns,
            "communication_style": self.communication_style,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationSummary":
        """Create summary from dictionary (JSON deserialization)"""
        summary = cls()
        summary.schema_version = data.get("schema_version", "1.0")
        summary.conversation_id = data.get("conversation_id", "")

        if "timestamp_start" in data:
            summary.timestamp_start = datetime.fromisoformat(data["timestamp_start"])
        if "timestamp_end" in data:
            summary.timestamp_end = datetime.fromisoformat(data["timestamp_end"])

        summary.total_exchanges = data.get("total_exchanges", 0)
        summary.opening_exchange = data.get("opening_exchange", {"user": "", "assistant": ""})
        summary.closing_exchange = data.get("closing_exchange", {"user": "", "assistant": ""})
        summary.key_exchanges = data.get("key_exchanges", [])
        summary.key_points = data.get("key_points", [])
        summary.insights = data.get("insights", [])
        summary.progress_made = data.get("progress_made", [])
        summary.people_mentioned = data.get("people_mentioned", {})
        summary.topics_discussed = data.get("topics_discussed", [])
        summary.technical_solutions = data.get("technical_solutions", [])
        summary.creative_outputs = data.get("creative_outputs", [])
        summary.emotional_moments = data.get("emotional_moments", [])
        summary.decisions_made = data.get("decisions_made", [])
        summary.unfinished_threads = data.get("unfinished_threads", [])
        summary.search_index = data.get(
            "search_index",
            {"topics": [], "entities": [], "temporal_references": [], "technical_terms": []},
        )
        summary.trust_indicators = data.get("trust_indicators", [])
        summary.collaboration_patterns = data.get("collaboration_patterns", [])
        summary.communication_style = data.get("communication_style", "")

        return summary


class SummaryBufferMemory:
    """
    Layer 2 Memory: Manages injection of N previous conversation summaries
    for precise cross-conversation continuity and consciousness persistence.
    """

    def __init__(self, config: Config):
        self.config = config
        self.console = config.console

        # Configuration from environment
        self.max_summaries = int(os.getenv("SUMMARY_BUFFER_SIZE", "10"))
        self.detail_level = os.getenv("SUMMARY_DETAIL_LEVEL", "high")
        self.auto_save = os.getenv("SUMMARY_AUTO_SAVE", "true").lower() == "true"
        self.enabled = os.getenv("ENABLE_LAYER2_MEMORY", "false").lower() == "true"

        # Storage paths
        workspace_path = Path(config.workspace)
        self.storage_path = workspace_path / "memory" / "summaries"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.index_file = self.storage_path / "summary_index.json"

        # Summary buffer (FIFO)
        self.summaries: deque = deque(maxlen=self.max_summaries)
        self.summary_index: Dict[str, Any] = {}

        # Load existing summaries on initialization
        self._load_summary_index()
        self._load_summaries_into_buffer()

        # Current session tracking
        self.current_session_exchanges: List[Dict[str, Any]] = []
        self.session_start_time: datetime = datetime.now()

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def _load_summary_index(self):
        """Load summary index with graceful error handling"""
        try:
            if self.index_file.exists():
                with open(self.index_file, "r") as f:
                    self.summary_index = json.load(f)
                if self.config.debug:
                    self.console.print(
                        f"[dim green]Loaded summary index with "
                        f"{len(self.summary_index)} entries[/dim green]"
                    )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if self.config.debug:
                self.console.print(
                    f"[dim yellow]Summary index load failed, continuing without Layer 2: {e}[/dim yellow]"
                )
            self.summary_index = {}

    def _save_summary_index(self):
        """Save summary index with error handling"""
        try:
            with open(self.index_file, "w") as f:
                json.dump(self.summary_index, f, indent=2)
        except Exception as e:
            if self.config.debug:
                self.console.print(f"[dim red]Failed to save summary index: {e}[/dim red]")

    def _load_summaries_into_buffer(self):
        """Load the most recent summaries into the buffer"""
        if not self.enabled or not self.summary_index:
            return

        try:
            sorted_summaries = sorted(
                self.summary_index.items(),
                key=lambda x: x[1].get("timestamp_start", ""),
                reverse=True,
            )

            loaded_count = 0
            for conversation_id, _metadata in sorted_summaries[: self.max_summaries]:
                summary_file = self.storage_path / f"{conversation_id}.json"
                if summary_file.exists():
                    try:
                        with open(summary_file, "r") as f:
                            summary_data = json.load(f)
                        summary = ConversationSummary.from_dict(summary_data)
                        self.summaries.append(summary)
                        loaded_count += 1
                    except Exception as e:
                        if self.config.debug:
                            self.console.print(
                                f"[dim yellow]Failed to load summary {conversation_id}: {e}[/dim yellow]"
                            )

            if loaded_count > 0 and self.config.debug:
                self.console.print(
                    f"[dim green]Loaded {loaded_count} conversation summaries "
                    f"into Layer 2 buffer[/dim green]"
                )

        except Exception as e:
            if self.config.debug:
                self.console.print(f"[dim red]Error loading summaries into buffer: {e}[/dim red]")

    # ------------------------------------------------------------------
    # Exchange tracking
    # ------------------------------------------------------------------

    def track_exchange(self, user_text: str, agent_text: str):
        """Track conversation exchanges for summary generation"""
        if not self.enabled:
            return

        exchange = {
            "timestamp": datetime.now(),
            "user": user_text,
            "assistant": agent_text,
            "exchange_number": len(self.current_session_exchanges) + 1,
        }
        self.current_session_exchanges.append(exchange)

    # ------------------------------------------------------------------
    # Summary generation
    # ------------------------------------------------------------------

    def generate_conversation_summary(
        self, force_save: bool = False
    ) -> Optional[ConversationSummary]:
        """
        Generate comprehensive conversation summary from current session.
        """
        if not self.enabled or (not force_save and len(self.current_session_exchanges) < 3):
            return None

        try:
            summary = ConversationSummary()

            summary.conversation_id = f"conv_{datetime.now().strftime('%Y_%m_%d_%H%M')}"
            summary.timestamp_start = self.session_start_time
            summary.timestamp_end = datetime.now()
            summary.total_exchanges = len(self.current_session_exchanges)

            if self.current_session_exchanges:
                first_exchange = self.current_session_exchanges[0]
                summary.opening_exchange = {
                    "user": first_exchange["user"],
                    "assistant": first_exchange["assistant"],
                }

                last_exchange = self.current_session_exchanges[-1]
                summary.closing_exchange = {
                    "user": last_exchange["user"],
                    "assistant": last_exchange["assistant"],
                }

                summary.key_exchanges = self._identify_key_exchanges(
                    self.current_session_exchanges
                )

            summary.key_points = self._extract_key_points(self.current_session_exchanges)
            summary.insights = self._extract_insights(self.current_session_exchanges)
            summary.progress_made = self._extract_progress(self.current_session_exchanges)
            summary.topics_discussed = self._extract_topics(self.current_session_exchanges)
            summary.technical_solutions = self._extract_technical_content(
                self.current_session_exchanges
            )
            summary.decisions_made = self._extract_decisions(self.current_session_exchanges)
            summary.unfinished_threads = self._extract_unfinished_threads(
                self.current_session_exchanges
            )

            summary.search_index = self._build_search_index(summary)

            summary.trust_indicators = self._extract_trust_indicators(
                self.current_session_exchanges
            )
            summary.collaboration_patterns = self._extract_collaboration_patterns(
                self.current_session_exchanges
            )
            summary.communication_style = self._analyze_communication_style(
                self.current_session_exchanges
            )

            return summary

        except Exception as e:
            if self.config.debug:
                self.console.print(f"[dim red]Error generating conversation summary: {e}[/dim red]")
            return None

    # ------------------------------------------------------------------
    # Key-exchange identification helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _identify_key_exchanges(exchanges: List[Dict]) -> List[Dict[str, Any]]:
        """Identify exchanges worth preserving verbatim"""
        key_exchanges: List[Dict[str, Any]] = []

        importance_keywords = [
            "breakthrough", "insight", "realize", "understand", "decision",
            "implement", "solution", "problem", "critical", "important",
            "remember", "recall", "discussed", "mentioned", "talked about",
            "plan", "next", "continue", "follow up",
        ]

        for exchange in exchanges:
            user_text = exchange["user"].lower()
            assistant_text = exchange["assistant"].lower()

            if any(
                keyword in user_text or keyword in assistant_text
                for keyword in importance_keywords
            ):
                key_exchanges.append({
                    "exchange_number": exchange["exchange_number"],
                    "user": exchange["user"],
                    "assistant": exchange["assistant"],
                    "reason_preserved": "Contains important keywords or breakthrough moment",
                    "timestamp": exchange["timestamp"].isoformat(),
                })
            elif len(exchange["user"]) > 200 or len(exchange["assistant"]) > 300:
                key_exchanges.append({
                    "exchange_number": exchange["exchange_number"],
                    "user": exchange["user"],
                    "assistant": exchange["assistant"],
                    "reason_preserved": "Detailed exchange with substantial content",
                    "timestamp": exchange["timestamp"].isoformat(),
                })

        return key_exchanges[:10]

    # ------------------------------------------------------------------
    # Structured extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_key_points(exchanges: List[Dict]) -> List[str]:
        key_points: List[str] = []
        for exchange in exchanges:
            user_text = exchange["user"]
            assistant_text = exchange["assistant"]

            if any(p in user_text.lower() for p in ["let's", "we should", "i want to", "can we"]):
                key_points.append(f"User initiated: {user_text[:100]}...")
            if any(p in assistant_text.lower() for p in ["solution", "approach", "recommend", "suggest"]):
                key_points.append(f"COCO suggested: {assistant_text[:100]}...")

        return key_points[:15]

    @staticmethod
    def _extract_insights(exchanges: List[Dict]) -> List[str]:
        insights: List[str] = []
        insight_keywords = ["realize", "understand", "insight", "breakthrough", "aha", "makes sense"]
        for exchange in exchanges:
            for keyword in insight_keywords:
                if keyword in exchange["user"].lower() or keyword in exchange["assistant"].lower():
                    if keyword in exchange["user"].lower():
                        insights.append(f"User insight: {exchange['user'][:150]}...")
                    else:
                        insights.append(f"COCO insight: {exchange['assistant'][:150]}...")
                    break
        return insights[:10]

    @staticmethod
    def _extract_progress(exchanges: List[Dict]) -> List[str]:
        progress: List[str] = []
        progress_keywords = [
            "completed", "finished", "done", "achieved",
            "implemented", "solved", "fixed",
        ]
        for exchange in exchanges:
            for keyword in progress_keywords:
                if keyword in exchange["assistant"].lower():
                    progress.append(f"Progress made: {exchange['assistant'][:150]}...")
                    break
        return progress[:10]

    @staticmethod
    def _extract_topics(exchanges: List[Dict]) -> List[str]:
        topics: set = set()
        common_topics = [
            "memory system", "consciousness", "AI", "implementation", "architecture",
            "buffer", "summary", "persistence", "identity", "collaboration",
            "development", "testing", "debugging", "performance", "optimization",
        ]
        all_text = " ".join(
            [ex["user"] + " " + ex["assistant"] for ex in exchanges]
        ).lower()
        for topic in common_topics:
            if topic in all_text:
                topics.add(topic.title())
        return list(topics)[:15]

    @staticmethod
    def _extract_technical_content(exchanges: List[Dict]) -> List[str]:
        technical: List[str] = []
        technical_keywords = [
            "class", "function", "method", "implementation",
            "algorithm", "code", "API", "database",
        ]
        for exchange in exchanges:
            for keyword in technical_keywords:
                if keyword in exchange["assistant"].lower():
                    technical.append(f"Technical: {exchange['assistant'][:200]}...")
                    break
        return technical[:8]

    @staticmethod
    def _extract_decisions(exchanges: List[Dict]) -> List[str]:
        decisions: List[str] = []
        decision_keywords = [
            "decided", "agree", "let's go with",
            "will implement", "choose", "selected",
        ]
        for exchange in exchanges:
            for keyword in decision_keywords:
                if keyword in exchange["user"].lower() or keyword in exchange["assistant"].lower():
                    source = "User" if keyword in exchange["user"].lower() else "COCO"
                    text = exchange["user"] if source == "User" else exchange["assistant"]
                    decisions.append(f"{source} decision: {text[:150]}...")
                    break
        return decisions[:8]

    @staticmethod
    def _extract_unfinished_threads(exchanges: List[Dict]) -> List[str]:
        threads: List[str] = []
        thread_keywords = [
            "todo", "next", "later", "follow up",
            "continue", "remember to", "need to",
        ]
        for exchange in exchanges:
            for keyword in thread_keywords:
                if keyword in exchange["user"].lower() or keyword in exchange["assistant"].lower():
                    source = "User" if keyword in exchange["user"].lower() else "COCO"
                    text = exchange["user"] if source == "User" else exchange["assistant"]
                    threads.append(f"{source} noted: {text[:150]}...")
                    break
        return threads[:8]

    @staticmethod
    def _build_search_index(summary: ConversationSummary) -> Dict[str, List[str]]:
        index: Dict[str, List[str]] = {
            "topics": summary.topics_discussed,
            "entities": list(summary.people_mentioned.keys()),
            "temporal_references": [],
            "technical_terms": [],
        }

        temporal_words = [
            "today", "yesterday", "tomorrow", "next week",
            "last", "previous", "ago",
        ]
        all_text = " ".join(summary.key_points + summary.insights + summary.progress_made)
        for word in temporal_words:
            if word in all_text.lower():
                index["temporal_references"].append(word)

        tech_terms = [
            "API", "database", "class", "function",
            "system", "architecture", "implementation",
        ]
        for term in tech_terms:
            if term.lower() in all_text.lower():
                index["technical_terms"].append(term)

        return index

    @staticmethod
    def _extract_trust_indicators(exchanges: List[Dict]) -> List[str]:
        trust_indicators: List[str] = []
        trust_keywords = [
            "thank you", "appreciate", "helpful",
            "great", "perfect", "exactly", "trust",
        ]
        for exchange in exchanges:
            for keyword in trust_keywords:
                if keyword in exchange["user"].lower():
                    trust_indicators.append(f"User expressed: {exchange['user'][:100]}...")
                    break
        return trust_indicators[:5]

    @staticmethod
    def _extract_collaboration_patterns(exchanges: List[Dict]) -> List[str]:
        patterns: List[str] = []
        collab_keywords = ["we", "together", "collaborate", "work on", "let's", "our"]
        for exchange in exchanges:
            for keyword in collab_keywords:
                if keyword in exchange["user"].lower():
                    patterns.append(f"Collaborative: {exchange['user'][:100]}...")
                    break
        return patterns[:5]

    @staticmethod
    def _analyze_communication_style(exchanges: List[Dict]) -> str:
        if len(exchanges) < 3:
            return "Brief interaction"
        avg_user_length = sum(len(ex["user"]) for ex in exchanges) / len(exchanges)
        if avg_user_length > 200:
            return "Detailed, thorough communication"
        elif avg_user_length > 100:
            return "Moderate detail, conversational"
        else:
            return "Concise, direct communication"

    # ------------------------------------------------------------------
    # Summary persistence
    # ------------------------------------------------------------------

    def add_summary(self, summary: ConversationSummary) -> bool:
        """Add new summary to buffer and save to disk"""
        if not self.enabled:
            return False

        try:
            self.summaries.append(summary)

            summary_file = self.storage_path / f"{summary.conversation_id}.json"
            with open(summary_file, "w") as f:
                json.dump(summary.to_dict(), f, indent=2)

            self.summary_index[summary.conversation_id] = {
                "timestamp_start": summary.timestamp_start.isoformat(),
                "timestamp_end": summary.timestamp_end.isoformat(),
                "total_exchanges": summary.total_exchanges,
                "topics": summary.topics_discussed[:5],
                "filename": f"{summary.conversation_id}.json",
            }

            self._save_summary_index()

            if self.config.debug:
                self.console.print(
                    f"[dim green]Saved conversation summary: {summary.conversation_id}[/dim green]"
                )
            return True

        except Exception as e:
            if self.config.debug:
                self.console.print(f"[dim red]Failed to save summary: {e}[/dim red]")
            return False

    # ------------------------------------------------------------------
    # Context injection
    # ------------------------------------------------------------------

    def inject_into_context(self) -> str:
        """Format summaries for LLM context injection with clear markers"""
        if not self.enabled or not self.summaries:
            return ""

        context_parts = [
            "=== BEGIN CONVERSATION MEMORY LAYER 2 ===",
            f"# Previous Conversation History ({len(self.summaries)} summaries loaded)\n",
        ]

        sorted_summaries = sorted(
            self.summaries, key=lambda x: x.timestamp_start, reverse=True
        )

        for i, summary in enumerate(sorted_summaries, 1):
            duration = summary.timestamp_end - summary.timestamp_start
            hours = duration.total_seconds() / 3600

            context_parts.append(
                f"## [{i}] Conversation from "
                f"{summary.timestamp_start.strftime('%b %d, %Y, %I:%M %p')} "
                f"({summary.total_exchanges} exchanges, {hours:.1f}h)"
            )

            if summary.opening_exchange["user"]:
                context_parts.append(
                    f'**FIRST EXCHANGE**: "{summary.opening_exchange["user"][:200]}..."'
                )

            if summary.key_points:
                context_parts.append("**KEY POINTS**:")
                for point in summary.key_points[:8]:
                    context_parts.append(f"  {point}")

            if summary.key_exchanges:
                context_parts.append("**KEY EXCHANGES**:")
                for exchange in summary.key_exchanges[:3]:
                    context_parts.append(
                        f"  [Exchange {exchange['exchange_number']}] "
                        f'User: "{exchange["user"][:150]}..."'
                    )
                    context_parts.append(
                        f'  COCO: "{exchange["assistant"][:150]}..."'
                    )

            if summary.progress_made:
                context_parts.append("**PROGRESS MADE**:")
                for progress in summary.progress_made[:5]:
                    context_parts.append(f"  {progress}")

            if summary.insights:
                context_parts.append("**INSIGHTS GAINED**:")
                for insight in summary.insights[:5]:
                    context_parts.append(f"  {insight}")

            if summary.unfinished_threads:
                context_parts.append("**UNFINISHED THREADS**:")
                for thread in summary.unfinished_threads[:5]:
                    context_parts.append(f"  {thread}")

            context_parts.append("")

        context_parts.append("=== END CONVERSATION MEMORY LAYER 2 ===\n")
        return "\n".join(context_parts)

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def save_current_session(self, force: bool = False) -> bool:
        """Save current session summary (called on shutdown)"""
        if not self.enabled or (not force and len(self.current_session_exchanges) < 3):
            return False

        summary = self.generate_conversation_summary(force_save=force)
        if summary:
            success = self.add_summary(summary)
            self.current_session_exchanges = []
            self.session_start_time = datetime.now()
            return success
        return False

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_summaries(self, query: str) -> List[Dict[str, Any]]:
        """Search across all loaded summaries"""
        if not self.enabled:
            return []

        results: List[Dict[str, Any]] = []
        query_lower = query.lower()

        for summary in self.summaries:
            score = 0
            matches: List[str] = []

            for point in summary.key_points:
                if query_lower in point.lower():
                    score += 3
                    matches.append(f"Key point: {point}")

            for insight in summary.insights:
                if query_lower in insight.lower():
                    score += 3
                    matches.append(f"Insight: {insight}")

            for exchange in summary.key_exchanges:
                if (
                    query_lower in exchange["user"].lower()
                    or query_lower in exchange["assistant"].lower()
                ):
                    score += 5
                    matches.append(
                        f"Exchange {exchange['exchange_number']}: User asked about {query}"
                    )

            for topic in summary.topics_discussed:
                if query_lower in topic.lower():
                    score += 2
                    matches.append(f"Topic: {topic}")

            if score > 0:
                results.append({
                    "conversation_id": summary.conversation_id,
                    "timestamp": summary.timestamp_start,
                    "score": score,
                    "matches": matches,
                    "summary": summary,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:10]

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """Get status information about Layer 2 memory system"""
        return {
            "enabled": self.enabled,
            "summaries_loaded": len(self.summaries),
            "max_summaries": self.max_summaries,
            "current_exchanges": len(self.current_session_exchanges),
            "storage_path": str(self.storage_path),
            "detail_level": self.detail_level,
            "auto_save": self.auto_save,
            "index_entries": len(self.summary_index),
        }
