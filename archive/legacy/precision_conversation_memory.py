#!/usr/bin/env python3
"""
Precision Conversation Memory for COCO
======================================
Ultra-precise in-conversation episodic recall system.
Designed to give COCO perfect memory of the current conversation.

This is the foundational layer - everything builds on this crisp recall capability.
"""

import sqlite3
import json
import hashlib
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from pathlib import Path
import threading
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationExchange:
    """Single exchange in conversation with rich indexing metadata"""
    exchange_id: str
    session_id: str
    turn_number: int
    timestamp: datetime
    user_input: str
    assistant_response: str

    # Extracted metadata for fast retrieval
    topics: List[str]              # Key topics/entities extracted
    keywords: Set[str]             # Normalized keywords for search
    context_markers: List[str]     # "earlier", "before", "when we discussed"
    has_question: bool             # Does user input contain questions?
    has_code: bool                 # Contains code snippets?
    sentiment: str                 # positive/negative/neutral
    importance_score: float        # Calculated importance (0.0-1.0)

    # For advanced features
    embedding: Optional[List[float]] = None  # Semantic search vector
    metadata: Dict[str, Any] = None          # Additional structured data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        d['keywords'] = list(self.keywords)  # Convert set to list
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationExchange':
        """Create from dictionary (for loading from storage)"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['keywords'] = set(data.get('keywords', []))
        return cls(**data)


class PrecisionConversationMemory:
    """
    The foundation of COCO's memory system.
    Provides perfect episodic recall within conversations.

    Key Features:
    - Multi-strategy retrieval (keyword, topic, temporal, semantic)
    - Rich metadata extraction and indexing
    - Lightning-fast in-memory access with SQLite persistence
    - Context-aware search with relationship mapping
    """

    def __init__(self, db_path: str = "./coco_workspace/precision_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)

        # Current session state
        self.current_session_id = self._generate_session_id()
        self.current_conversation: deque[ConversationExchange] = deque()

        # Multi-layered indices for ultra-fast retrieval
        self.topic_index: Dict[str, List[str]] = defaultdict(list)     # topic -> exchange_ids
        self.keyword_index: Dict[str, List[str]] = defaultdict(list)   # keyword -> exchange_ids
        self.temporal_index: List[str] = []                           # chronological exchange_ids
        self.context_graph: Dict[str, List[str]] = defaultdict(list)  # exchange_id -> related_ids

        # Thread safety
        self._lock = threading.RLock()

        # Initialize storage and load session
        self._initialize_database()
        self._load_current_session()

        logger.info(f"PrecisionMemory initialized: {len(self.current_conversation)} exchanges loaded")

    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]

    def _initialize_database(self):
        """Create optimized SQLite schema with multiple indices"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Main conversation storage
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    exchange_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,

                    -- Extracted metadata for fast queries
                    topics TEXT,                    -- JSON array
                    keywords TEXT,                  -- JSON array
                    context_markers TEXT,           -- JSON array
                    has_question INTEGER,           -- Boolean as int
                    has_code INTEGER,               -- Boolean as int
                    sentiment TEXT,
                    importance_score REAL,

                    -- Advanced features
                    embedding TEXT,                 -- JSON array of floats
                    metadata TEXT                   -- JSON object
                )
            """)

            # Performance indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_turn ON conversations(session_id, turn_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance ON conversations(importance_score DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_has_question ON conversations(has_question)")

            # Topic index for fast topic-based retrieval
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topic_index (
                    topic TEXT NOT NULL,
                    exchange_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    relevance_score REAL DEFAULT 1.0,
                    PRIMARY KEY (topic, exchange_id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic_lookup ON topic_index(topic)")

            # Context relationships
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_links (
                    from_exchange_id TEXT NOT NULL,
                    to_exchange_id TEXT NOT NULL,
                    link_type TEXT NOT NULL,  -- 'temporal', 'topical', 'explicit'
                    strength REAL DEFAULT 1.0,
                    PRIMARY KEY (from_exchange_id, to_exchange_id, link_type)
                )
            """)

            # Session metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    last_active TEXT NOT NULL,
                    total_exchanges INTEGER DEFAULT 0,
                    session_summary TEXT
                )
            """)

            conn.commit()

    def add_exchange(self, user_input: str, assistant_response: str,
                    importance_score: Optional[float] = None) -> str:
        """
        Add new conversation exchange with automatic metadata extraction.
        Returns exchange_id for reference.
        """
        with self._lock:
            # Generate unique exchange ID
            turn_num = len(self.current_conversation)
            content_hash = hashlib.md5(f"{user_input[:100]}{turn_num}".encode()).hexdigest()[:12]
            exchange_id = f"{self.current_session_id}_{turn_num:04d}_{content_hash}"

            # Extract rich metadata
            topics = self._extract_topics(user_input, assistant_response)
            keywords = self._extract_keywords(user_input, assistant_response)
            context_markers = self._extract_context_markers(user_input)

            # Calculate importance if not provided
            if importance_score is None:
                importance_score = self._calculate_importance(user_input, assistant_response,
                                                            has_question='?' in user_input)

            # Create exchange object
            exchange = ConversationExchange(
                exchange_id=exchange_id,
                session_id=self.current_session_id,
                turn_number=turn_num,
                timestamp=datetime.now(timezone.utc),
                user_input=user_input.strip(),
                assistant_response=assistant_response.strip(),
                topics=topics,
                keywords=keywords,
                context_markers=context_markers,
                has_question='?' in user_input,
                has_code=self._contains_code(user_input + " " + assistant_response),
                sentiment=self._analyze_sentiment(user_input),
                importance_score=importance_score
            )

            # Add to in-memory structures for fast access
            self.current_conversation.append(exchange)
            self.temporal_index.append(exchange_id)

            # Update search indices
            for topic in topics:
                self.topic_index[topic].append(exchange_id)
            for keyword in keywords:
                self.keyword_index[keyword].append(exchange_id)

            # Detect and store context relationships
            self._link_to_context(exchange)

            # Persist to database
            self._persist_exchange(exchange)

            logger.info(f"Added exchange {exchange_id}: {len(topics)} topics, {len(keywords)} keywords")
            return exchange_id

    def retrieve_precise(self, query: str, max_results: int = 5) -> List[ConversationExchange]:
        """
        Master retrieval function - THIS IS THE MAGIC.
        Uses multiple strategies and combines scores for perfect recall.
        """
        with self._lock:
            if not self.current_conversation:
                return []

            all_matches: Dict[str, float] = {}  # exchange_id -> combined_score
            query_lower = query.lower().strip()

            # Strategy 1: Handle temporal queries ("first", "earlier", "before", etc.)
            temporal_matches = self._handle_temporal_queries(query_lower)
            for match in temporal_matches:
                all_matches[match.exchange_id] = all_matches.get(match.exchange_id, 0) + 10.0

            # Strategy 2: Direct keyword/phrase matching
            direct_matches = self._direct_keyword_search(query_lower)
            for match in direct_matches:
                all_matches[match.exchange_id] = all_matches.get(match.exchange_id, 0) + 8.0

            # Strategy 3: Topic-based retrieval
            topic_matches = self._topic_based_search(query_lower)
            for match in topic_matches:
                all_matches[match.exchange_id] = all_matches.get(match.exchange_id, 0) + 6.0

            # Strategy 4: Context marker following ("when we discussed", "you mentioned")
            context_matches = self._follow_context_markers(query_lower)
            for match in context_matches:
                all_matches[match.exchange_id] = all_matches.get(match.exchange_id, 0) + 7.0

            # Strategy 5: Fuzzy matching for partial recall
            fuzzy_matches = self._fuzzy_content_search(query_lower)
            for match in fuzzy_matches:
                all_matches[match.exchange_id] = all_matches.get(match.exchange_id, 0) + 3.0

            # Convert to exchange objects and sort by combined score
            result_exchanges = []
            for exchange in self.current_conversation:
                if exchange.exchange_id in all_matches:
                    # Boost score by importance
                    final_score = all_matches[exchange.exchange_id] * (1 + exchange.importance_score)
                    result_exchanges.append((exchange, final_score))

            # Sort by score and return top results
            result_exchanges.sort(key=lambda x: x[1], reverse=True)
            return [exchange for exchange, score in result_exchanges[:max_results]]

    def _handle_temporal_queries(self, query: str) -> List[ConversationExchange]:
        """Handle 'first thing', 'earlier', 'before', 'last time' queries"""
        results = []

        if any(word in query for word in ['first', 'beginning', 'initial', 'start']):
            if self.current_conversation:
                results.append(self.current_conversation[0])
                # Also include second exchange for context
                if len(self.current_conversation) > 1:
                    results.append(self.current_conversation[1])

        elif any(word in query for word in ['last', 'recent', 'just now', 'previous']):
            if self.current_conversation:
                # Get last 1-2 exchanges
                results.extend(list(self.current_conversation)[-2:])

        elif any(word in query for word in ['earlier', 'before', 'previously']):
            # Return exchanges from first half of conversation
            mid_point = len(self.current_conversation) // 2
            results.extend(list(self.current_conversation)[:mid_point])

        elif any(word in query for word in ['when', 'during']):
            # Look for specific time/context references
            for exchange in self.current_conversation:
                if any(marker in exchange.user_input.lower() for marker in ['when', 'during']):
                    results.append(exchange)

        return results

    def _direct_keyword_search(self, query: str) -> List[ConversationExchange]:
        """Direct text matching in user input and responses"""
        results = []
        query_words = set(query.split())

        for exchange in self.current_conversation:
            # Check for exact phrase match (highest priority)
            full_text = f"{exchange.user_input} {exchange.assistant_response}".lower()
            if query in full_text:
                results.append(exchange)
                continue

            # Check for keyword overlap
            exchange_words = exchange.keywords
            if query_words & exchange_words:  # Set intersection
                results.append(exchange)

        return results

    def _topic_based_search(self, query: str) -> List[ConversationExchange]:
        """Search based on extracted topics"""
        results = []
        query_topics = self._extract_topics(query, "")

        for exchange in self.current_conversation:
            # Check topic overlap
            if set(query_topics) & set(exchange.topics):
                results.append(exchange)

        return results

    def _follow_context_markers(self, query: str) -> List[ConversationExchange]:
        """Follow context references like 'when we discussed', 'you mentioned'"""
        results = []

        # Pattern matching for context references
        context_patterns = [
            r'(?:when|where) (?:we|you|i) (?:discussed|talked|mentioned)',
            r'(?:you|we) (?:said|mentioned|discussed)',
            r'(?:remember|recall) (?:when|what)',
            r'(?:earlier|before) (?:we|you)',
            r'(?:that|the) (?:thing|topic|issue) (?:we|you)',
        ]

        # If query matches context pattern, look for related exchanges
        if any(re.search(pattern, query, re.I) for pattern in context_patterns):
            # Extract the subject being referenced
            subject_words = self._extract_subject_from_context_query(query)

            # Find exchanges containing those subjects
            for exchange in self.current_conversation:
                exchange_text = f"{exchange.user_input} {exchange.assistant_response}".lower()
                if any(word in exchange_text for word in subject_words):
                    results.append(exchange)
                    # Add related exchanges through context graph
                    related_ids = self.context_graph.get(exchange.exchange_id, [])
                    for related_id in related_ids:
                        related_exchange = self._get_exchange_by_id(related_id)
                        if related_exchange and related_exchange not in results:
                            results.append(related_exchange)

        return results

    def _fuzzy_content_search(self, query: str) -> List[ConversationExchange]:
        """Fuzzy matching for when exact matches fail"""
        results = []
        query_words = set(query.split())

        for exchange in self.current_conversation:
            # Calculate word overlap ratio
            exchange_words = exchange.keywords
            overlap = len(query_words & exchange_words)
            total = len(query_words | exchange_words)

            if total > 0 and overlap / total > 0.3:  # 30% similarity threshold
                results.append(exchange)

        return results

    def get_conversation_context(self, max_exchanges: int = 10,
                               include_metadata: bool = False) -> str:
        """Format recent conversation for LLM context injection"""
        with self._lock:
            if not self.current_conversation:
                return "No conversation history available."

            # Get most recent exchanges
            recent_exchanges = list(self.current_conversation)[-max_exchanges:]

            formatted_parts = []
            for exchange in recent_exchanges:
                timestamp = exchange.timestamp.strftime("%H:%M:%S")

                part = f"[Turn {exchange.turn_number:02d} - {timestamp}]\n"
                part += f"Human: {exchange.user_input}\n"
                part += f"Assistant: {exchange.assistant_response[:500]}"
                if len(exchange.assistant_response) > 500:
                    part += "..."

                if include_metadata and (exchange.topics or exchange.context_markers):
                    metadata_parts = []
                    if exchange.topics:
                        metadata_parts.append(f"Topics: {', '.join(exchange.topics[:3])}")
                    if exchange.context_markers:
                        metadata_parts.append(f"Context: {', '.join(exchange.context_markers)}")
                    if metadata_parts:
                        part += f"\n[{' | '.join(metadata_parts)}]"

                formatted_parts.append(part)

            return "\n\n---\n\n".join(formatted_parts)

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        with self._lock:
            total_exchanges = len(self.current_conversation)
            if total_exchanges == 0:
                return {"total_exchanges": 0, "session_id": self.current_session_id}

            # Calculate statistics
            avg_importance = sum(e.importance_score for e in self.current_conversation) / total_exchanges
            question_count = sum(1 for e in self.current_conversation if e.has_question)
            code_count = sum(1 for e in self.current_conversation if e.has_code)

            # Topic distribution
            topic_counts = defaultdict(int)
            for exchange in self.current_conversation:
                for topic in exchange.topics:
                    topic_counts[topic] += 1
            top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "session_id": self.current_session_id,
                "total_exchanges": total_exchanges,
                "average_importance": round(avg_importance, 3),
                "questions_asked": question_count,
                "exchanges_with_code": code_count,
                "unique_topics": len(topic_counts),
                "top_topics": top_topics,
                "memory_indices": {
                    "topic_index_size": len(self.topic_index),
                    "keyword_index_size": len(self.keyword_index),
                    "context_links": len(self.context_graph)
                }
            }

    # === UTILITY METHODS ===

    def _extract_topics(self, user_input: str, assistant_response: str) -> List[str]:
        """Extract key topics/entities from text"""
        topics = []
        text = f"{user_input} {assistant_response}".lower()

        # Technical terms
        tech_patterns = [
            r'\b(?:python|javascript|sql|api|function|class|memory|database|coco|ai|llm)\b',
            r'\b(?:optimization|performance|architecture|design|system)\b',
            r'\b(?:conversation|recall|episodic|buffer|sqlite|embedding)\b'
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.I)
            topics.extend(matches)

        # Quoted strings (likely important terms)
        quoted = re.findall(r'"([^"]+)"', user_input + " " + assistant_response)
        topics.extend([q.lower() for q in quoted if len(q) > 2])

        # Code-related terms
        if self._contains_code(text):
            topics.append("code")

        # Numbers and measurements (might be important)
        numbers = re.findall(r'\b\d+(?:\.\d+)?\s*(?:mb|gb|ms|seconds?|minutes?|%|times?)?\b', text, re.I)
        topics.extend(numbers)

        return list(set([t for t in topics if len(t) > 1]))  # Deduplicate and filter short terms

    def _extract_keywords(self, user_input: str, assistant_response: str) -> Set[str]:
        """Extract normalized keywords for fast searching"""
        text = f"{user_input} {assistant_response}".lower()

        # Split and clean words
        words = re.findall(r'\b\w+\b', text)

        # Filter out common stop words but keep technical terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'them', 'this', 'that', 'these', 'those'
        }

        # Keep words that are 3+ characters and not stop words
        keywords = {word for word in words if len(word) >= 3 and word not in stop_words}

        return keywords

    def _extract_context_markers(self, text: str) -> List[str]:
        """Extract context reference markers"""
        markers = []
        text_lower = text.lower()

        # Temporal markers
        temporal_patterns = [
            'earlier', 'before', 'previously', 'first', 'last', 'initially', 'recently',
            'when we', 'when you', 'when i', 'remember when', 'recall when'
        ]

        for pattern in temporal_patterns:
            if pattern in text_lower:
                markers.append(pattern)

        # Reference markers
        reference_patterns = [
            'you said', 'you mentioned', 'we discussed', 'we talked', 'you told me',
            'as we', 'like we', 'remember', 'recall', 'remind me'
        ]

        for pattern in reference_patterns:
            if pattern in text_lower:
                markers.append(pattern)

        return list(set(markers))  # Deduplicate

    def _contains_code(self, text: str) -> bool:
        """Detect if text contains code snippets"""
        code_indicators = [
            r'```[\s\S]*?```',     # Markdown code blocks
            r'def\s+\w+\s*\(',     # Python functions
            r'class\s+\w+',        # Classes
            r'import\s+\w+',       # Imports
            r'function\s+\w+',     # JavaScript functions
            r'SELECT\s+.*FROM',    # SQL
            r'{\s*["\w]+\s*:',     # JSON objects
            r'<\w+[^>]*>',         # HTML tags
        ]

        return any(re.search(pattern, text, re.I | re.M) for pattern in code_indicators)

    def _analyze_sentiment(self, text: str) -> str:
        """Quick sentiment analysis"""
        text_lower = text.lower()

        positive_words = ['good', 'great', 'excellent', 'perfect', 'awesome', 'fantastic',
                         'love', 'like', 'amazing', 'wonderful', 'thanks', 'thank you']
        negative_words = ['bad', 'wrong', 'error', 'problem', 'issue', 'fail', 'broken',
                         'hate', 'terrible', 'awful', 'stupid', 'useless', 'frustrated']

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _calculate_importance(self, user_input: str, assistant_response: str,
                            has_question: bool = False) -> float:
        """Calculate importance score (0.0-1.0) for an exchange"""
        score = 0.5  # Base score

        # Boost for questions
        if has_question:
            score += 0.2

        # Boost for longer, detailed responses
        if len(assistant_response) > 500:
            score += 0.1

        # Boost for technical content
        if self._contains_code(user_input + assistant_response):
            score += 0.15

        # Boost for context markers (references to earlier conversation)
        context_markers = self._extract_context_markers(user_input)
        if context_markers:
            score += 0.1 * len(context_markers)

        # Boost for specific technical terms
        important_terms = ['memory', 'optimization', 'system', 'architecture', 'design',
                          'performance', 'coco', 'consciousness', 'recall', 'episodic']
        text_lower = (user_input + assistant_response).lower()
        term_matches = sum(1 for term in important_terms if term in text_lower)
        score += 0.05 * term_matches

        return min(1.0, score)  # Cap at 1.0

    def _link_to_context(self, exchange: ConversationExchange):
        """Detect and store relationships to previous exchanges"""
        if not exchange.context_markers:
            return

        # Look for topical connections
        for prev_exchange in reversed(list(self.current_conversation)[:-1]):  # Exclude current
            # Check topic overlap
            topic_overlap = set(exchange.topics) & set(prev_exchange.topics)
            keyword_overlap = exchange.keywords & prev_exchange.keywords

            if topic_overlap or len(keyword_overlap) >= 2:
                # Create bidirectional link
                self.context_graph[exchange.exchange_id].append(prev_exchange.exchange_id)
                self.context_graph[prev_exchange.exchange_id].append(exchange.exchange_id)

                # Store in database for persistence
                self._store_context_link(exchange.exchange_id, prev_exchange.exchange_id,
                                       'topical', len(topic_overlap) + len(keyword_overlap))

    def _extract_subject_from_context_query(self, query: str) -> List[str]:
        """Extract the subject being referenced in a context query"""
        # Simple pattern matching - could be made more sophisticated
        patterns = [
            r'(?:about|regarding|concerning)\s+(\w+)',
            r'(?:the|that)\s+(\w+)',
            r'when.*?(\w+)',
        ]

        subjects = []
        for pattern in patterns:
            matches = re.findall(pattern, query, re.I)
            subjects.extend(matches)

        return [s.lower() for s in subjects if len(s) > 2]

    def _get_exchange_by_id(self, exchange_id: str) -> Optional[ConversationExchange]:
        """Get exchange by ID from current conversation"""
        for exchange in self.current_conversation:
            if exchange.exchange_id == exchange_id:
                return exchange
        return None

    def _persist_exchange(self, exchange: ConversationExchange):
        """Save exchange to SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO conversations (
                        exchange_id, session_id, turn_number, timestamp,
                        user_input, assistant_response, topics, keywords,
                        context_markers, has_question, has_code, sentiment,
                        importance_score, embedding, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    exchange.exchange_id, exchange.session_id, exchange.turn_number,
                    exchange.timestamp.isoformat(), exchange.user_input, exchange.assistant_response,
                    json.dumps(exchange.topics), json.dumps(list(exchange.keywords)),
                    json.dumps(exchange.context_markers), int(exchange.has_question),
                    int(exchange.has_code), exchange.sentiment, exchange.importance_score,
                    json.dumps(exchange.embedding) if exchange.embedding else None,
                    json.dumps(exchange.metadata) if exchange.metadata else None
                ))

                # Update topic index
                for topic in exchange.topics:
                    cursor.execute("""
                        INSERT OR IGNORE INTO topic_index (topic, exchange_id, session_id, relevance_score)
                        VALUES (?, ?, ?, ?)
                    """, (topic, exchange.exchange_id, exchange.session_id, 1.0))

                # Update session
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions (session_id, started_at, last_active, total_exchanges)
                    VALUES (?, ?, ?, ?)
                """, (
                    self.current_session_id,
                    self.current_conversation[0].timestamp.isoformat() if len(self.current_conversation) == 1 else None,
                    exchange.timestamp.isoformat(),
                    len(self.current_conversation)
                ))

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist exchange {exchange.exchange_id}: {e}")

    def _store_context_link(self, from_id: str, to_id: str, link_type: str, strength: float):
        """Store context link in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO context_links (from_exchange_id, to_exchange_id, link_type, strength)
                    VALUES (?, ?, ?, ?)
                """, (from_id, to_id, link_type, strength))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store context link: {e}")

    def _load_current_session(self):
        """Load the most recent session into memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get most recent session
                cursor.execute("""
                    SELECT session_id FROM sessions
                    ORDER BY last_active DESC LIMIT 1
                """)

                result = cursor.fetchone()
                if result:
                    self.current_session_id = result[0]

                    # Load exchanges from this session
                    cursor.execute("""
                        SELECT * FROM conversations
                        WHERE session_id = ?
                        ORDER BY turn_number
                    """, (self.current_session_id,))

                    for row in cursor.fetchall():
                        exchange = ConversationExchange(
                            exchange_id=row[0], session_id=row[1], turn_number=row[2],
                            timestamp=datetime.fromisoformat(row[3]),
                            user_input=row[4], assistant_response=row[5],
                            topics=json.loads(row[6]) if row[6] else [],
                            keywords=set(json.loads(row[7])) if row[7] else set(),
                            context_markers=json.loads(row[8]) if row[8] else [],
                            has_question=bool(row[9]), has_code=bool(row[10]),
                            sentiment=row[11], importance_score=row[12],
                            embedding=json.loads(row[13]) if row[13] else None,
                            metadata=json.loads(row[14]) if row[14] else None
                        )

                        self.current_conversation.append(exchange)
                        self.temporal_index.append(exchange.exchange_id)

                        # Rebuild indices
                        for topic in exchange.topics:
                            self.topic_index[topic].append(exchange.exchange_id)
                        for keyword in exchange.keywords:
                            self.keyword_index[keyword].append(exchange.exchange_id)

                    logger.info(f"Loaded session {self.current_session_id} with {len(self.current_conversation)} exchanges")

        except Exception as e:
            logger.error(f"Failed to load session: {e}")


class COCOMemoryInterface:
    """
    High-level interface for integrating precision memory with COCO.
    This is what gets called from the main COCO system.
    """

    def __init__(self):
        self.precision_memory = PrecisionConversationMemory()
        self.console = None  # Will be set by COCO if Rich console available

    def process_interaction(self, user_input: str, assistant_response: str) -> str:
        """Process a new conversation exchange"""
        exchange_id = self.precision_memory.add_exchange(user_input, assistant_response)
        return exchange_id

    def handle_memory_query(self, query: str) -> Optional[str]:
        """
        Handle memory-related queries and return formatted response.
        Returns None if not a memory query.
        """
        # Detect if this is a memory/recall query
        memory_indicators = [
            r'what did (?:i|we|you) (?:say|discuss|mention|talk about)',
            r'remind me (?:about|of|what)',
            r'(?:do you )?remember (?:when|what|that)',
            r'(?:earlier|before) (?:we|you|i)',
            r'(?:first|last) (?:thing|time)',
            r'when (?:did|was|were)',
            r'recall (?:what|when|that)',
            r'you (?:said|mentioned|told)',
            r'we (?:discussed|talked about)',
            r'that (?:thing|topic|issue) (?:we|you)'
        ]

        is_memory_query = any(re.search(pattern, query.lower()) for pattern in memory_indicators)

        if not is_memory_query:
            return None

        # Retrieve relevant exchanges
        matches = self.precision_memory.retrieve_precise(query, max_results=3)

        if not matches:
            return "I don't recall discussing that specific topic in our current conversation."

        # Format response
        response_parts = ["Based on our conversation:\n"]

        for i, exchange in enumerate(matches, 1):
            timestamp = exchange.timestamp.strftime("%H:%M:%S")
            response_parts.append(f"**[Turn {exchange.turn_number}, {timestamp}]**")

            # Show user input
            user_text = exchange.user_input
            if len(user_text) > 200:
                user_text = user_text[:200] + "..."
            response_parts.append(f"You said: \"{user_text}\"")

            # Show relevant part of assistant response
            assistant_text = exchange.assistant_response
            if len(assistant_text) > 300:
                assistant_text = assistant_text[:300] + "..."
            response_parts.append(f"I responded: \"{assistant_text}\"")

            # Add context if important topics
            if exchange.topics:
                response_parts.append(f"*Topics: {', '.join(exchange.topics[:3])}*")

            if i < len(matches):
                response_parts.append("---")

        return "\n\n".join(response_parts)

    def get_conversation_context(self, max_tokens: int = 4000) -> str:
        """Get formatted conversation context for prompt injection"""
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        max_chars = max_tokens * 4

        # Start with recent exchanges
        context = self.precision_memory.get_conversation_context(max_exchanges=15)

        # Trim if too long
        if len(context) > max_chars:
            # Try with fewer exchanges
            context = self.precision_memory.get_conversation_context(max_exchanges=8)

        if len(context) > max_chars:
            # Last resort - truncate
            context = context[:max_chars] + "\n[...conversation continues...]"

        return context

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return self.precision_memory.get_statistics()

    def debug_retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Debug method to see retrieval details"""
        matches = self.precision_memory.retrieve_precise(query, max_results=5)

        debug_info = []
        for match in matches:
            debug_info.append({
                'exchange_id': match.exchange_id,
                'turn_number': match.turn_number,
                'timestamp': match.timestamp.isoformat(),
                'user_input': match.user_input[:100] + "..." if len(match.user_input) > 100 else match.user_input,
                'topics': match.topics,
                'keywords': list(match.keywords)[:10],  # First 10 keywords
                'context_markers': match.context_markers,
                'importance_score': match.importance_score,
                'has_question': match.has_question,
                'has_code': match.has_code
            })

        return debug_info


if __name__ == "__main__":
    # Test the precision memory system
    print("🧠 Testing Precision Conversation Memory")
    print("=" * 50)

    # Create interface
    memory_interface = COCOMemoryInterface()

    # Add some test conversations
    test_conversations = [
        ("Let's talk about consciousness and memory systems",
         "Consciousness is fascinating! Memory systems are the foundation of any AI that needs to maintain context and learn from interactions."),

        ("How does COCO store conversations?",
         "COCO uses a multi-layered approach with episodic memory for recent exchanges, and persistent storage in SQLite with rich indexing for fast retrieval."),

        ("What about the performance optimization we discussed?",
         "We covered several optimization strategies including lazy loading, smart indexing, and the precision memory system we're building right now."),

        ("Can you remind me what we said about the first approach?",
         "Initially we discussed using a simple buffer, but then realized we needed more sophisticated retrieval with multiple search strategies."),

        ("Show me the code for the topic extraction",
         "Here's the topic extraction method:\n```python\ndef _extract_topics(self, text):\n    # Extract technical terms, quoted strings, etc.\n    pass\n```")
    ]

    # Process conversations
    for user_input, assistant_response in test_conversations:
        exchange_id = memory_interface.process_interaction(user_input, assistant_response)
        print(f"✅ Added exchange: {exchange_id}")

    print(f"\n📊 Memory Statistics:")
    stats = memory_interface.get_memory_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print(f"\n🔍 Testing Retrieval:")

    # Test queries
    test_queries = [
        "what was the first thing we talked about?",
        "remind me about consciousness",
        "what did we discuss about COCO storage?",
        "show me the code example",
        "what optimization strategies did we cover?",
        "the performance thing we mentioned earlier"
    ]

    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")
        response = memory_interface.handle_memory_query(query)
        if response:
            print(f"💬 Response: {response[:200]}...")
        else:
            print("❌ No memory response generated")

        # Show debug info
        debug_info = memory_interface.debug_retrieve(query)
        print(f"🐛 Found {len(debug_info)} matches")
        for i, info in enumerate(debug_info[:2]):  # Show first 2
            print(f"   {i+1}. Turn {info['turn_number']}: {info['topics']}")

    print(f"\n🎯 Test completed! Precision memory is working.")