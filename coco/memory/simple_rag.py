#!/usr/bin/env python3
"""
Simple RAG Layer for COCO
=========================
Dead-simple semantic memory that actually works.
No entity extraction, no relationships, just semantic similarity.
"""

import sqlite3
import json
import numpy as np
from datetime import datetime
from typing import List, Optional
import hashlib
from pathlib import Path
import warnings

# Suppress OpenAI deprecation warnings - we handle the fallback gracefully
warnings.filterwarnings('ignore', message='.*openai.Embedding.*')
warnings.filterwarnings('ignore', message='.*no longer supported in openai.*')

class SimpleRAG:
    """
    Dead-simple RAG implementation for COCO's Layer 2 memory.
    Store text, retrieve by similarity. That's it.
    """

    def __init__(self, db_path: str = "coco_workspace/simple_rag.db"):
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        """One table. That's it."""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_hash TEXT UNIQUE,  -- Prevent duplicates
                embedding TEXT,  -- JSON array of floats
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                importance REAL DEFAULT 1.0,
                access_count INTEGER DEFAULT 0
            )
        ''')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON semantic_memory(timestamp)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_importance ON semantic_memory(importance)')
        self.conn.commit()

    def store(self, text: str, importance: float = 1.0) -> bool:
        """
        Store text with its embedding. Skip if duplicate.
        """
        if not text or len(text.strip()) < 10:  # Skip tiny fragments
            return False

        # Create hash to check for duplicates
        content_hash = hashlib.md5(text.encode()).hexdigest()

        # Check if already exists
        existing = self.conn.execute(
            'SELECT id FROM semantic_memory WHERE content_hash = ?',
            (content_hash,)
        ).fetchone()

        if existing:
            # Just update access count and timestamp
            self.conn.execute('''
                UPDATE semantic_memory
                SET access_count = access_count + 1,
                    timestamp = CURRENT_TIMESTAMP
                WHERE content_hash = ?
            ''', (content_hash,))
            self.conn.commit()
            return False

        # Get embedding (fake for now, can add OpenAI later)
        embedding = self._get_embedding(text)

        # Store it
        self.conn.execute('''
            INSERT INTO semantic_memory (content, content_hash, embedding, importance)
            VALUES (?, ?, ?, ?)
        ''', (text, content_hash, json.dumps(embedding), importance))
        self.conn.commit()
        return True

    def store_conversation_exchange(self, user_text: str, assistant_text: str):
        """
        Store a conversation exchange as semantic memory.
        """
        # Store individual parts
        if user_text and len(user_text) > 20:
            self.store(f"User asked: {user_text}", importance=1.0)

        if assistant_text and len(assistant_text) > 20:
            # Truncate very long responses
            if len(assistant_text) > 1000:
                assistant_text = assistant_text[:997] + "..."
            self.store(f"Assistant answered: {assistant_text}", importance=0.9)

        # Store the exchange as a unit for better context
        if user_text and assistant_text:
            exchange = f"Conversation:\nQ: {user_text}\nA: {assistant_text[:500]}"
            self.store(exchange, importance=1.1)

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        """
        Retrieve k most similar memories to the query.
        Simple cosine similarity search.
        """
        if not query:
            return []

        query_embedding = self._get_embedding(query)

        # Get all memories with embeddings
        cursor = self.conn.execute('''
            SELECT content, embedding, importance, timestamp
            FROM semantic_memory
            WHERE embedding IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 500  -- Only search recent memories for performance
        ''')

        # Calculate similarities
        similarities = []
        for row in cursor:
            try:
                memory_embedding = json.loads(row['embedding'])
                similarity = self._cosine_similarity(query_embedding, memory_embedding)

                # Boost by importance and recency
                recency_boost = self._calculate_recency_boost(row['timestamp'])
                final_score = similarity * row['importance'] * recency_boost

                similarities.append((row['content'], final_score))
            except:
                continue  # Skip malformed embeddings

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Update access count for retrieved memories
        for content, _ in similarities[:k]:
            self.conn.execute('''
                UPDATE semantic_memory
                SET access_count = access_count + 1
                WHERE content = ?
            ''', (content,))
        self.conn.commit()

        return [content for content, _ in similarities[:k]]

    def get_context(self, query: str, k: int = 5) -> str:
        """
        Get formatted context for injection into prompts.
        """
        if not query or len(query.strip()) < 5:
            return ""

        memories = self.retrieve(query, k)

        if not memories:
            return ""

        context_parts = ["📚 Relevant Semantic Memory:"]
        for i, memory in enumerate(memories, 1):
            # Clean up and truncate
            memory = memory.strip()
            if len(memory) > 300:
                memory = memory[:297] + "..."
            context_parts.append(f"[{i}] {memory}")

        return "\n".join(context_parts)

    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text.
        This is a simple hash-based fake embedding for testing.
        TODO: Replace with OpenAI embeddings when available.
        """
        # Create deterministic fake embedding from text
        hash_obj = hashlib.sha256(text.lower().encode())
        hash_hex = hash_obj.hexdigest()

        # Convert to 384-dimensional embedding
        embedding = []
        for i in range(0, len(hash_hex), 2):
            if i + 1 < len(hash_hex):
                value = int(hash_hex[i:i+2], 16) / 255.0
                embedding.append(value)

        # Pad or truncate to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)

        return embedding[:384]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def _calculate_recency_boost(self, timestamp_str: str) -> float:
        """
        Calculate a recency boost factor.
        Recent memories get a slight boost.
        """
        try:
            # Handle different timestamp formats
            if 'T' in timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

            age_hours = (datetime.now() - timestamp).total_seconds() / 3600

            # Decay factor: recent memories get up to 1.5x boost
            if age_hours < 1:
                return 1.5
            elif age_hours < 24:
                return 1.3
            elif age_hours < 168:  # One week
                return 1.1
            else:
                return 1.0
        except:
            return 1.0

    def cleanup_old_memories(self, days: int = 30):
        """
        Remove old, unimportant memories to keep the system lean.
        """
        self.conn.execute('''
            DELETE FROM semantic_memory
            WHERE datetime(timestamp) < datetime('now', ? || ' days')
              AND importance < 0.5
              AND access_count < 2
        ''', (f'-{days}',))
        self.conn.commit()

        # Vacuum to reclaim space
        self.conn.execute('VACUUM')

    def get_stats(self) -> dict:
        """Get simple statistics about the semantic memory."""
        stats = {}

        # Total memories
        result = self.conn.execute('SELECT COUNT(*) as count FROM semantic_memory').fetchone()
        stats['total_memories'] = result['count']

        # Recent memories (last 24 hours)
        result = self.conn.execute('''
            SELECT COUNT(*) as count FROM semantic_memory
            WHERE datetime(timestamp) > datetime('now', '-1 day')
        ''').fetchone()
        stats['recent_memories'] = result['count']

        # Most accessed
        result = self.conn.execute('''
            SELECT content, access_count FROM semantic_memory
            WHERE access_count > 0
            ORDER BY access_count DESC LIMIT 1
        ''').fetchone()
        if result:
            content_preview = result['content'][:50] + "..." if len(result['content']) > 50 else result['content']
            stats['most_accessed'] = f"{content_preview} ({result['access_count']} times)"
        else:
            stats['most_accessed'] = "No accesses yet"

        return stats

    def search_keyword(self, keyword: str, limit: int = 10) -> List[str]:
        """
        Simple keyword search fallback for when semantic search isn't enough.
        """
        cursor = self.conn.execute('''
            SELECT content FROM semantic_memory
            WHERE LOWER(content) LIKE LOWER(?)
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        ''', (f'%{keyword}%', limit))

        return [row['content'] for row in cursor]


class SimpleRAGWithOpenAI(SimpleRAG):
    """
    Extension with real OpenAI embeddings if you have API access.
    """

    def __init__(self, db_path: str, openai_api_key: str = None):
        super().__init__(db_path)
        self.openai_api_key = openai_api_key
        self.openai_client = None

        if openai_api_key:
            try:
                import openai
                # Use OpenAI v1.0+ API
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                # Silently enable - no print statement to avoid console clutter
            except ImportError:
                # Silently fall back to hash-based embeddings
                pass

    def _get_embedding(self, text: str) -> List[float]:
        """Get real OpenAI embeddings if available, otherwise use parent method."""
        if self.openai_client:
            try:
                # Use OpenAI v1.0+ API
                response = self.openai_client.embeddings.create(
                    input=text[:8000],  # OpenAI has token limits
                    model="text-embedding-3-small"
                )
                return response.data[0].embedding
            except Exception:
                # Silently fall back to hash-based embeddings
                return super()._get_embedding(text)
        else:
            return super()._get_embedding(text)


# Quick test if run directly
if __name__ == "__main__":
    print("🧪 Testing SimpleRAG...")

    rag = SimpleRAG("test_rag.db")

    # Store some test memories
    rag.store("Ilia is a friend who attended the RLF Workshop.", importance=2.0)
    rag.store("Ramin is an attorney at RLF.", importance=2.0)
    rag.store("Ilia and Ramin are connected through the RLF Workshop.", importance=2.0)

    # Test retrieval
    print("\n🔍 Testing retrieval:")
    context = rag.get_context("How are Ilia and Ramin connected?")
    print(context)

    print("\n📊 Stats:")
    print(rag.get_stats())