#!/usr/bin/env python3
"""
episodic_memory_fix.py - Production-ready episodic memory system with precise recall
Fixes session boundaries, temporal navigation, and conversation ordering
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib
from pathlib import Path

@dataclass
class Episode:
    """Single conversation exchange with full context"""
    session_id: str
    exchange_number: int
    user_text: str
    agent_text: str
    timestamp: datetime
    is_session_start: bool = False
    metadata: Dict = None
    embedding: List[float] = None  # For semantic search

class EnhancedEpisodicMemory:
    """
    Production-ready episodic memory with precise temporal recall
    Solves: session boundaries, exchange ordering, cross-session confusion
    """

    def __init__(self, db_path: str = "./coco_workspace/enhanced_memory.db"):
        self.db_path = db_path
        self.current_session_id = None
        self.current_exchange_number = 0
        self._init_database()

    def _init_database(self):
        """Initialize database with proper schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    total_exchanges INTEGER DEFAULT 0,
                    session_metadata JSON
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    exchange_number INTEGER NOT NULL,
                    user_text TEXT,
                    agent_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_session_start BOOLEAN DEFAULT FALSE,
                    metadata JSON,
                    embedding BLOB,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                    UNIQUE(session_id, exchange_number)
                )
            """)

            # Critical indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_session_order
                ON episodes(session_id, exchange_number)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_timestamp
                ON episodes(timestamp DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_session_start
                ON episodes(is_session_start) WHERE is_session_start = TRUE
            """)

    def start_session(self, session_metadata: Dict = None) -> str:
        """Start a new conversation session"""
        self.current_session_id = self._generate_session_id()
        self.current_exchange_number = 0

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions (session_id, session_metadata)
                VALUES (?, ?)
            """, (self.current_session_id, json.dumps(session_metadata or {})))

        print(f"📍 Session started: {self.current_session_id}")
        return self.current_session_id

    def add_exchange(self, user_text: str, agent_text: str,
                    metadata: Dict = None) -> Episode:
        """Add a conversation exchange with precise ordering"""
        if not self.current_session_id:
            self.start_session()

        self.current_exchange_number += 1

        episode = Episode(
            session_id=self.current_session_id,
            exchange_number=self.current_exchange_number,
            user_text=user_text,
            agent_text=agent_text,
            timestamp=datetime.now(),
            is_session_start=(self.current_exchange_number == 1),
            metadata=metadata
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO episodes
                (session_id, exchange_number, user_text, agent_text,
                 is_session_start, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                episode.session_id,
                episode.exchange_number,
                episode.user_text,
                episode.agent_text,
                episode.is_session_start,
                json.dumps(episode.metadata) if episode.metadata else None
            ))

            # Update session exchange count
            conn.execute("""
                UPDATE sessions
                SET total_exchanges = ?
                WHERE session_id = ?
            """, (self.current_exchange_number, self.current_session_id))

        return episode

    def get_first_exchange_of_session(self, session_id: str = None) -> Optional[Episode]:
        """Get the actual first thing said in a session - FILTERS OUT SCHEDULER POLLUTION"""
        if session_id is None:
            session_id = self.current_session_id

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # CRITICAL FIX: Filter out autonomous tasks to get ACTUAL conversation start
            result = conn.execute("""
                SELECT * FROM episodes
                WHERE session_id = ?
                AND user_text NOT LIKE '%🤖 Autonomous Task:%'
                AND user_text NOT LIKE '%Scheduler Consciousness%'
                AND user_text NOT LIKE '%System awareness update%'
                ORDER BY exchange_number ASC
                LIMIT 1
            """, (session_id,)).fetchone()

            if result:
                return self._row_to_episode(result)
        return None

    def get_current_session_history(self, limit: int = None) -> List[Episode]:
        """Get all exchanges from current session in order"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            query = """
                SELECT * FROM episodes
                WHERE session_id = ?
                ORDER BY exchange_number ASC
            """

            if limit:
                query += f" LIMIT {limit}"

            results = conn.execute(query, (self.current_session_id,)).fetchall()
            return [self._row_to_episode(row) for row in results]

    def get_exchange_by_number(self, exchange_number: int,
                              session_id: str = None) -> Optional[Episode]:
        """Get specific exchange by number in session"""
        if session_id is None:
            session_id = self.current_session_id

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute("""
                SELECT * FROM episodes
                WHERE session_id = ? AND exchange_number = ?
            """, (session_id, exchange_number)).fetchone()

            if result:
                return self._row_to_episode(result)
        return None

    def get_previous_exchange(self) -> Optional[Episode]:
        """Get the immediately previous exchange"""
        if self.current_exchange_number > 1:
            return self.get_exchange_by_number(self.current_exchange_number - 1)
        return None

    def search_current_session(self, query: str) -> List[Episode]:
        """Search only within current session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            results = conn.execute("""
                SELECT * FROM episodes
                WHERE session_id = ?
                AND (user_text LIKE ? OR agent_text LIKE ?)
                ORDER BY exchange_number DESC
            """, (self.current_session_id, f"%{query}%", f"%{query}%")).fetchall()

            return [self._row_to_episode(row) for row in results]

    def get_session_boundaries(self) -> Dict:
        """Get clear session boundary information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Current session info
            current = conn.execute("""
                SELECT * FROM sessions
                WHERE session_id = ?
            """, (self.current_session_id,)).fetchone()

            # Previous session
            previous = conn.execute("""
                SELECT * FROM sessions
                WHERE start_time < (
                    SELECT start_time FROM sessions WHERE session_id = ?
                )
                ORDER BY start_time DESC LIMIT 1
            """, (self.current_session_id,)).fetchone()

            return {
                'current_session': {
                    'id': current['session_id'] if current else None,
                    'start_time': current['start_time'] if current else None,
                    'total_exchanges': current['total_exchanges'] if current else 0
                },
                'previous_session': {
                    'id': previous['session_id'] if previous else None,
                    'start_time': previous['start_time'] if previous else None,
                    'total_exchanges': previous['total_exchanges'] if previous else 0
                } if previous else None
            }

    def clarify_temporal_reference(self, reference: str) -> Dict:
        """
        Clarify ambiguous temporal references
        Returns specific episodes based on common references
        """
        reference_lower = reference.lower()

        if "first thing" in reference_lower or "beginning" in reference_lower:
            episode = self.get_first_exchange_of_session()
            return {
                'interpretation': 'First exchange of current session',
                'episode': episode,
                'clarification': f"The first thing you said was: '{episode.user_text}'" if episode else "No exchanges yet"
            }

        elif "just said" in reference_lower or "previous" in reference_lower:
            episode = self.get_previous_exchange()
            return {
                'interpretation': 'Previous exchange',
                'episode': episode,
                'clarification': f"You just said: '{episode.user_text}'" if episode else "This is the first exchange"
            }

        elif "last time" in reference_lower or "last session" in reference_lower:
            boundaries = self.get_session_boundaries()
            if boundaries['previous_session']:
                # Get last exchange of previous session
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    result = conn.execute("""
                        SELECT * FROM episodes
                        WHERE session_id = ?
                        ORDER BY exchange_number DESC LIMIT 1
                    """, (boundaries['previous_session']['id'],)).fetchone()

                    episode = self._row_to_episode(result) if result else None
                    return {
                        'interpretation': 'Last exchange of previous session',
                        'episode': episode,
                        'clarification': f"Last time we talked, the conversation ended with: '{episode.user_text}'" if episode else "No previous session found"
                    }

        # Content-based search for current session
        search_results = self.search_current_session(reference)
        if search_results:
            episode = search_results[0]  # Get most recent match
            return {
                'interpretation': f'Found "{reference}" in conversation',
                'episode': episode,
                'clarification': f"You mentioned \"{reference}\" when you said: '{episode.user_text}'"
            }

        return {
            'interpretation': 'Unclear reference',
            'episode': None,
            'clarification': "Could you clarify if you mean in this current conversation or from a previous session?"
        }

    def get_statistics(self) -> Dict:
        """Get memory system statistics"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}

            # Total episodes
            stats['total_episodes'] = conn.execute(
                "SELECT COUNT(*) FROM episodes"
            ).fetchone()[0]

            # Total sessions
            stats['total_sessions'] = conn.execute(
                "SELECT COUNT(*) FROM sessions"
            ).fetchone()[0]

            # Current session exchanges
            stats['current_session_exchanges'] = self.current_exchange_number

            # Average exchanges per session
            avg_result = conn.execute("""
                SELECT AVG(total_exchanges) FROM sessions
                WHERE total_exchanges > 0
            """).fetchone()[0]
            stats['avg_exchanges_per_session'] = round(avg_result, 2) if avg_result else 0

            return stats

    def _row_to_episode(self, row: sqlite3.Row) -> Episode:
        """Convert database row to Episode object"""
        return Episode(
            session_id=row['session_id'],
            exchange_number=row['exchange_number'],
            user_text=row['user_text'],
            agent_text=row['agent_text'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            is_session_start=bool(row['is_session_start']),
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

    def end_session(self):
        """Properly close current session"""
        if self.current_session_id:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions
                    SET end_time = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (self.current_session_id,))

            print(f"📍 Session ended: {self.current_session_id}")
            self.current_session_id = None
            self.current_exchange_number = 0


# Integration with COCO
class COCOMemoryIntegration:
    """
    Drop-in replacement for COCO's existing memory system
    Maintains backward compatibility while adding precision
    """

    def __init__(self, existing_memory_system, enhanced_episodic_instance=None):
        self.legacy_memory = existing_memory_system
        # Use shared instance if provided, otherwise create new one
        if enhanced_episodic_instance:
            self.episodic_memory = enhanced_episodic_instance
        else:
            self.episodic_memory = EnhancedEpisodicMemory()
            self.episodic_memory.start_session()

    def add_interaction(self, user_text: str, agent_text: str, metadata: Dict = None):
        """Add interaction to both legacy and enhanced systems"""
        # Add to enhanced episodic memory
        episode = self.episodic_memory.add_exchange(user_text, agent_text, metadata)

        # Add to legacy system for compatibility
        if hasattr(self.legacy_memory, 'add_episode'):
            self.legacy_memory.add_episode(user_text, agent_text)

        return episode

    def handle_temporal_query(self, query: str) -> str:
        """Handle queries about conversation history"""
        result = self.episodic_memory.clarify_temporal_reference(query)

        if result['episode']:
            return f"""
✅ Found it! {result['interpretation']}

User said: "{result['episode'].user_text}"

I responded: "{result['episode'].agent_text[:200]}..."

Exchange #{result['episode'].exchange_number} at {result['episode'].timestamp.strftime('%H:%M:%S')}
"""
        else:
            return result['clarification']

    def get_context_for_prompt(self) -> str:
        """Get properly formatted context for COCO's prompt"""
        boundaries = self.episodic_memory.get_session_boundaries()
        recent = self.episodic_memory.get_current_session_history(limit=5)

        context = f"""
📍 Current Session Context:
- Session ID: {boundaries['current_session']['id']}
- Started: {boundaries['current_session']['start_time']}
- Total Exchanges: {boundaries['current_session']['total_exchanges']}

Recent Conversation:
"""
        for episode in recent:
            context += f"\n[#{episode.exchange_number}] User: {episode.user_text[:100]}..."

        return context


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Enhanced Episodic Memory")

    memory = EnhancedEpisodicMemory()

    # Simulate conversation
    memory.add_exchange(
        "excellent work! great job getting that info!",
        "Thank you! I successfully retrieved the RX2 intelligence reports..."
    )

    memory.add_exchange(
        "nope, thats not it...it was something else. what you doing something?",
        "Let me check my memory more carefully..."
    )

    # Test precise recall
    first = memory.get_first_exchange_of_session()
    print(f"\n✅ First exchange: {first.user_text}")

    # Test temporal clarification
    result = memory.clarify_temporal_reference("first thing")
    print(f"\n✅ Temporal clarification: {result['clarification']}")

    # Stats
    stats = memory.get_statistics()
    print(f"\n📊 Stats: {stats}")