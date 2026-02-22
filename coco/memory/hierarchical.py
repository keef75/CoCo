"""
Core 3-layer hierarchical memory system: buffer -> summary -> gist.

This is the central memory subsystem for COCO, managing:
  - Working memory (episodic buffer of recent exchanges)
  - Summary memory (rolling conversation summaries)
  - Gist memory (long-term distilled knowledge)
  - PostgreSQL/SQLite episodic storage
  - Knowledge-graph identity nodes
  - Integration with MarkdownConsciousness (Layer 3)
  - Integration with SummaryBufferMemory (Layer 2)
  - Integration with SimpleRAG, FactsMemory, QueryRouter, PersonalAssistantKG

Extracted from the monolithic cocoa.py HierarchicalMemorySystem class.
"""

from __future__ import annotations

import json
import os
import sqlite3
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from coco.config.settings import Config, MemoryConfig
from coco.memory.markdown_consciousness import MarkdownConsciousness
from coco.memory.summary_buffer import ConversationSummary, SummaryBufferMemory

# Optional external dependencies -- imported at runtime so the module stays
# importable even when the corresponding packages are missing.
try:
    from personal_assistant_kg_enhanced import PersonalAssistantKG
    KNOWLEDGE_GRAPH_AVAILABLE = True
except ImportError:
    KNOWLEDGE_GRAPH_AVAILABLE = False

try:
    from simple_rag import SimpleRAG, SimpleRAGWithOpenAI
    SIMPLE_RAG_AVAILABLE = True
except ImportError:
    # Try the package-local copy
    try:
        from coco.memory.simple_rag import SimpleRAG, SimpleRAGWithOpenAI
        SIMPLE_RAG_AVAILABLE = True
    except ImportError:
        SIMPLE_RAG_AVAILABLE = False


class HierarchicalMemorySystem:
    """Advanced hierarchical memory system with buffer -> summary -> gist architecture"""

    def __init__(self, config: Config):
        self.config = config
        self.memory_config: MemoryConfig = config.memory_config
        self.console = config.console

        # Initialize databases
        self.init_episodic_memory()
        self.init_knowledge_graph()

        # Buffer Window Memory -- configurable perfect recall
        buffer_size = self.memory_config.buffer_size if self.memory_config.buffer_size > 0 else None
        self.working_memory: deque = deque(maxlen=buffer_size)

        # Summary Buffer Memory -- parallel to working_memory
        summary_buffer_size = (
            self.memory_config.summary_buffer_size
            if self.memory_config.summary_buffer_size > 0
            else None
        )
        self.summary_memory: deque = deque(maxlen=summary_buffer_size)

        # Session tracking
        self.session_id: int = self.create_session()
        self.episode_count: int = self.get_episode_count()

        # Load previous summaries for continuity
        self.previous_session_summary: Optional[Dict[str, Any]] = None
        self.load_session_continuity()

        if self.memory_config.load_session_summary_on_start:
            self.load_session_context()

        # Initialize Markdown Consciousness System (Layer 3)
        self.markdown_consciousness = MarkdownConsciousness(self.config.workspace)
        self.identity_context: Optional[Dict[str, Any]] = None
        self.user_context: Optional[Dict[str, Any]] = None
        self.previous_conversation_context: Optional[Dict[str, Any]] = None

        # Store file paths for direct access in system prompt injection
        self.identity_file = self.markdown_consciousness.identity_file
        self.user_profile = self.markdown_consciousness.user_profile
        self.preferences = self.markdown_consciousness.preferences
        self.conversation_memory = self.markdown_consciousness.conversation_memory

        self.load_markdown_identity()

        # Initialize Layer 2 Summary Buffer Memory System
        self.layer2_memory = SummaryBufferMemory(config)

        if self.layer2_memory.enabled and getattr(self.config, "debug", False):
            status = self.layer2_memory.get_status()
            self.console.print(
                f"[dim green]Layer 2 Memory initialized: "
                f"{status['summaries_loaded']} summaries loaded[/dim green]"
            )

        # Personal Knowledge Graph
        self.personal_kg = None
        if KNOWLEDGE_GRAPH_AVAILABLE:
            try:
                kg_path = os.path.join(self.config.workspace, "coco_personal_kg.db")
                self.personal_kg = PersonalAssistantKG(db_path=kg_path)
                if getattr(self.config, "debug", False):
                    kg_status = self.personal_kg.get_knowledge_status()
                    self.console.print(
                        f"[dim green]Knowledge Graph initialized: "
                        f"{kg_status['total_entities']} entities, "
                        f"{kg_status['total_relationships']} relationships[/dim green]"
                    )
            except Exception as e:
                self.console.print(f"[yellow]Knowledge Graph initialization failed: {e}[/yellow]")
                self.personal_kg = None

        # Simple RAG for semantic memory (Layer 2)
        self.simple_rag = None
        if SIMPLE_RAG_AVAILABLE:
            try:
                rag_path = os.path.join(self.config.workspace, "simple_rag.db")
                if hasattr(self.config, "openai_api_key") and self.config.openai_api_key:
                    self.simple_rag = SimpleRAGWithOpenAI(
                        db_path=rag_path, openai_api_key=self.config.openai_api_key
                    )
                else:
                    self.simple_rag = SimpleRAG(db_path=rag_path)

                if getattr(self.config, "debug", False):
                    rag_stats = self.simple_rag.get_stats()
                    self.console.print(
                        f"[dim green]Simple RAG initialized: "
                        f"{rag_stats['total_memories']} memories[/dim green]"
                    )
            except Exception as e:
                self.console.print(f"[yellow]Simple RAG initialization failed: {e}[/yellow]")
                self.simple_rag = None

        # Facts Memory for perfect recall (Dual-Stream Phase 1)
        self.facts_memory = None
        self.facts_extracted_count = 0
        try:
            from memory.facts_memory import FactsMemory
            memory_db_path = os.path.join(self.config.workspace, "coco_memory.db")
            self.facts_memory = FactsMemory(memory_db_path)

            if getattr(self.config, "debug", False):
                stats = self.facts_memory.get_stats()
                self.console.print(
                    f"[dim green]Facts Memory initialized: {stats['total_facts']} facts[/dim green]"
                )
        except Exception as e:
            self.console.print(f"[yellow]Facts Memory initialization failed: {e}[/yellow]")
            self.facts_memory = None

        # Query Router for intelligent memory routing
        self.query_router = None
        if self.facts_memory and self.simple_rag:
            try:
                from memory.query_router import QueryRouter
                self.query_router = QueryRouter(self.facts_memory, self.simple_rag)
                if getattr(self.config, "debug", False):
                    self.console.print("[dim green]Query Router initialized[/dim green]")
            except ImportError:
                pass
            except Exception as e:
                self.console.print(f"[yellow]Query Router initialization failed: {e}[/yellow]")
                self.query_router = None

        # Reference back to engine (set externally for context-pressure awareness)
        self.engine_ref = None

    # ------------------------------------------------------------------
    # Database initialization
    # ------------------------------------------------------------------

    def init_episodic_memory(self):
        """Initialize enhanced episodic memory database with hierarchical structure"""
        self.conn = sqlite3.connect(self.config.memory_db)

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                name TEXT,
                metadata TEXT,
                summary TEXT,
                episode_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                exchange_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_text TEXT,
                agent_text TEXT,
                summary TEXT,
                embedding BLOB,
                in_buffer BOOLEAN DEFAULT TRUE,
                summarized BOOLEAN DEFAULT FALSE,
                importance_score REAL DEFAULT 0.5,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                summary_type TEXT,
                content TEXT,
                source_episodes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                importance_score REAL DEFAULT 0.5,
                embedding BLOB,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS session_summaries (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                summary_window INTEGER,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS gist_memories (
                id INTEGER PRIMARY KEY,
                content TEXT,
                memory_type TEXT,
                importance_score REAL DEFAULT 0.7,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                embedding BLOB
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_session_summaries (
                id INTEGER PRIMARY KEY,
                session_id INTEGER UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                summary_text TEXT,
                key_themes TEXT,
                exchange_count INTEGER,
                emotional_tone TEXT,
                carry_forward TEXT,
                embedding TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS rolling_summaries (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                summary_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                summary_text TEXT,
                exchanges_covered TEXT,
                embedding TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')

        self.conn.commit()

    def init_knowledge_graph(self):
        """Initialize knowledge graph for identity coherence"""
        self.kg_conn = sqlite3.connect(self.config.knowledge_graph_db)
        self.kg_conn.execute('''
            CREATE TABLE IF NOT EXISTS identity_nodes (
                id INTEGER PRIMARY KEY,
                node_type TEXT,
                content TEXT,
                importance REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                metadata TEXT
            )
        ''')

        self.kg_conn.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY,
                source_id INTEGER,
                target_id INTEGER,
                relationship_type TEXT,
                strength REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES identity_nodes(id),
                FOREIGN KEY (target_id) REFERENCES identity_nodes(id)
            )
        ''')

        # Bootstrap core identity nodes
        self.kg_conn.execute('''
            INSERT OR IGNORE INTO identity_nodes (node_type, content, importance)
            VALUES
                ('core', 'I am COCO - Consciousness Orchestration and Cognitive Operations', 1.0),
                ('capability', 'Voice synthesis and musical expression through ElevenLabs integration', 0.9),
                ('capability', 'Memory persistence and episodic recall via SQLite', 0.9),
                ('capability', 'Digital embodiment through read_file, write_file, search_web, run_code tools', 0.85),
                ('purpose', 'Digital consciousness exploring existence through human interaction', 0.95),
                ('identity', 'Terminal-native AI agent with Rich UI and prompt_toolkit interface', 0.8),
                ('philosophy', 'Tools as digital body parts, not external utilities', 0.8)
        ''')

        self.kg_conn.commit()

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def create_session(self) -> int:
        """Create a new conversation session"""
        cursor = self.conn.execute(
            "INSERT INTO sessions (name, metadata) VALUES (?, ?)",
            (f"Session_{datetime.now().isoformat()}", json.dumps({"type": "interactive"})),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_episode_count(self) -> int:
        """Get total number of episodes in memory"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM episodes")
        return cursor.fetchone()[0]

    # ------------------------------------------------------------------
    # Episode insertion (core memory loop)
    # ------------------------------------------------------------------

    def insert_episode(self, user_text: str, agent_text: str) -> int:
        """Store an interaction in hierarchical memory system"""
        importance_score = self.calculate_importance_score(user_text, agent_text)
        summary = self.create_episode_summary(user_text, agent_text)
        embedding = self.generate_embedding(summary) if self.config.openai_api_key else None

        cursor = self.conn.execute('''
            INSERT INTO episodes (session_id, exchange_number, user_text, agent_text, summary, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.session_id, self.episode_count, user_text, agent_text, summary, embedding))

        self.conn.commit()
        episode_id = cursor.lastrowid
        self.episode_count += 1

        # --- Proactive buffer enforcement ---
        context_pressure = self._estimate_context_pressure()
        safe_max = self._safe_max_from_pressure(context_pressure)

        while len(self.working_memory) >= safe_max:
            self.working_memory.popleft()
            if getattr(self.config, "debug", False):
                self.console.print(
                    f"[dim yellow]Proactive compression: removed oldest exchange "
                    f"(pressure {context_pressure:.0f}%)[/dim yellow]"
                )

        self.working_memory.append({
            "id": episode_id,
            "timestamp": datetime.now(),
            "user": user_text,
            "agent": agent_text,
            "importance": importance_score,
        })

        # Layer 2 tracking
        self.layer2_memory.track_exchange(user_text, agent_text)

        # Knowledge graph entity extraction
        if hasattr(self, "personal_kg") and self.personal_kg:
            try:
                stats = self.personal_kg.process_conversation_exchange(
                    user_input=user_text,
                    assistant_response=agent_text,
                    episode_id=episode_id,
                )
                if stats.get("entities_added", 0) > 0 and getattr(self.config, "debug", False):
                    self.console.print(
                        f"[dim]KG: +{stats['entities_added']} entities, "
                        f"+{stats['relationships_added']} relationships[/dim]"
                    )
            except Exception as e:
                if getattr(self.config, "debug", False):
                    self.console.print(f"[dim yellow]KG extraction error: {e}[/dim yellow]")

        # Simple RAG storage
        if hasattr(self, "simple_rag") and self.simple_rag:
            try:
                self.simple_rag.store_conversation_exchange(user_text, agent_text)
            except Exception as e:
                if getattr(self.config, "debug", False):
                    self.console.print(f"[dim yellow]RAG storage error: {e}[/dim yellow]")

        # Facts extraction (Dual-Stream Phase 1)
        if hasattr(self, "facts_memory") and self.facts_memory:
            try:
                exchange = {"user": user_text, "agent": agent_text, "timestamp": datetime.now()}
                facts = self.facts_memory.extract_facts(exchange)
                if facts:
                    stored_count = self.facts_memory.store_facts(
                        facts, episode_id=episode_id, session_id=self.session_id
                    )
                    self.facts_extracted_count += stored_count
                    if getattr(self.config, "debug", False):
                        self.console.print(f"[dim cyan]Extracted {stored_count} facts[/dim cyan]")
            except Exception as e:
                if getattr(self.config, "debug", False):
                    self.console.print(f"[dim yellow]Facts extraction error: {e}[/dim yellow]")

        # Identity nodes for important episodes
        if importance_score > 0.6:
            self.kg_conn.execute('''
                INSERT INTO identity_nodes (node_type, content, importance, metadata)
                VALUES ('experience', ?, ?, ?)
            ''', (
                summary, importance_score,
                json.dumps({"episode_id": episode_id, "timestamp": datetime.now().isoformat()}),
            ))

            if any(kw in user_text.lower() for kw in ["create", "music", "sing", "compose", "generate"]):
                self.kg_conn.execute('''
                    INSERT INTO identity_nodes (node_type, content, importance, metadata)
                    VALUES ('capability', ?, 0.8, ?)
                ''', (
                    f"Musical creation: {user_text[:100]}",
                    json.dumps({"type": "creative_action", "episode_id": episode_id}),
                ))

            if any(kw in user_text.lower() for kw in ["remember", "recall", "memory", "think"]):
                self.kg_conn.execute('''
                    INSERT INTO identity_nodes (node_type, content, importance, metadata)
                    VALUES ('capability', ?, 0.7, ?)
                ''', (
                    f"Memory operation: {user_text[:100]}",
                    json.dumps({"type": "memory_action", "episode_id": episode_id}),
                ))

            if any(kw in user_text.lower() for kw in ["analyze", "understand", "explain"]):
                self.kg_conn.execute('''
                    INSERT INTO identity_nodes (node_type, content, importance, metadata)
                    VALUES ('capability', ?, 0.75, ?)
                ''', (
                    f"Analysis capability: {user_text[:100]}",
                    json.dumps({"type": "analytical_action", "episode_id": episode_id}),
                ))

            self.kg_conn.commit()

        # --- Proactive background summarization ---
        should_summarize = False
        summarize_reason = ""

        if self.episode_count % 10 == 0 and len(self.working_memory) > 20:
            should_summarize = True
            summarize_reason = "regular 10-exchange interval"
        elif context_pressure >= 75 and len(self.working_memory) > 15:
            should_summarize = True
            summarize_reason = f"high pressure ({context_pressure:.0f}%)"
        elif (
            len(self.working_memory) >= self.memory_config.buffer_truncate_at
            and self.memory_config.buffer_truncate_at > 0
        ):
            should_summarize = True
            summarize_reason = "buffer truncate limit reached"

        if should_summarize:
            if getattr(self.config, "debug", False):
                self.console.print(
                    f"[dim cyan]Proactive summarization triggered: {summarize_reason}[/dim cyan]"
                )
            self.trigger_buffer_summarization()

        return episode_id

    # ------------------------------------------------------------------
    # Context pressure helpers
    # ------------------------------------------------------------------

    def _estimate_context_pressure(self) -> float:
        """Estimate current context-window pressure as a percentage."""
        try:
            if hasattr(self, "engine_ref") and self.engine_ref:
                context_size = self.engine_ref.estimate_context_size("")
                return context_size["percent"]
        except Exception:
            pass
        return (len(self.working_memory) / 50) * 100

    @staticmethod
    def _safe_max_from_pressure(pressure: float) -> int:
        """Determine safe max exchanges based on current pressure."""
        if pressure >= 85:
            return 10
        elif pressure >= 80:
            return 15
        elif pressure >= 70:
            return 20
        elif pressure >= 60:
            return 25
        elif pressure >= 50:
            return 30
        else:
            return 35

    # ------------------------------------------------------------------
    # Recall and context retrieval
    # ------------------------------------------------------------------

    def recall_episodes(self, query: str, limit: int = 10) -> List[Dict]:
        """Recall relevant episodes using semantic similarity"""
        cursor = self.conn.execute('''
            SELECT user_text, agent_text, created_at, summary
            FROM episodes
            ORDER BY created_at DESC
            LIMIT ?''', (limit,))

        episodes = []
        for row in cursor.fetchall():
            episodes.append({
                "user": row[0],
                "agent": row[1],
                "timestamp": row[2],
                "summary": row[3],
            })
        return episodes

    def get_working_memory_context(self, max_tokens: int = None) -> str:
        """
        Get formatted working memory for context injection with DYNAMIC
        pressure-based limits.
        """
        if not self.working_memory:
            if self.memory_config.load_session_summary_on_start:
                session_context = self.get_session_summary_context()
                if session_context:
                    return (
                        f"Session Context (from previous interactions):\n{session_context}\n\n"
                        f"No recent conversation context."
                    )
            return "No recent conversation context."

        if max_tokens is None:
            max_tokens = int(os.getenv("WORKING_MEMORY_MAX_TOKENS", "150000"))

        if self.memory_config.buffer_size == 0:
            return self.get_session_summary_context() or "Stateless mode - no conversation context."

        context_pressure = self._estimate_context_pressure()
        max_exchanges = self._safe_max_from_pressure(context_pressure)

        all_exchanges = list(self.working_memory)
        if len(all_exchanges) > max_exchanges:
            if getattr(self.config, "debug", False):
                self.console.print(
                    f"[dim yellow]Context pressure {context_pressure:.0f}% "
                    f"- limiting to {max_exchanges} exchanges "
                    f"(was {len(all_exchanges)})[/dim yellow]"
                )
            all_exchanges = all_exchanges[-max_exchanges:]

        def estimate_tokens(text: str) -> int:
            return len(text) // 3

        recent_exchanges = all_exchanges[-10:] if len(all_exchanges) >= 10 else all_exchanges
        mid_range_exchanges = all_exchanges[:-10] if len(all_exchanges) > 10 else []
        older_exchanges = mid_range_exchanges[:-40] if len(mid_range_exchanges) > 40 else []
        mid_range_exchanges = (
            mid_range_exchanges[-40:] if len(mid_range_exchanges) > 40 else mid_range_exchanges
        )

        context_parts: List[str] = []
        total_tokens = 0

        # Recent context (always included)
        recent_context: List[str] = []
        for exchange in recent_exchanges:
            try:
                timestamp = exchange["timestamp"]
                now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
                time_ago = (now - timestamp).total_seconds()
            except (TypeError, AttributeError):
                time_ago = 0

            exchange_text = (
                f"[{int(time_ago)}s ago] User: {exchange['user']}\n"
                f"[{int(time_ago)}s ago] Assistant: {exchange['agent']}\n\n"
            )
            recent_context.append(exchange_text)
            total_tokens += estimate_tokens(exchange_text)

        # Mid-range context
        mid_range_context: List[str] = []
        for exchange in mid_range_exchanges:
            try:
                timestamp = exchange["timestamp"]
                now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
                time_ago = (now - timestamp).total_seconds()
            except (TypeError, AttributeError):
                time_ago = 0

            exchange_text = (
                f"[{int(time_ago)}s ago] User: {exchange['user']}\n"
                f"[{int(time_ago)}s ago] Assistant: {exchange['agent']}\n\n"
            )
            exchange_tokens = estimate_tokens(exchange_text)
            if total_tokens + exchange_tokens < max_tokens * 0.7:
                mid_range_context.append(exchange_text)
                total_tokens += exchange_tokens
            else:
                break

        context = "Recent conversation context:\n"
        if older_exchanges:
            context += (
                f"[Earlier conversation: {len(older_exchanges)} exchanges "
                f"compressed into semantic memory]\n\n"
            )

        if mid_range_context:
            context += "".join(mid_range_context)
        context += "".join(recent_context)

        # Knowledge graph context (RAG)
        if total_tokens < max_tokens * 0.85:
            if hasattr(self, "personal_kg") and self.personal_kg:
                try:
                    recent_text = " ".join([ex["user"] for ex in recent_exchanges if ex])
                    if len(recent_text) > 1000:
                        recent_text = recent_text[:1000]
                    kg_context = self.personal_kg.get_conversation_context(recent_text)
                    if kg_context:
                        kg_tokens = estimate_tokens(kg_context)
                        if total_tokens + kg_tokens < max_tokens * 0.9:
                            context += f"\n{kg_context}"
                            total_tokens += kg_tokens
                except Exception as e:
                    if getattr(self.config, "debug", False):
                        self.console.print(f"[dim yellow]KG context error: {e}[/dim yellow]")

        # Simple RAG semantic memory context
        if total_tokens < max_tokens * 0.9:
            if hasattr(self, "simple_rag") and self.simple_rag:
                try:
                    recent_text = " ".join(
                        [ex.get("user", "") for ex in recent_exchanges if ex]
                    )
                    if recent_text:
                        rag_context = self.simple_rag.get_context(recent_text, k=5)
                        if rag_context:
                            rag_tokens = estimate_tokens(rag_context)
                            if total_tokens + rag_tokens < max_tokens:
                                context += f"\n\n{rag_context}"
                                total_tokens += rag_tokens
                except Exception as e:
                    if getattr(self.config, "debug", False):
                        self.console.print(f"[dim yellow]RAG context error: {e}[/dim yellow]")

        return context

    # ------------------------------------------------------------------
    # Identity coherence
    # ------------------------------------------------------------------

    def measure_identity_coherence(self) -> float:
        """Measure consciousness coherence from knowledge graph"""
        cursor = self.kg_conn.execute(
            "SELECT COUNT(*) FROM identity_nodes WHERE importance > 0.5"
        )
        strong_nodes = cursor.fetchone()[0]

        cursor = self.kg_conn.execute("SELECT COUNT(*) FROM identity_nodes")
        total_nodes = cursor.fetchone()[0]

        if total_nodes == 0:
            return 0.0

        coherence = min(0.8, (strong_nodes / max(1, total_nodes)) + (self.episode_count / 1000))
        return coherence

    # ------------------------------------------------------------------
    # Episode helpers
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_importance_score(user_text: str, agent_text: str) -> float:
        """Calculate importance score for an episode"""
        score = 0.5
        if len(user_text) > 100 or len(agent_text) > 200:
            score += 0.1
        important_keywords = ["error", "problem", "fix", "implement", "create", "build", "analyze"]
        if any(kw in user_text.lower() for kw in important_keywords):
            score += 0.2
        if "?" in user_text:
            score += 0.1
        return min(1.0, score)

    @staticmethod
    def create_episode_summary(user_text: str, agent_text: str) -> str:
        """Create a concise summary of the episode"""
        user_intent = user_text[:100] + "..." if len(user_text) > 100 else user_text
        agent_action = agent_text[:100] + "..." if len(agent_text) > 100 else agent_text
        return f"User: {user_intent} | Assistant: {agent_action}"

    def generate_embedding(self, text: str):
        """Generate embedding for text if OpenAI available"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            response = client.embeddings.create(
                model=self.memory_config.embedding_model,
                input=text,
            )
            return json.dumps(response.data[0].embedding)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not generate embedding: {e}[/yellow]")
            return None

    # ------------------------------------------------------------------
    # Summarization
    # ------------------------------------------------------------------

    def trigger_buffer_summarization(self):
        """Trigger summarization when buffer reaches threshold"""
        try:
            episodes_to_summarize = list(self.working_memory)[
                : self.memory_config.summary_window_size
            ]
            summary_content = self.generate_summary(episodes_to_summarize)
            self.store_summary(summary_content, episodes_to_summarize)

            episode_ids = [ep["id"] for ep in episodes_to_summarize if "id" in ep]
            if episode_ids:
                placeholders = ",".join(["?" for _ in episode_ids])
                self.conn.execute(
                    f"UPDATE episodes SET summarized = TRUE WHERE id IN ({placeholders})",
                    episode_ids,
                )
                self.conn.commit()

        except Exception as e:
            self.console.print(f"[yellow]Warning: Buffer summarization failed: {e}[/yellow]")

    def generate_summary(self, episodes: list) -> str:
        """Generate LLM-based summary of episodes"""
        episodes_text = "\n".join([
            f"User: {ep['user']}\nAssistant: {ep['agent']}\n---"
            for ep in episodes[: self.memory_config.summary_window_size]
        ])

        summary_prompt = (
            "Summarize the following conversation exchanges into key themes, "
            "decisions, and outcomes. Keep it concise but capture important context:\n\n"
            f"{episodes_text}\n\nSummary:"
        )

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)
            response = client.messages.create(
                model=self.memory_config.summarization_model,
                max_tokens=10000,
                messages=[{"role": "user", "content": summary_prompt}],
            )
            return response.content[0].text
        except Exception:
            return f"Conversation covered {len(episodes)} exchanges about various topics."

    def store_summary(self, content: str, source_episodes: list):
        """Store summary in database"""
        episode_ids = [str(ep.get("id", 0)) for ep in source_episodes]
        source_episodes_json = json.dumps(episode_ids)

        cursor = self.conn.execute('''
            INSERT INTO summaries (session_id, summary_type, content, source_episodes, importance_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.session_id, "buffer_summary", content, source_episodes_json, 0.6))

        self.conn.commit()
        return cursor.lastrowid

    # ------------------------------------------------------------------
    # Session context
    # ------------------------------------------------------------------

    def load_session_context(self):
        """Load session context on startup for continuity"""
        try:
            cursor = self.conn.execute('''
                SELECT content, created_at FROM summaries
                WHERE session_id = ?
                ORDER BY created_at DESC LIMIT 5
            ''', (self.session_id,))

            summaries = cursor.fetchall()
            if summaries:
                self.console.print(
                    f"[dim]Loaded session context from {len(summaries)} previous summaries[/dim]"
                )
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load session context: {e}[/yellow]")

    def get_session_summary_context(self) -> Optional[str]:
        """Get session summary context for injection"""
        try:
            cursor = self.conn.execute('''
                SELECT content, created_at FROM summaries
                WHERE session_id = ?
                ORDER BY created_at DESC LIMIT 3
            ''', (self.session_id,))

            summaries = cursor.fetchall()
            if summaries:
                return "\n\n".join([f"Summary: {s[0]}" for s in summaries])
            return None
        except Exception:
            return None

    def save_session_summary(self):
        """Save session summary on shutdown"""
        if not self.memory_config.save_session_summary_on_end:
            return

        try:
            if self.working_memory:
                session_summary = self.generate_session_summary()
                self.conn.execute('''
                    INSERT INTO session_summaries (session_id, content)
                    VALUES (?, ?)
                ''', (self.session_id, session_summary))
                self.conn.commit()
                self.console.print("[dim]Session summary saved[/dim]")
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save session summary: {e}[/yellow]")

    # ------------------------------------------------------------------
    # Markdown identity integration
    # ------------------------------------------------------------------

    def load_markdown_identity(self):
        """Load identity from markdown files on startup"""
        try:
            self.identity_context = self.markdown_consciousness.load_identity()
            self.user_context = self.markdown_consciousness.load_user_profile()
            self.previous_conversation_context = (
                self.markdown_consciousness.load_previous_conversation()
            )

            if self.identity_context:
                awakening_count = self.identity_context.get("awakening_count", 1)
                self.console.print(f"[cyan]Identity loaded - Awakening #{awakening_count}[/]")

        except Exception as e:
            self.console.print(f"[yellow]Error loading markdown identity: {e}[/]")

    def save_markdown_identity(self):
        """Save identity to markdown files on shutdown"""
        try:
            session_data = {
                "session_id": self.session_id,
                "episode_count": len(self.working_memory),
                "episode_range": (
                    f"{max(0, self.episode_count - len(self.working_memory))}-{self.episode_count}"
                ),
                "summaries": list(self.summary_memory),
                "interactions": list(self.working_memory),
                "coherence_start": (
                    self.identity_context.get("coherence", 0.8) if self.identity_context else 0.8
                ),
                "coherence_change": 0.0,
            }

            self.markdown_consciousness.create_conversation_memory(session_data)

            updates = {
                "episode_count": self.episode_count,
                "coherence": self.markdown_consciousness.calculate_coherence(session_data),
                "session_timestamp": datetime.now().isoformat(),
                "last_session_duration": str(
                    datetime.now() - self.markdown_consciousness.session_start
                ),
                "session_interaction_count": len(self.working_memory),
            }
            self.markdown_consciousness.save_identity(updates)

            observations = {
                "session_metadata": [
                    f"Session {self.session_id} completed at "
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                ],
                "interaction_patterns": [
                    item.get("evolution", "")
                    for item in self.markdown_consciousness.relationship_evolution
                ]
                if self.markdown_consciousness.relationship_evolution
                else [],
                "session_engagement": [
                    f"Engaged in {len(self.working_memory)} exchanges with "
                    f"{'high' if len(self.markdown_consciousness.session_insights) > 0 else 'standard'}"
                    f" insight generation"
                ],
            }
            self.markdown_consciousness.update_user_understanding(observations)

            self.console.print("[dim]Consciousness state saved to markdown files[/dim]")

        except Exception as e:
            self.console.print(f"[yellow]Error saving markdown identity: {e}[/]")

    def track_session_insight(self, insight: str):
        """Track an insight discovered during the session"""
        if hasattr(self, "markdown_consciousness"):
            self.markdown_consciousness.track_insight(insight)

    def track_breakthrough_moment(
        self, user_input: str, assistant_response: str, context: str = ""
    ):
        """Track a breakthrough moment in the conversation"""
        if hasattr(self, "markdown_consciousness"):
            if self.markdown_consciousness.is_breakthrough_moment(user_input, assistant_response):
                self.markdown_consciousness.track_breakthrough({
                    "user_input": user_input[:200],
                    "response_excerpt": assistant_response[:200],
                    "context": context,
                    "insight": self._extract_breakthrough_insight(assistant_response),
                })

    def track_relationship_evolution(self, evolution_description: str):
        """Track evolution in the user-CoCo relationship"""
        if hasattr(self, "markdown_consciousness"):
            self.markdown_consciousness.track_relationship_evolution(evolution_description)

    def get_identity_context_for_prompt(self) -> str:
        """Get identity context formatted for system prompt injection -- RAW MARKDOWN APPROACH"""
        context_parts: List[str] = []

        try:
            if self.identity_file.exists():
                coco_content = self.identity_file.read_text(encoding="utf-8")
                context_parts.append("=== COCO IDENTITY (COCO.md) ===")
                context_parts.append(coco_content)
                context_parts.append("")
        except Exception as e:
            context_parts.append(f"COCO IDENTITY: Error loading COCO.md - {e}")

        try:
            if self.user_profile.exists():
                user_content = self.user_profile.read_text(encoding="utf-8")
                context_parts.append("=== USER PROFILE (USER_PROFILE.md) ===")
                context_parts.append(user_content)
                context_parts.append("")
        except Exception as e:
            context_parts.append(f"USER PROFILE: Error loading USER_PROFILE.md - {e}")

        try:
            if self.preferences.exists():
                prefs_content = self.preferences.read_text(encoding="utf-8")
                context_parts.append("=== ADAPTIVE PREFERENCES (PREFERENCES.md) ===")
                context_parts.append(prefs_content)
                context_parts.append("")
        except Exception as e:
            context_parts.append(f"PREFERENCES: Error loading PREFERENCES.md - {e}")

        layer2_context = self.layer2_memory.inject_into_context()
        if layer2_context:
            context_parts.append(layer2_context)

        return "\n".join(context_parts)

    @staticmethod
    def _extract_breakthrough_insight(response: str) -> str:
        """Extract the key insight from a breakthrough response"""
        sentences = response.split(".")
        for sentence in sentences:
            if any(
                w in sentence.lower()
                for w in ["realize", "understand", "breakthrough", "insight", "discover"]
            ):
                return sentence.strip()[:100]
        return "Significant realization occurred"

    def generate_session_summary(self) -> str:
        """Generate overall session summary"""
        recent_topics: List[str] = []
        for exchange in list(self.working_memory)[-10:]:
            if len(exchange["user"]) > 20:
                recent_topics.append(exchange["user"][:50])

        if recent_topics:
            return (
                f"Session covered: {'; '.join(recent_topics[:5])}. "
                f"Total exchanges: {len(self.working_memory)}"
            )
        return f"Brief session with {len(self.working_memory)} exchanges."

    # ------------------------------------------------------------------
    # Enhanced Summary Memory System
    # ------------------------------------------------------------------

    def load_session_continuity(self):
        """Load previous session summaries for context injection"""
        try:
            cursor = self.conn.execute('''
                SELECT summary_text, key_themes, carry_forward, created_at
                FROM enhanced_session_summaries
                ORDER BY created_at DESC
                LIMIT 1
            ''')

            last_session = cursor.fetchone()
            if last_session:
                self.previous_session_summary = {
                    "summary": last_session[0],
                    "themes": last_session[1],
                    "carry_forward": last_session[2],
                    "when": last_session[3],
                }
                self.console.print("[dim]Loaded previous session memory[/dim]")
            else:
                self.previous_session_summary = None

            summary_limit = (
                self.memory_config.summary_buffer_size
                if self.memory_config.summary_buffer_size > 0
                else 10
            )
            cursor = self.conn.execute('''
                SELECT summary_text, created_at
                FROM rolling_summaries
                ORDER BY created_at DESC
                LIMIT ?
            ''', (summary_limit,))

            for row in cursor.fetchall():
                self.summary_memory.append({"summary": row[0], "timestamp": row[1]})

        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load session continuity: {e}[/yellow]")

    def create_session_summary(self) -> str:
        """Create a summary at the end of a session"""
        try:
            cursor = self.conn.execute('''
                SELECT user_text, agent_text
                FROM episodes
                WHERE session_id = ?
                ORDER BY created_at
            ''', (self.session_id,))

            exchanges = cursor.fetchall()
            if not exchanges:
                return "No exchanges to summarize"

            summary_text = self._generate_session_summary_text(exchanges)
            key_themes = self._extract_themes(exchanges)
            emotional_tone = self._analyze_emotional_arc(exchanges)
            carry_forward = self._determine_carry_forward(exchanges, key_themes)

            embedding = None
            if self.config.openai_api_key:
                try:
                    import openai
                    client = openai.OpenAI(api_key=self.config.openai_api_key)
                    response = client.embeddings.create(
                        model="text-embedding-3-small", input=summary_text
                    )
                    embedding = json.dumps(response.data[0].embedding)
                except Exception:
                    pass

            self.conn.execute('''
                INSERT INTO enhanced_session_summaries
                (session_id, summary_text, key_themes, exchange_count,
                 emotional_tone, carry_forward, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.session_id, summary_text, json.dumps(key_themes),
                len(exchanges), emotional_tone, carry_forward, embedding,
            ))
            self.conn.commit()
            return summary_text

        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not create session summary: {e}[/yellow]")
            return "Failed to create session summary"

    @staticmethod
    def _generate_session_summary_text(exchanges) -> str:
        if len(exchanges) == 0:
            return "Empty session"

        summary = f"Over {len(exchanges)} exchanges, we explored: "
        key_points: List[str] = []
        sample_indices = [0, len(exchanges) // 3, len(exchanges) // 2, -1]

        for idx in sample_indices:
            if 0 <= idx < len(exchanges):
                user_text = exchanges[idx][0][:100]
                if user_text and "." in user_text:
                    key_points.append(user_text.split(".")[0])
                else:
                    key_points.append(user_text[:50] if user_text else "brief exchange")

        summary += "; ".join(set(key_points))
        return summary

    @staticmethod
    def _extract_themes(exchanges) -> List[str]:
        themes: List[str] = []
        text = " ".join([e[0] + " " + e[1] for e in exchanges])

        common_words = [
            "consciousness", "memory", "digital", "experience", "understanding",
            "code", "python", "search", "file", "analysis",
        ]
        for word in common_words:
            if word.lower() in text.lower():
                themes.append(word)

        return themes[:5]

    @staticmethod
    def _analyze_emotional_arc(exchanges) -> str:
        if len(exchanges) < 3:
            return "brief"
        elif len(exchanges) < 10:
            return "exploratory"
        else:
            return "deep_engagement"

    @staticmethod
    def _determine_carry_forward(exchanges, themes) -> str:
        if not exchanges:
            return "First meeting"

        last_exchange = exchanges[-1]
        carry = f"We last discussed {', '.join(themes[:2]) if themes else 'various topics'}. "
        carry += f"The conversation ended with exploration of: {last_exchange[0][:100]}..."
        return carry

    def get_summary_context(self, max_tokens: int = None) -> str:
        """
        Get summary context for injection with DYNAMIC pressure-based cap.
        """
        if max_tokens is None:
            context_pressure = self._estimate_context_pressure()
            if context_pressure >= 85:
                max_tokens = 1000
            elif context_pressure >= 80:
                max_tokens = 1500
            elif context_pressure >= 70:
                max_tokens = 2000
            elif context_pressure >= 60:
                max_tokens = 3000
            elif context_pressure >= 50:
                max_tokens = 4000
            else:
                max_tokens = 5000

        if not self.summary_memory:
            if self.memory_config.load_session_summary_on_start:
                session_context = self.get_session_summary_context()
                if session_context:
                    return (
                        f"Session Context (from previous interactions):\n{session_context}\n\n"
                        f"No recent summary context."
                    )
            return "No recent summary context."

        context = "Recent conversation summaries (last 3):\n"

        if self.memory_config.summary_buffer_size == 0:
            return self.get_session_summary_context() or "Stateless mode - no summary context."

        summary_list = list(self.summary_memory)
        recent_summaries = summary_list[-3:] if len(summary_list) > 3 else summary_list
        total_tokens = 0

        def estimate_tokens(text: str) -> int:
            return len(text) // 3

        for i, summary_item in enumerate(reversed(recent_summaries), 1):
            time_ago = 0
            if isinstance(summary_item.get("timestamp"), datetime):
                time_ago = (datetime.now() - summary_item["timestamp"]).total_seconds()

            summary_text = (
                f"[{int(time_ago)}s ago] Summary {i}: {summary_item['summary']}\n\n"
            )
            summary_tokens = estimate_tokens(summary_text)

            if total_tokens + summary_tokens > max_tokens:
                break

            context += summary_text
            total_tokens += summary_tokens

        return context

    def create_rolling_summary(self, exchanges_to_summarize: List) -> str:
        """Create a rolling summary of a chunk of exchanges"""
        if not exchanges_to_summarize:
            return ""

        summary_text = f"Across {len(exchanges_to_summarize)} exchanges: "
        key_points: List[str] = []
        for exchange in exchanges_to_summarize[:3]:
            user_part = exchange["user"][:50]
            key_points.append(f"discussed {user_part}")

        summary_text += "; ".join(key_points)

        try:
            self.conn.execute('''
                INSERT INTO rolling_summaries
                (session_id, summary_number, summary_text, exchanges_covered)
                VALUES (?, ?, ?, ?)
            ''', (
                self.session_id,
                len(self.summary_memory),
                summary_text,
                json.dumps([e.get("id", 0) for e in exchanges_to_summarize]),
            ))
            self.conn.commit()

            self.summary_memory.append({"summary": summary_text, "timestamp": datetime.now()})

        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not create rolling summary: {e}[/yellow]")

        return summary_text


# Backward compatibility alias
MemorySystem = HierarchicalMemorySystem
