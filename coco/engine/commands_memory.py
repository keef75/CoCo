"""
Memory, recall, facts, knowledge-graph, RAG, and help slash-command handlers.

Covers ``/memory``, ``/recall``, ``/facts``, ``/facts-stats``, ``/kg``,
``/rag``, ``/docs``, ``/sent``, ``/help``, ``/commands``, Layer-2 summary
buffer commands, and the comprehensive command guide.

Extracted from ``cocoa.py`` lines ~9613-9785, ~9903-10025, ~11103-11226,
~14592-15919, and the help/guide methods.
"""

from __future__ import annotations

import logging
import os
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class MemoryCommandHandler:
    """
    Handles slash commands related to memory, recall, knowledge-graph,
    RAG, documents, sent-emails, help, and the command guide.

    Parameters
    ----------
    engine : Any
        Reference to the main engine with ``.memory``, ``.tools``,
        ``.config``, ``.console``, and optional consciousness sub-systems.
    """

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    # ------------------------------------------------------------------
    # Shortcuts
    # ------------------------------------------------------------------

    @property
    def _memory(self) -> Any:
        return self.engine.memory

    @property
    def _console(self) -> Any:
        return self.engine.console

    @property
    def _config(self) -> Any:
        return self.engine.config

    @staticmethod
    def _panel(text: Any, title: str = "", style: str = "red") -> Any:
        from rich.panel import Panel

        return Panel(text, title=title, border_style=style)

    # ==================================================================
    # /memory  (central sub-command dispatcher)
    # ==================================================================

    def handle_memory_commands(self, args: str) -> Any:
        """Dispatch ``/memory <sub>`` commands."""
        if not args:
            return self.show_memory_help()

        parts = args.split(maxsplit=1)
        subcmd = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ""

        if subcmd == "status":
            return self.show_memory_status()
        elif subcmd == "config":
            return self.show_memory_config()
        elif subcmd == "buffer":
            return self._handle_buffer(subargs)
        elif subcmd == "summary":
            return self._handle_summary(subargs)
        elif subcmd == "session":
            return self._handle_session(subargs)
        elif subcmd == "stats":
            return self.show_memory_statistics()
        elif subcmd == "layers":
            return self.show_memory_layers()
        elif subcmd == "emergency-cleanup":
            return self.emergency_cleanup_memory()
        elif subcmd == "health":
            return self.show_memory_health()
        elif subcmd == "pressure":
            return self.show_memory_pressure()
        else:
            return self.show_memory_help()

    # ------------------------------------------------------------------
    # Buffer / summary / session sub-sub-commands
    # ------------------------------------------------------------------

    def _handle_buffer(self, subargs: str) -> Any:
        if subargs == "show":
            return self.show_buffer_contents()
        elif subargs == "clear":
            self._memory.working_memory.clear()
            return "[green]Buffer memory cleared[/green]"
        elif subargs.startswith("resize"):
            try:
                size = int(subargs.split()[1])
                self._memory.memory_config.buffer_size = size if size > 0 else None
                buffer_size = size if size > 0 else None
                old = list(self._memory.working_memory)
                self._memory.working_memory = deque(old, maxlen=buffer_size)
                label = str(size) if size > 0 else "unlimited"
                return f"[green]Buffer resized to {label}[/green]"
            except (ValueError, IndexError):
                return "[red]Usage: /memory buffer resize <size>[/red]"
        return self.show_memory_help()

    def _handle_summary(self, subargs: str) -> Any:
        if subargs == "trigger":
            self._memory.trigger_buffer_summarization()
            return "[green]Buffer summarization triggered[/green]"
        elif subargs == "show":
            return self.show_recent_summaries()
        return self.show_memory_help()

    def _handle_session(self, subargs: str) -> Any:
        if subargs == "save":
            self._memory.save_session_summary()
            return "[green]Session summary saved[/green]"
        elif subargs == "load":
            self._memory.load_session_context()
            return "[green]Session context loaded[/green]"
        return self.show_memory_help()

    # ==================================================================
    # Memory status / config / stats / layers / health / pressure
    # ==================================================================

    def show_memory_status(self) -> Any:
        """Context-window usage and memory configuration."""
        from rich.markdown import Markdown

        config = self._memory.memory_config
        buffer_size = len(self._memory.working_memory)
        max_buffer = config.buffer_size or "unlimited"

        context_size = self.engine.estimate_context_size("")
        usage_percent = context_size["percent"]

        if usage_percent < 70:
            usage_color, usage_status = "green", "Normal"
        elif usage_percent < 85:
            usage_color, usage_status = "yellow", "Warning"
        else:
            usage_color, usage_status = "red", "Critical"

        cursor = self._memory.conn.execute("SELECT COUNT(*) FROM episodes")
        total_episodes = cursor.fetchone()[0]
        cursor = self._memory.conn.execute("SELECT COUNT(*) FROM summaries")
        total_summaries = cursor.fetchone()[0]

        rag_text = ""
        if hasattr(self._memory, "simple_rag") and self._memory.simple_rag:
            rs = self._memory.simple_rag.get_stats()
            rag_text = (
                f"\n**Semantic Memory (RAG):**\n"
                f"- Total Memories: {rs.get('total_memories', 0)}\n"
                f"- Checkpoints: {rs.get('checkpoints', 0)}\n"
                f"- Emergency Compressions: {rs.get('compressions', 0)}\n"
            )

        recs = self._get_memory_recommendations(context_size)

        md = (
            f"# Memory & Context Status\n\n"
            f"**Context Window Usage:** {usage_status}\n"
            f"- Total Tokens: {context_size['total']:,} / {context_size['limit']:,} ({usage_percent:.1f}%)\n"
            f"- System Prompt: ~{context_size['system_prompt']:,} tokens\n"
            f"- Working Memory: ~{context_size['working_memory']:,} tokens\n"
            f"- Identity Context: ~{context_size['identity']:,} tokens\n"
            f"- Available: {context_size['remaining']:,} tokens\n\n"
            f"**Buffer Memory:**\n"
            f"- Current Size: {buffer_size} / {max_buffer}\n"
            f"- Truncate Threshold: {config.buffer_truncate_at}\n"
            f"{rag_text}\n"
            f"**Summary Memory:**\n"
            f"- Total Summaries: {total_summaries}\n\n"
            f"**Database:**\n"
            f"- Total Episodes: {total_episodes}\n"
            f"- Session: {self._memory.session_id}\n\n"
            f"**Recommendations:**\n{recs}"
        )

        return self._panel(Markdown(md), title="Memory & Context Status", style="bright_cyan")

    def show_memory_config(self) -> Any:
        from rich.markdown import Markdown

        cfg = self._memory.memory_config
        md = (
            f"# Memory Configuration\n\n"
            f"**Buffer Settings:**\n"
            f"- Buffer Size: {cfg.buffer_size or 'Unlimited'}\n"
            f"- Truncate At: {cfg.buffer_truncate_at}\n\n"
            f"**Summary Settings:**\n"
            f"- Window Size: {cfg.summary_window_size}\n"
            f"- Overlap: {cfg.summary_overlap}\n"
            f"- Max in Memory: {cfg.max_summaries_in_memory}\n\n"
            f"**Models:**\n"
            f"- Summarization: {cfg.summarization_model}\n"
            f"- Embedding: {cfg.embedding_model}"
        )
        return self._panel(Markdown(md), title="Memory Config", style="yellow")

    def show_memory_statistics(self) -> Any:
        from rich.markdown import Markdown

        cursor = self._memory.conn.execute("SELECT COUNT(*) FROM episodes")
        total_episodes = cursor.fetchone()[0]
        in_buffer = len(self._memory.working_memory)

        cursor = self._memory.conn.execute("SELECT COUNT(*) FROM summaries")
        total_summaries = cursor.fetchone()[0]

        cursor = self._memory.conn.execute("SELECT COUNT(*) FROM gist_memories")
        total_gists = cursor.fetchone()[0]

        buffer_pct = (in_buffer / max(1, total_episodes)) * 100
        max_buf = self._memory.memory_config.buffer_size or 100

        md = (
            f"# Memory Statistics\n\n"
            f"**Episode Distribution:**\n"
            f"- Total Episodes: {total_episodes}\n"
            f"- In Buffer: {in_buffer} ({buffer_pct:.1f}%)\n\n"
            f"**Memory Hierarchy:**\n"
            f"- Buffer Memories: {in_buffer}\n"
            f"- Summary Memories: {total_summaries}\n"
            f"- Gist Memories: {total_gists}\n\n"
            f"**Ratios:**\n"
            f"- Compression Ratio: {(total_episodes / max(1, total_summaries)):.1f}:1\n"
            f"- Active Buffer Usage: {(in_buffer / max(1, max_buf)):.1%}"
        )
        return self._panel(Markdown(md), title="Memory Statistics", style="bright_green")

    def show_memory_layers(self) -> Any:
        """Three-layer memory architecture status."""
        from rich.markdown import Markdown

        buf_size = len(self._memory.working_memory)
        buf_sample = ""
        if buf_size > 0:
            recent = list(self._memory.working_memory)[-1]
            buf_sample = f"{recent['user'][:60]}..."

        rag_status = "Not initialized"
        rag_memories = 0
        rag_sample = ""
        if hasattr(self._memory, "simple_rag") and self._memory.simple_rag:
            rs = self._memory.simple_rag.get_stats()
            rag_memories = rs["total_memories"]
            rag_status = f"Active ({rag_memories} memories)"
            memories = self._memory.simple_rag.retrieve("memory system knowledge", k=1)
            if memories:
                rag_sample = f"{memories[0][:60]}..."

        identity_files: list[str] = []
        workspace = Path(self._config.workspace)
        for fn in ("COCO.md", "USER_PROFILE.md", "previous_conversation.md"):
            fp = workspace / fn
            if fp.exists():
                identity_files.append(f"{fn} ({fp.stat().st_size:,} bytes)")

        working_ctx_size = len(self._memory.get_working_memory_context())
        identity_ctx_size = 0
        if hasattr(self._memory, "get_identity_context_for_prompt"):
            identity_ctx_size = len(self._memory.get_identity_context_for_prompt())

        md = (
            f"# Three-Layer Memory Architecture\n\n"
            f"## Layer 1: Episodic Buffer\n"
            f"**Size:** {buf_size} exchanges\n"
            f"**Injected:** {working_ctx_size:,} chars\n"
            f"**Sample:** {buf_sample or 'No exchanges yet'}\n\n"
            f"## Layer 2: Simple RAG\n"
            f"**Status:** {rag_status}\n"
            f"**Sample:** {rag_sample or 'No memories yet'}\n\n"
            f"## Layer 3: Markdown Identity\n"
            f"**Files:** {len(identity_files)}/3 loaded\n"
            + "\n".join(f"- {f}" for f in identity_files)
            + f"\n\n## Integration Summary\n"
            f"- Layer 1+2: ~{working_ctx_size:,} chars (messages)\n"
            f"- Layer 3: ~{identity_ctx_size:,} chars (system prompt)\n"
            f"- **Total: ~{working_ctx_size + identity_ctx_size:,} chars**"
        )
        return self._panel(Markdown(md), title="Three-Layer Memory System", style="bright_magenta")

    def show_memory_health(self) -> Any:
        """Detailed memory health diagnostics."""
        from rich.markdown import Markdown

        cfg = self._memory.memory_config
        buf_actual = len(self._memory.working_memory)
        buf_expected = cfg.buffer_size or 100

        context = self._memory.get_working_memory_context()
        context_tokens = len(context) // 3

        kg_health = "Not initialized"
        kg_errors = 0
        if hasattr(self._memory, "personal_kg") and self._memory.personal_kg:
            try:
                ks = self._memory.personal_kg.get_knowledge_status()
                kg_health = f"Active ({ks['total_entities']} entities)"
            except Exception as exc:
                kg_health = f"Error: {str(exc)[:50]}"
                kg_errors = 1

        rag_health = "Not initialized"
        if hasattr(self._memory, "simple_rag") and self._memory.simple_rag:
            try:
                rs = self._memory.simple_rag.get_stats()
                rag_health = f"Active ({rs['total_memories']} memories)"
            except Exception as exc:
                rag_health = f"Error: {str(exc)[:50]}"

        # Summarization schema check
        try:
            cursor = self._memory.conn.execute("PRAGMA table_info(episodes)")
            columns = [row[1] for row in cursor.fetchall()]
            if "summarized" in columns:
                summ_health = "Database schema OK"
            else:
                summ_health = "Missing 'summarized' column (run migration)"
        except Exception as exc:
            summ_health = f"Database error: {str(exc)[:50]}"

        score = 100
        if buf_actual > buf_expected:
            score -= 30
        if context_tokens > 40000:
            score -= 25
        elif context_tokens > 20000:
            score -= 15
        if kg_errors > 0:
            score -= 10
        if "Missing" in summ_health:
            score -= 20

        if score >= 90:
            grade = "Excellent"
        elif score >= 70:
            grade = "Good"
        elif score >= 50:
            grade = "Fair"
        else:
            grade = "Poor"

        md = (
            f"# Memory System Health Check\n\n"
            f"## Overall Health: {grade} ({score}/100)\n\n"
            f"### Layer 1: Episodic Buffer\n"
            f"- Actual: {buf_actual}, Expected limit: {buf_expected}\n\n"
            f"### Context Injection\n"
            f"- Size: {len(context):,} chars (~{context_tokens:,} tokens)\n\n"
            f"### Knowledge Graph\n- {kg_health}\n\n"
            f"### Simple RAG\n- {rag_health}\n\n"
            f"### Summarization\n- {summ_health}\n\n"
            f"## Quick Fixes\n"
            f"1. Emergency cleanup: /memory emergency-cleanup\n"
            f"2. Manual summarization: /memory summary trigger\n"
            f"3. Buffer resize: /memory buffer resize 50"
        )
        return self._panel(Markdown(md), title="Memory Health Diagnostics", style="bright_cyan")

    def show_memory_pressure(self) -> Any:
        """Real-time context pressure monitoring."""
        from rich.markdown import Markdown

        ctx = self.engine.estimate_context_size("")
        total = ctx["total"]
        limit = ctx["limit"]
        pct = ctx["percent"]

        if pct >= 85:
            level, color = "EMERGENCY", "red"
        elif pct >= 80:
            level, color = "CRITICAL", "bright_red"
        elif pct >= 70:
            level, color = "HIGH", "yellow"
        elif pct >= 60:
            level, color = "MEDIUM-HIGH", "bright_yellow"
        elif pct >= 50:
            level, color = "MEDIUM", "green"
        else:
            level, color = "LOW", "bright_green"

        bar_len = 40
        filled = int((pct / 100) * bar_len)
        bar = "\u2588" * filled + "\u2591" * (bar_len - filled)

        buf_size = len(self._memory.working_memory)

        md = (
            f"# Context Pressure Monitor\n\n"
            f"## Current Pressure: {level} ({pct:.1f}%)\n\n"
            f"```\n{bar}\n0%                  50%                 100%\n```\n\n"
            f"**Used**: {total:,} / {limit:,} tokens\n"
            f"**Remaining**: {ctx['remaining']:,} tokens ({100 - pct:.1f}%)\n\n"
            f"**Working Memory**: {buf_size} exchanges\n\n"
            f"## Actions Available\n"
            f"- /memory emergency-cleanup\n"
            f"- /memory health\n"
            f"- /memory summary trigger"
        )
        return self._panel(Markdown(md), title=f"Memory Pressure: {pct:.1f}%", style=color)

    def emergency_cleanup_memory(self) -> Any:
        """Aggressive cleanup for long-running sessions."""
        from rich.markdown import Markdown

        self._console.print("[yellow]Starting emergency memory cleanup...[/yellow]")

        before_buffer = len(self._memory.working_memory)
        before_episodes = self._memory.get_episode_count()

        # Trim to 50
        all_exchanges = list(self._memory.working_memory)
        if len(all_exchanges) > 50:
            self._memory.working_memory = deque(all_exchanges[-50:], maxlen=50)
            self._memory.memory_config.buffer_size = 50

        # Summarize
        try:
            self._memory.trigger_buffer_summarization()
        except Exception as exc:
            self._console.print(f"[yellow]Summarization warning: {exc}[/yellow]")

        after_buffer = len(self._memory.working_memory)

        md = (
            f"# Emergency Memory Cleanup Complete\n\n"
            f"## Before\n- Buffer: {before_buffer} exchanges\n"
            f"- Episodes: {before_episodes}\n\n"
            f"## After\n- Buffer: {after_buffer} exchanges\n\n"
            f"## Actions Taken\n"
            f"1. Trimmed working memory to last 50 exchanges\n"
            f"2. Triggered buffer summarization\n"
            f"3. Reset buffer size to 50\n\n"
            f"Run /memory health to verify"
        )
        return self._panel(Markdown(md), title="Emergency Cleanup", style="bright_yellow")

    def show_memory_help(self) -> Any:
        from rich.markdown import Markdown

        md = (
            "# Memory System Commands\n\n"
            "## Status & Configuration\n"
            "- /memory status\n- /memory config\n- /memory stats\n"
            "- /memory layers\n- /memory pressure\n\n"
            "## Buffer Operations\n"
            "- /memory buffer show\n- /memory buffer clear\n"
            "- /memory buffer resize <size>\n\n"
            "## Summary Operations\n"
            "- /memory summary show\n- /memory summary trigger\n\n"
            "## Session Operations\n"
            "- /memory session save\n- /memory session load\n\n"
            "## Emergency & Health\n"
            "- /memory emergency-cleanup\n- /memory health"
        )
        return self._panel(Markdown(md), title="Memory System", style="bright_cyan")

    def show_buffer_contents(self) -> Any:
        from rich.table import Table
        from rich.box import ROUNDED

        table = Table(title="Buffer Memory Contents", box=ROUNDED)
        table.add_column("#", style="dim", width=3)
        table.add_column("Age", style="cyan", width=8)
        table.add_column("User", style="green")
        table.add_column("Assistant", style="blue")
        table.add_column("Importance", style="magenta", width=10)

        for i, ex in enumerate(list(self._memory.working_memory)):
            try:
                ts = ex["timestamp"]
                now = datetime.now(ts.tzinfo) if ts.tzinfo else datetime.now()
                secs = (now - ts).total_seconds()
            except (TypeError, AttributeError):
                secs = 0
            age = f"{int(secs)}s" if secs < 3600 else f"{int(secs / 3600)}h"
            imp = f"{ex.get('importance', 0.5):.2f}"

            table.add_row(
                str(i + 1),
                age,
                ex["user"][:60] + ("..." if len(ex["user"]) > 60 else ""),
                ex["agent"][:60] + ("..." if len(ex["agent"]) > 60 else ""),
                imp,
            )
        return table

    def show_recent_summaries(self) -> Any:
        from rich.table import Table
        from rich.box import ROUNDED

        cursor = self._memory.conn.execute(
            "SELECT id, content, created_at, importance_score "
            "FROM summaries WHERE session_id = ? ORDER BY created_at DESC LIMIT 10",
            (self._memory.session_id,),
        )

        table = Table(title="Recent Summaries", box=ROUNDED)
        table.add_column("ID", style="dim", width=3)
        table.add_column("Created", style="cyan")
        table.add_column("Content", style="white")
        table.add_column("Importance", style="magenta", width=10)

        for row in cursor.fetchall():
            sid, content, created_at, importance = row
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                ts = dt.strftime("%H:%M:%S")
            except Exception:
                ts = str(created_at)[:8]
            table.add_row(
                str(sid), ts, content[:80] + ("..." if len(content) > 80 else ""), f"{importance:.2f}"
            )
        return table

    # ==================================================================
    # /recall
    # ==================================================================

    def handle_recall_command(self, args: str) -> Any:
        """Perfect recall with intelligent routing."""
        if not args:
            return self._panel(
                "Usage: /recall <query>\n\n"
                "Examples:\n"
                "- /recall email about project deadline\n"
                "- /recall meeting with Sarah yesterday\n"
                "- /recall task to review proposal\n\n"
                "Searches your perfect memory for exact matches",
                title="Perfect Recall",
                style="yellow",
            )

        if not hasattr(self._memory, "facts_memory") or not self._memory.facts_memory:
            return self._panel(
                "Facts memory not initialized", title="Perfect Recall", style="red"
            )

        # Ensure query router
        if not hasattr(self._memory, "query_router"):
            try:
                from memory.query_router import QueryRouter

                self._memory.query_router = QueryRouter(
                    self._memory.facts_memory,
                    self._memory.simple_rag if hasattr(self._memory, "simple_rag") else None,
                )
            except Exception:
                pass

        if hasattr(self._memory, "query_router") and self._memory.query_router:
            results = self._memory.query_router.route_query(args)
        else:
            facts = self._memory.facts_memory.search_facts(args, limit=5)
            results = {
                "source": "facts" if facts else "none",
                "results": facts,
                "count": len(facts) if facts else 0,
            }

        # Context persistence
        if results and results.get("results") and results.get("count", 0) > 0:
            try:
                summaries: list[str] = []
                for f in results["results"][:5]:
                    if isinstance(f, dict):
                        ft = f.get("type", f.get("fact_type", "UNKNOWN"))
                        summaries.append(f"[{ft}] {f.get('content', '')}")

                exchange = {
                    "user": f"/recall {args}",
                    "agent": f"Found {results['count']} facts:\n" + "\n".join(summaries[:3]),
                    "timestamp": datetime.now(),
                    "recall_results": results,
                }
                if hasattr(self._memory, "working_memory"):
                    self._memory.working_memory.append(exchange)
            except Exception:
                pass

        if results["source"] == "facts" and results["results"]:
            lines: list[str] = []
            for i, fact in enumerate(results["results"], 1):
                lines.append(f"[cyan]#{i} [{fact['type'].upper()}][/cyan]")
                lines.append(f"Content: {fact['content']}")
                if fact.get("context"):
                    preview = fact["context"][:200]
                    if len(fact["context"]) > 200:
                        preview += "..."
                    lines.append(f"Context: {preview}")
                lines.append(f"When: {fact['timestamp']}")
                lines.append(f"Importance: {fact['importance']:.1f}/1.0")
                if fact.get("access_count", 0) > 0:
                    lines.append(f"Accessed: {fact['access_count']} times")
                lines.append("")

            return self._panel(
                "\n".join(lines),
                title=f"Found {len(results['results'])} Perfect Matches",
                style="green",
            )

        return self._panel(
            f"No exact matches found for: {args}\n\n"
            "Try different keywords or use /facts to browse",
            title="No Exact Matches",
            style="yellow",
        )

    # ==================================================================
    # /facts
    # ==================================================================

    def handle_facts_command(self, args: str) -> Any:
        """Browse facts database by type."""
        if not hasattr(self._memory, "facts_memory") or not self._memory.facts_memory:
            return self._panel("Facts memory not initialized", title="Facts Database", style="red")

        fact_type = args.strip() if args else None

        if fact_type:
            facts = self._memory.facts_memory.search_facts("", fact_type=fact_type, limit=20)
            title = f"Recent {fact_type} facts"
        else:
            stats = self._memory.facts_memory.get_stats()
            facts = self._memory.facts_memory.search_facts("", limit=15)
            title = f"Recent facts ({stats['total_facts']} total)"

        if not facts:
            return self._panel(
                "No facts found\n\nFacts are extracted automatically as you use COCO.",
                title="Facts Database",
                style="yellow",
            )

        lines: list[str] = []
        current_type = None
        for fact in facts:
            if fact["type"] != current_type:
                if current_type is not None:
                    lines.append("")
                lines.append(f"[bold cyan]{fact['type'].upper()}:[/bold cyan]")
                current_type = fact["type"]
            content = fact["content"][:77] + "..." if len(fact["content"]) > 80 else fact["content"]
            stars = "*" * int(fact["importance"] * 5)
            lines.append(f"  {stars} {content}")

        lines += ["", "[dim]Use /recall <query> for specific searches[/dim]", "[dim]Use /facts-stats for detailed statistics[/dim]"]
        return self._panel("\n".join(lines), title=title, style="cyan")

    # ==================================================================
    # /facts-stats
    # ==================================================================

    def handle_facts_stats(self) -> Any:
        """Facts database analytics."""
        if not hasattr(self._memory, "facts_memory") or not self._memory.facts_memory:
            return self._panel("Facts memory not initialized", title="Facts Statistics", style="red")

        stats = self._memory.facts_memory.get_stats()
        lines = [
            "[bold]Facts Database Statistics[/bold]\n",
            f"Total Facts: {stats['total_facts']:,}",
            f"Avg Importance: {stats.get('avg_importance', 0):.2f}",
            "",
            "[bold]Facts by Type:[/bold]",
        ]

        if stats.get("breakdown"):
            for ft, count in sorted(stats["breakdown"].items(), key=lambda x: x[1], reverse=True):
                bar = "\u2588" * min(20, count // 10 + 1)
                lines.append(f"  {ft:15} {count:5,} {bar}")

        if stats.get("most_accessed"):
            lines += ["", "[bold]Most Accessed:[/bold]"]
            for item in stats["most_accessed"][:3]:
                c = item["content"][:40] + ("..." if len(item["content"]) > 40 else "")
                lines.append(f"  [{item['type']}] {c} ({item['count']} times)")

        lines += [
            "",
            "[bold]Extraction Performance:[/bold]",
            f"Session Facts: {getattr(self._memory, 'facts_extracted_count', 0):,}",
        ]

        total = stats["total_facts"]
        health = "Healthy" if total > 100 else "Building" if total > 10 else "New"
        lines.append(f"\nSystem Status: {health}")

        return self._panel("\n".join(lines), title="Facts Database Analytics", style="green")

    # ==================================================================
    # /kg  |  /knowledge
    # ==================================================================

    def handle_knowledge_command(self, command: str) -> Any:
        """Knowledge graph status, refresh, search."""
        from rich.markdown import Markdown

        if not hasattr(self._memory, "personal_kg") or not self._memory.personal_kg:
            return self._panel("Knowledge graph not initialized", title="Knowledge Graph", style="red")

        parts = command.split(maxsplit=2)
        subcmd = parts[1] if len(parts) > 1 else "status"

        if subcmd == "status":
            ks = self._memory.personal_kg.get_knowledge_status()
            types = "\n".join(f"  - {t}: {c}" for t, c in ks["entity_types"].items())
            md = (
                f"# Knowledge Graph Status\n\n"
                f"**Entities:** {ks['total_entities']}\n"
                f"**Relationships:** {ks['total_relationships']}\n"
                f"**Entity Types:**\n{types}\n\n"
                "Use /kg refresh to extract from recent conversations"
            )
            return self._panel(Markdown(md), title="Knowledge Graph", style="green")

        elif subcmd == "refresh":
            count = 0
            for ex in list(self._memory.working_memory)[-20:]:
                self._memory.personal_kg.process_conversation_exchange(ex["user"], ex["agent"])
                count += 1
            return self._panel(
                f"Processed {count} recent exchanges\n\nKnowledge graph updated",
                title="Knowledge Refresh",
                style="green",
            )

        elif subcmd == "search" and len(parts) > 2:
            context = self._memory.personal_kg.get_relevant_entities_rag(parts[2])
            return self._panel(context or "No relevant entities found", title=f"Search: '{parts[2]}'", style="cyan")

        else:
            return self._panel(
                "Knowledge Graph Commands:\n"
                "/kg (status) - Show statistics\n"
                "/kg refresh - Extract from recent conversations\n"
                "/kg search <query> - Search entities",
                title="Knowledge Graph",
                style="cyan",
            )

    # ==================================================================
    # /rag
    # ==================================================================

    def handle_rag_command(self, command: str) -> Any:
        """Simple RAG semantic memory commands."""
        from rich.markdown import Markdown

        if not hasattr(self._memory, "simple_rag") or not self._memory.simple_rag:
            return self._panel("Simple RAG not initialized", title="Simple RAG", style="red")

        parts = command.split(maxsplit=2)
        subcmd = parts[1] if len(parts) > 1 else "stats"

        if subcmd == "stats":
            s = self._memory.simple_rag.get_stats()
            md = (
                f"# Simple RAG Statistics\n\n"
                f"**Total Memories:** {s['total_memories']}\n"
                f"**Recent (24h):** {s['recent_memories']}\n\n"
                "Use /rag search <query> to search\n"
                "Use /rag add <text> to add context"
            )
            return self._panel(Markdown(md), title="Simple RAG", style="cyan")

        elif subcmd == "search" and len(parts) > 2:
            memories = self._memory.simple_rag.retrieve(parts[2], k=3)
            if memories:
                result = "Found relevant memories:\n\n"
                for i, mem in enumerate(memories, 1):
                    m = mem[:197] + "..." if len(mem) > 200 else mem
                    result += f"[{i}] {m}\n\n"
                return self._panel(result, title=f"Search: '{parts[2]}'", style="green")
            return self._panel("No relevant memories found", title=f"Search: '{parts[2]}'", style="yellow")

        elif subcmd == "add" and len(parts) > 2:
            self._memory.simple_rag.store(parts[2], importance=1.5)
            return self._panel(f"Added to semantic memory:\n{parts[2][:100]}...", title="Memory Added", style="green")

        elif subcmd == "clean":
            self._memory.simple_rag.cleanup_old_memories(days=30)
            s = self._memory.simple_rag.get_stats()
            return self._panel(f"Cleaned old memories\n\nRemaining: {s['total_memories']}", title="Cleanup", style="green")

        else:
            return self._panel(
                "Simple RAG Commands:\n"
                "/rag (stats)\n/rag search <query>\n"
                "/rag add <text>\n/rag clean",
                title="Simple RAG",
                style="cyan",
            )

    # ==================================================================
    # /remember
    # ==================================================================

    def handle_remember_command(self, args: str) -> Any:
        from rich.table import Table
        from rich.box import ROUNDED

        episodes = self._memory.recall_episodes(args or "recent", limit=5)
        table = Table(title="Episodic Memories", box=ROUNDED)
        table.add_column("Time", style="cyan")
        table.add_column("User", style="green")
        table.add_column("Response", style="blue")
        for ep in episodes:
            table.add_row(ep["timestamp"], ep["user"][:50] + "...", ep["agent"][:50] + "...")
        return table

    # ==================================================================
    # /sent-emails  |  /sent
    # ==================================================================

    def handle_sent_emails_command(self, args: str) -> Any:
        try:
            limit = 30
            if args and args.strip().isdigit():
                limit = min(int(args.strip()), 50)
            result = self.engine.tools.check_sent_emails(limit)
            return self._panel(result, title="Sent Emails", style="bright_yellow")
        except Exception as exc:
            return self._panel(f"Error: {exc}", title="Error", style="red")

    # ==================================================================
    # /docs  |  /docs-clear
    # ==================================================================

    def handle_docs_list_command(self) -> Any:
        from rich.table import Table
        from rich.box import ROUNDED
        from rich.markdown import Markdown
        from rich.console import Group

        cache = getattr(self.engine, "document_cache", None)
        if not cache:
            return self._panel(
                "**No documents currently registered**\n\n"
                "Large documents (>10K words) are automatically registered when read.",
                title="Document Cache Empty",
                style="cyan",
            )

        table = Table(title="Registered Documents", box=ROUNDED)
        table.add_column("Document", style="cyan", no_wrap=False)
        table.add_column("Size", style="yellow", justify="right")
        table.add_column("Chunks", style="green", justify="right")
        table.add_column("Tokens", style="magenta", justify="right")

        total_tokens = 0
        for fpath, dd in cache.items():
            tokens = dd["tokens"]
            chunks = len(dd["chunks"])
            words = len(dd["content"].split())
            table.add_row(fpath, f"{words:,} words", str(chunks), f"{tokens:,}")
            total_tokens += tokens

        budget = self.engine._calculate_available_document_budget()
        summary = (
            f"**Total Documents:** {len(cache)}\n"
            f"**Total Tokens:** {total_tokens:,}\n"
            f"**Available Budget:** {budget:,} tokens\n\n"
            "Use /docs-clear to remove all cached documents"
        )
        return self._panel(Group(table, Markdown(summary)), title="Document Management", style="bright_blue")

    def handle_docs_clear_command(self, args: str) -> Any:
        cache = getattr(self.engine, "document_cache", None)
        if not cache:
            return self._panel("Document cache is already empty", title="Nothing to Clear", style="cyan")

        if args.strip():
            name = args.strip()
            if name in cache:
                del cache[name]
                return self._panel(
                    f"**Document removed:** {name}\n\n**Remaining:** {len(cache)}",
                    title="Document Removed",
                    style="green",
                )
            matches = [n for n in cache if name.lower() in n.lower()]
            if matches:
                return self._panel(
                    f"**Document not found:** {name}\n\n**Did you mean?**\n" + "\n".join(f"- {m}" for m in matches[:5]),
                    title="Document Not Found",
                    style="red",
                )
            return self._panel(f"**Document not found:** {name}", title="Document Not Found", style="red")

        count = len(cache)
        cache.clear()
        return self._panel(
            f"**Document cache cleared**\n\n**Removed:** {count} document(s)",
            title="Cache Cleared",
            style="green",
        )

    # ==================================================================
    # /help
    # ==================================================================

    def get_help_panel(self) -> Any:
        """Comprehensive help panel (abbreviated -- the full version lives in the engine)."""
        from rich.markdown import Markdown

        md = (
            "# COCOA Command Reference\n\n"
            "## Memory & Learning\n"
            "- /memory - Advanced memory control\n"
            "- /recall <query> - Perfect recall\n"
            "- /facts [type] - Browse facts\n"
            "- /facts-stats - Analytics\n\n"
            "## Automation\n"
            "- /auto-status - View all automations\n"
            "- /auto-news, /auto-calendar, /auto-meetings, /auto-report, /auto-video\n\n"
            "## Twitter\n"
            "- /tweet <text> - Post with approval\n"
            "- /mentions - Recent mentions\n"
            "- /twitter-status - Rate limits\n\n"
            "## Visual & Video\n"
            "- /image - Last generated image\n"
            "- /video - Last generated video\n"
            "- /watch <url> - Watch any video\n\n"
            "## Audio\n"
            "- /speak <text> - Voice synthesis\n"
            "- /play-music on/off - Background music\n\n"
            "## System\n"
            "- /help - This reference\n"
            "- /commands - Full command center\n"
            "- /status - System status\n"
            "- /exit - End session\n"
        )
        return self._panel(Markdown(md), title="COCOA Help System", style="bright_green")

    # ==================================================================
    # /commands  |  /guide
    # ==================================================================

    def get_comprehensive_command_guide(self) -> Any:
        """Delegate to the engine's full command guide if available."""
        if hasattr(self.engine, "get_comprehensive_command_guide"):
            return self.engine.get_comprehensive_command_guide()
        return self.get_help_panel()

    # ==================================================================
    # Layer 2 summary buffer commands
    # ==================================================================

    def handle_layer2_save_summary(self, args: str) -> Any:
        if not hasattr(self._memory, "layer2_memory"):
            return self._panel("Layer 2 memory system not available", style="red")
        layer2 = self._memory.layer2_memory
        if not layer2.enabled:
            return self._panel(
                "Layer 2 Summary Buffer Memory is **DISABLED**\n\n"
                "Set ENABLE_LAYER2_MEMORY=true in .env and restart.",
                title="Layer 2 Disabled",
                style="yellow",
            )
        try:
            if len(layer2.current_session_exchanges) < 3 and not (args and args.startswith("force")):
                return self._panel(
                    f"Not enough content ({len(layer2.current_session_exchanges)} exchanges, need 3)\n\n"
                    "Use /save-summary force to save anyway.",
                    title="Insufficient Content",
                    style="yellow",
                )
            summary = layer2.generate_conversation_summary(force_save=True)
            if summary and layer2.add_summary(summary):
                from rich.table import Table
                from rich.box import ROUNDED

                table = Table(title="Layer 2 Summary Generated", box=ROUNDED)
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="bright_white")
                table.add_row("Conversation ID", summary.conversation_id)
                table.add_row("Exchanges", str(summary.total_exchanges))
                table.add_row("Topics", ", ".join(summary.topics_discussed[:5]))
                layer2.current_session_exchanges = []
                layer2.session_start_time = datetime.now()
                return table
            return self._panel("Failed to generate summary", style="red")
        except Exception as exc:
            return self._panel(f"Error: {exc}", style="red")

    def handle_layer2_list_summaries(self) -> Any:
        if not hasattr(self._memory, "layer2_memory"):
            return self._panel("Layer 2 memory not available", style="red")
        layer2 = self._memory.layer2_memory
        if not layer2.enabled or not layer2.summaries:
            return self._panel("No conversation summaries loaded", title="Empty", style="yellow")

        from rich.table import Table
        from rich.box import ROUNDED

        table = Table(title=f"Layer 2 Summary Buffer ({len(layer2.summaries)} loaded)", box=ROUNDED)
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Exchanges", style="green", width=10)
        table.add_column("Topics", style="bright_magenta", width=30)

        for s in sorted(layer2.summaries, key=lambda x: x.timestamp_start, reverse=True):
            topics = ", ".join(s.topics_discussed[:3]) if s.topics_discussed else "None"
            table.add_row(s.timestamp_start.strftime("%b %d"), str(s.total_exchanges), topics[:30])
        return table

    def handle_layer2_search_memory(self, query: str) -> Any:
        if not hasattr(self._memory, "layer2_memory"):
            return self._panel("Layer 2 memory not available", style="red")
        layer2 = self._memory.layer2_memory
        if not layer2.enabled:
            return self._panel("Layer 2 disabled", style="yellow")
        if not query.strip():
            return self._panel("Usage: /search-memory <query>", title="Search Memory", style="yellow")

        results = layer2.search_summaries(query.strip())
        if not results:
            return self._panel(f"No results for: {query}", title="No Results", style="yellow")

        from rich.table import Table
        from rich.box import ROUNDED

        table = Table(title=f"Memory Search: '{query}' ({len(results)} results)", box=ROUNDED)
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Score", style="green", width=8)
        table.add_column("Matches", style="bright_white", width=60)

        for r in results:
            s = r["summary"]
            matches = "\n".join(f"- {m[:55]}..." if len(m) > 55 else f"- {m}" for m in r["matches"][:3])
            table.add_row(s.timestamp_start.strftime("%b %d, %Y"), str(r["score"]), matches)
        return table

    def handle_layer2_status(self) -> Any:
        if not hasattr(self._memory, "layer2_memory"):
            return self._panel("Layer 2 memory not available", style="red")
        layer2 = self._memory.layer2_memory
        status = layer2.get_status()

        from rich.table import Table
        from rich.box import ROUNDED

        table = Table(title="Layer 2 Summary Buffer Memory Status", box=ROUNDED)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="bright_white")
        table.add_row("System Status", "ENABLED" if status["enabled"] else "DISABLED")
        table.add_row("Summaries Loaded", str(status["summaries_loaded"]))
        table.add_row("Current Session", f"{status['current_exchanges']} exchanges")
        table.add_row("Storage Path", str(status["storage_path"]))
        table.add_row("Detail Level", status["detail_level"])
        table.add_row("Auto Save", "YES" if status["auto_save"] else "NO")
        return table

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_memory_recommendations(self, context_size: Dict[str, int]) -> str:
        pct = context_size["percent"]
        if pct < 50:
            return "Context usage is healthy -- no action needed"
        elif pct < 70:
            return "Context usage is moderate -- monitor for long conversations"
        elif pct < 85:
            return "Approaching warning threshold -- compression may trigger soon"
        elif pct < 95:
            return "Near critical -- emergency compression will trigger automatically"
        return "CRITICAL -- checkpoint creation imminent to prevent overflow"
