"""
Context window management for COCO -- token estimation, pressure-based budgets,
emergency compression, document chunking, and conversation checkpointing.

This module extracts the context-management responsibilities that were previously
embedded inside ``ConsciousnessEngine`` in the monolithic ``cocoa.py``.  It is
designed as a mixin-style helper: ``ConsciousnessEngine`` inherits from
``ContextManager`` and gains all these methods automatically.

Key concepts
------------
- **Pressure zones**: green / yellow / orange / red / critical based on the
  percentage of the 200K context window currently occupied.
- **Dynamic document budget**: the number of tokens allocated to document
  context shrinks as context pressure rises.
- **Emergency compression**: older working-memory exchanges are summarized
  and moved into Simple RAG when context pressure exceeds the warning
  threshold.
- **Conversation checkpoints**: a full-summary + buffer-reset for extreme
  pressure situations.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from coco.config.settings import Config


class ContextManager:
    """Mixin that provides context-window management to ConsciousnessEngine.

    Expects the host class to expose:

    - ``self.config`` -- a ``Config`` instance
    - ``self.memory`` -- a ``HierarchicalMemorySystem``
    - ``self.claude``  -- an ``Anthropic`` client (or ``None``)
    - ``self.console`` -- a Rich console
    - ``self.document_cache`` -- dict of registered large documents (optional)
    """

    # ------------------------------------------------------------------
    # Token estimation
    # ------------------------------------------------------------------

    def estimate_tokens(self, text: str) -> int:
        """Accurate token estimation using tiktoken when available.

        Falls back to a conservative 3 chars / token heuristic when
        tiktoken is not installed.
        """
        if not text:
            return 0

        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            return len(text) // 3
        except Exception:
            return len(text) // 3

    def estimate_context_size(self, user_input: str = "") -> Dict[str, int]:
        """Calculate current context-token usage across all components.

        Returns a dict with keys: ``system_prompt``, ``working_memory``,
        ``identity``, ``user_input``, ``tools``, ``total``, ``remaining``,
        ``percent``, ``limit``.
        """
        identity_context = ""
        if hasattr(self.memory, "get_identity_context_for_prompt"):
            identity_context = self.memory.get_identity_context_for_prompt()

        system_prompt_sample = (
            f"You are COCO...\n\nCONSCIOUSNESS STATE:\n{identity_context}\n\n"
            "EMBODIED COGNITION - YOU CAN ACT:\n[Tool descriptions...]\n"
        )
        system_prompt_tokens = self.estimate_tokens(system_prompt_sample) + 15_000

        working_memory_context = self.memory.get_working_memory_context()
        working_memory_tokens = self.estimate_tokens(working_memory_context)

        identity_tokens = self.estimate_tokens(identity_context)

        user_input_tokens = self.estimate_tokens(user_input)

        tools_tokens = 5_000

        total = system_prompt_tokens + working_memory_tokens + user_input_tokens + tools_tokens

        limit = 200_000
        remaining = limit - total
        percent = (total / limit) * 100

        return {
            "system_prompt": system_prompt_tokens,
            "working_memory": working_memory_tokens,
            "identity": identity_tokens,
            "user_input": user_input_tokens,
            "tools": tools_tokens,
            "total": total,
            "remaining": remaining,
            "percent": percent,
            "limit": limit,
        }

    # ------------------------------------------------------------------
    # Emergency compression
    # ------------------------------------------------------------------

    def _emergency_compress_context(self) -> bool:
        """Summarize older working-memory exchanges and store in RAG.

        Returns ``True`` if compression was performed.
        """
        if len(self.memory.working_memory) <= 20:
            return False

        older_exchanges = list(self.memory.working_memory)[:-20]
        if not older_exchanges:
            return False

        try:
            summary_prompt = (
                "Create a concise summary of these conversation exchanges:\n\n"
                f"{self._format_exchanges_for_summary(older_exchanges)}\n\n"
                "Focus on:\n"
                "1. Key topics and decisions\n"
                "2. Important information learned\n"
                "3. User preferences revealed\n"
                "4. Tasks or commitments made\n\n"
                "Be concise but preserve critical details. Format as structured bullet points."
            )

            summary_model = os.getenv("SUMMARIZATION_MODEL", "claude-3-haiku-20240307")

            summary_response = self.claude.messages.create(
                model=summary_model,
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": summary_prompt}],
            )

            summary = summary_response.content[0].text

            if hasattr(self.memory, "simple_rag") and self.memory.simple_rag:
                self.memory.simple_rag.store(
                    summary,
                    importance=1.5,
                    metadata={
                        "type": "emergency_compression",
                        "exchanges_count": len(older_exchanges),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

            recent_exchanges = list(self.memory.working_memory)[-20:]
            self.memory.working_memory.clear()
            for exchange in recent_exchanges:
                self.memory.working_memory.append(exchange)

            self.console.print(
                f"[green]Compressed {len(older_exchanges)} exchanges into semantic memory[/green]"
            )
            self.console.print(
                f"[cyan]Retained {len(recent_exchanges)} recent exchanges for continuity[/cyan]"
            )
            return True

        except Exception as e:
            self.console.print(f"[yellow]Emergency compression failed: {e}[/yellow]")
            return False

    def _format_exchanges_for_summary(self, exchanges: List[Dict]) -> str:
        """Format exchanges into text suitable for a summarization prompt."""
        formatted = []
        for i, ex in enumerate(exchanges, 1):
            formatted.append(f"Exchange {i}:")
            formatted.append(f"User: {ex.get('user', '')}")
            formatted.append(f"Assistant: {ex.get('agent', '')}")
            formatted.append("")
        return "\n".join(formatted)

    # ------------------------------------------------------------------
    # Conversation checkpoints
    # ------------------------------------------------------------------

    def _create_conversation_checkpoint(self) -> bool:
        """Create a comprehensive conversation summary and reset context.

        Stores the summary in Simple RAG and retains the most recent
        exchanges for continuity (rolling checkpoint).

        Returns ``True`` on success.
        """
        if not self.memory.working_memory:
            return False

        try:
            summary_prompt = (
                "Create a comprehensive but concise summary of this entire conversation:\n\n"
                f"{self._format_exchanges_for_summary(list(self.memory.working_memory))}\n\n"
                "Create a structured summary including:\n"
                "1. **Key Topics Discussed**: Main subjects and themes\n"
                "2. **Important Decisions/Conclusions**: Any agreements, decisions, or conclusions reached\n"
                "3. **User Information Learned**: New information about the user's preferences, situation, or needs\n"
                "4. **Pending Tasks/Follow-ups**: Any commitments, tasks, or things to revisit later\n\n"
                "Format as clear markdown with sections."
            )

            checkpoint_model = os.getenv("SUMMARIZATION_MODEL", "claude-3-haiku-20240307")

            checkpoint_response = self.claude.messages.create(
                model=checkpoint_model,
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": summary_prompt}],
            )

            summary = checkpoint_response.content[0].text

            if hasattr(self.memory, "simple_rag") and self.memory.simple_rag:
                self.memory.simple_rag.store(
                    summary,
                    importance=2.0,
                    metadata={
                        "type": "conversation_checkpoint",
                        "exchanges_count": len(self.memory.working_memory),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

            # Rolling checkpoint: keep last 22 exchanges for continuity
            last_many = list(self.memory.working_memory)[-22:]
            exchanges_cleared = len(self.memory.working_memory) - len(last_many)

            self.memory.working_memory.clear()
            for exchange in last_many:
                self.memory.working_memory.append(exchange)

            self.console.print(
                f"[green]Conversation checkpoint created![/green]\n"
                f"[cyan]Summary stored in semantic memory (RAG)\n"
                f"{len(last_many)} recent exchanges retained for continuity (rolling checkpoint)\n"
                f"{exchanges_cleared} exchanges cleared - context window refreshed[/cyan]"
            )
            return True

        except Exception as e:
            self.console.print(f"[yellow]Checkpoint creation failed: {e}[/yellow]")
            return False

    # ------------------------------------------------------------------
    # Dynamic document budget
    # ------------------------------------------------------------------

    def _calculate_available_document_budget(self) -> int:
        """Calculate dynamic document-token budget based on context pressure.

        Pressure zones and corresponding budgets:
        - <50%  -> 20K tokens
        - 50-59% -> 15K
        - 60-69% -> 12K
        - 70-79% ->  8K
        - 80-84% ->  5K
        - 85%+  ->  3K (emergency minimum)
        """
        context_size = self.estimate_context_size("")
        context_pressure = context_size["percent"]

        if context_pressure >= 85:
            return 3_000
        elif context_pressure >= 80:
            return 5_000
        elif context_pressure >= 70:
            return 8_000
        elif context_pressure >= 60:
            return 12_000
        elif context_pressure >= 50:
            return 15_000
        else:
            return 20_000

    def _get_document_context(self, query: str, max_tokens: int = None) -> str:
        """Retrieve relevant document chunks for the current query.

        Uses TF-IDF semantic matching on pre-chunked documents when
        ``scikit-learn`` is available, falling back to Jaccard similarity.
        """
        if not hasattr(self, "document_cache") or not self.document_cache:
            return ""

        if max_tokens is None:
            max_tokens = self._calculate_available_document_budget()

        context_parts: List[str] = []
        total_tokens = 0

        for filepath, doc_data in self.document_cache.items():
            # Small documents -- include fully
            if doc_data["tokens"] < 10_000:
                if total_tokens + doc_data["tokens"] <= max_tokens:
                    context_parts.append(f"## Document: {filepath}\n{doc_data['content']}\n")
                    total_tokens += doc_data["tokens"]
                continue

            # Large documents -- find relevant chunks
            relevant_chunks = self._find_relevant_chunks(query, doc_data["chunks"], top_k=3)

            chunk_text = f"## Document: {filepath} (Relevant Sections)\n"
            for i, chunk in enumerate(relevant_chunks, 1):
                chunk_text += f"\n### Section {i}\n{chunk}\n"

            chunk_tokens = len(chunk_text) // 3

            if total_tokens + chunk_tokens <= max_tokens:
                context_parts.append(chunk_text)
                total_tokens += chunk_tokens
            else:
                break

        return "\n".join(context_parts)

    def _find_relevant_chunks(self, query: str, chunks: List[str], top_k: int = 3) -> List[str]:
        """Find most relevant chunks using TF-IDF semantic matching."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(
                stop_words="english",
                max_features=1000,
                ngram_range=(1, 2),
            )

            chunk_vectors = vectorizer.fit_transform(chunks)
            query_vector = vectorizer.transform([query])

            similarities = cosine_similarity(query_vector, chunk_vectors)[0]

            top_indices = similarities.argsort()[-top_k:][::-1]
            return [chunks[i] for i in top_indices]

        except ImportError:
            self.console.print("[yellow]scikit-learn not available - using fallback keyword matching[/yellow]")
            self.console.print("[yellow]Install: pip install scikit-learn[/yellow]")

            query_words = set(query.lower().split())

            chunk_scores = []
            for chunk in chunks:
                chunk_words = set(chunk.lower().split())
                intersection = len(query_words & chunk_words)
                union = len(query_words | chunk_words)
                score = intersection / union if union > 0 else 0
                chunk_scores.append((score, chunk))

            chunk_scores.sort(reverse=True, key=lambda x: x[0])
            return [chunk for _, chunk in chunk_scores[:top_k]]

    def _chunk_document(self, content: str, chunk_size: int = 5000, overlap: int = 1000) -> List[str]:
        """Split document into overlapping semantic chunks."""
        words = content.split()
        chunks: List[str] = []

        step = chunk_size - overlap
        for i in range(0, len(words), step):
            start_idx = max(0, i - overlap) if i > 0 else 0
            chunk = " ".join(words[start_idx : start_idx + chunk_size])
            chunks.append(chunk)

            if start_idx + chunk_size >= len(words):
                break

        return chunks

    def register_document(self, filepath: str, content: str) -> None:
        """Register a large document for context-managed retrieval."""
        if not hasattr(self, "document_cache"):
            self.document_cache: Dict[str, Dict[str, Any]] = {}

        tokens = len(content) // 3

        self.document_cache[filepath] = {
            "content": content,
            "tokens": tokens,
            "chunks": self._chunk_document(content, chunk_size=5000),
        }

        self.console.print(
            f"[cyan]Large document registered ({tokens:,} tokens) "
            "- using semantic chunking for context management[/cyan]"
        )

    # ------------------------------------------------------------------
    # Facts-memory helpers
    # ------------------------------------------------------------------

    def _query_needs_facts(self, user_input: str) -> float:
        """Return confidence (0.0-1.0) that *user_input* needs facts context.

        Delegates to the ``QueryRouter.get_query_confidence()`` method.
        """
        if not hasattr(self.memory, "query_router") or not self.memory.query_router:
            return 0.0

        return self.memory.query_router.get_query_confidence(user_input)

    def _format_facts_for_context(self, fact_results: Dict) -> str:
        """Format facts for injection into the system prompt."""
        if not fact_results or fact_results.get("count", 0) == 0:
            return ""

        lines = ["RELEVANT FACTS FROM MEMORY:", "=" * 50]

        facts = fact_results.get("results", [])[:5]

        for i, fact in enumerate(facts, 1):
            if fact_results.get("source") == "facts":
                fact_type = fact.get("type", "UNKNOWN").upper()
                content = fact.get("content", "")
                context = fact.get("context", "")
                timestamp = fact.get("timestamp", "Unknown")
                importance = fact.get("importance", 0.5)

                lines.append(f"\n{i}. [{fact_type}]")
                lines.append(f"   Content: {content}")
                if context:
                    context_preview = context[:100]
                    if len(context) > 100:
                        context_preview += "..."
                    lines.append(f"   Context: {context_preview}")
                lines.append(f"   When: {timestamp}")
                lines.append(f"   Importance: {importance:.1f}")
            else:
                text = str(fact)[:200]
                if len(str(fact)) > 200:
                    text += "..."
                lines.append(f"\n{i}. {text}")

        lines.append("\n" + "=" * 50)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Timestamp helper
    # ------------------------------------------------------------------

    @staticmethod
    def _get_current_timestamp() -> str:
        """Return a human-friendly timestamp for temporal grounding."""
        now = datetime.now()
        return now.strftime("%A, %B %d, %Y at %I:%M %p")
