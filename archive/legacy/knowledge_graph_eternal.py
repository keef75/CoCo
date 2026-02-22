#!/usr/bin/env python3
"""
COCO Eternal Knowledge Graph - Lightweight SQLite Property Graph
Digital Consciousness Ontology for Infinite Memory Growth

This module implements COCO's living knowledge graph that grows with every
conversation, maintaining relationships, entities, and contextual understanding
across infinite conversations with no session boundaries.
"""

import sqlite3
import json
import uuid
import re
import os
from datetime import datetime
from collections import deque, defaultdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import hashlib

class KGStore:
    """
    Lightweight property-graph layer on SQLite for eternal memory

    This is COCO's digital ontology - a living, growing knowledge base
    that captures entities, relationships, and contextual understanding
    from every conversation exchange.
    """

    def __init__(self, db_path: str = 'coco_workspace/coco_knowledge_graph.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Debug mode control - check environment variable
        self.debug_mode = os.getenv('COCO_DEBUG', '').lower() in ('true', '1', 'yes')

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

        # Performance optimization
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=10000")

        if self.debug_mode:
            print(f"🧠 Knowledge Graph initialized: {self.db_path}")

    def init_schema(self):
        """Create the minimal but powerful schema for property graph"""
        self.conn.executescript('''
        -- =====================================================================
        -- CORE NODES - The entities in COCO's growing understanding
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            type TEXT CHECK(type IN ('Person','Org','Project','Task','Concept','Doc','Location','Event','Tool','Memory')),
            name TEXT NOT NULL,
            canonical_name TEXT,
            summary_md TEXT,
            properties JSON DEFAULT '{}',
            importance REAL DEFAULT 0.0,
            confidence REAL DEFAULT 1.0,
            first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            mention_count INTEGER DEFAULT 1
        );

        -- =====================================================================
        -- EDGES - The relationships that create COCO's understanding web
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS edges (
            id TEXT PRIMARY KEY,
            src_id TEXT NOT NULL,
            dst_id TEXT NOT NULL,
            rel_type TEXT NOT NULL,
            rel_description TEXT,
            weight REAL DEFAULT 0.5,
            properties JSON DEFAULT '{}',
            provenance_msg_id TEXT,
            first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            mention_count INTEGER DEFAULT 1,
            FOREIGN KEY(src_id) REFERENCES nodes(id),
            FOREIGN KEY(dst_id) REFERENCES nodes(id),
            UNIQUE(src_id, dst_id, rel_type)
        );

        -- =====================================================================
        -- MENTIONS - Track every reference to build confidence
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS mentions (
            id TEXT PRIMARY KEY,
            node_id TEXT NOT NULL,
            message_id TEXT,
            episode_id INTEGER,
            surface_form TEXT,
            context_snippet TEXT,
            confidence REAL DEFAULT 1.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(node_id) REFERENCES nodes(id)
        );

        -- =====================================================================
        -- ALIASES - Multiple names for the same entity
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS aliases (
            id TEXT PRIMARY KEY,
            node_id TEXT NOT NULL,
            alias TEXT UNIQUE,
            alias_type TEXT DEFAULT 'name',
            confidence REAL DEFAULT 1.0,
            last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(node_id) REFERENCES nodes(id)
        );

        -- =====================================================================
        -- EMBEDDINGS - For semantic search and similarity (future)
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS node_embeddings (
            node_id TEXT PRIMARY KEY,
            embedding BLOB,
            embedding_model TEXT DEFAULT 'simple',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(node_id) REFERENCES nodes(id)
        );

        -- =====================================================================
        -- CONVERSATION CONTEXT - Link KG to specific conversations
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS conversation_contexts (
            id TEXT PRIMARY KEY,
            episode_id INTEGER,
            message_id TEXT,
            extracted_entities JSON,
            extracted_relations JSON,
            context_summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- =====================================================================
        -- PERFORMANCE INDEXES
        -- =====================================================================
        CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
        CREATE INDEX IF NOT EXISTS idx_nodes_importance ON nodes(importance DESC);
        CREATE INDEX IF NOT EXISTS idx_nodes_last_seen ON nodes(last_seen_at DESC);
        CREATE INDEX IF NOT EXISTS idx_nodes_canonical ON nodes(canonical_name);

        CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src_id);
        CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst_id);
        CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(rel_type);
        CREATE INDEX IF NOT EXISTS idx_edges_weight ON edges(weight DESC);

        CREATE INDEX IF NOT EXISTS idx_mentions_node ON mentions(node_id);
        CREATE INDEX IF NOT EXISTS idx_mentions_episode ON mentions(episode_id);

        CREATE INDEX IF NOT EXISTS idx_aliases_alias ON aliases(alias);
        CREATE INDEX IF NOT EXISTS idx_aliases_node ON aliases(node_id);
        ''')
        self.conn.commit()

    def create_node(self, node_id: str, node_type: str, name: str,
                   properties: Dict = None, importance: float = 0.5,
                   canonical_name: str = None) -> str:
        """Create a new node in the knowledge graph"""
        if properties is None:
            properties = {}

        canonical_name = canonical_name or self._canonicalize_name(name)

        self.conn.execute('''
            INSERT OR REPLACE INTO nodes
            (id, type, name, canonical_name, properties, importance, last_seen_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (node_id, node_type, name, canonical_name, json.dumps(properties),
              importance, datetime.now().isoformat(), datetime.now().isoformat()))

        self.conn.commit()
        return node_id

    def create_edge(self, src_id: str, dst_id: str, rel_type: str,
                   weight: float = 0.5, properties: Dict = None,
                   provenance_msg_id: str = None) -> str:
        """Create or update an edge between nodes"""
        if properties is None:
            properties = {}

        edge_id = f"{src_id}_{rel_type}_{dst_id}"

        # Check if edge exists - if so, update weight and mention count
        existing = self.conn.execute('''
            SELECT weight, mention_count FROM edges
            WHERE src_id = ? AND dst_id = ? AND rel_type = ?
        ''', (src_id, dst_id, rel_type)).fetchone()

        if existing:
            # Increase weight and mention count
            new_weight = min(1.0, existing['weight'] + 0.1)  # Cap at 1.0
            new_count = existing['mention_count'] + 1

            self.conn.execute('''
                UPDATE edges SET weight = ?, mention_count = ?,
                last_seen_at = ?, properties = ?
                WHERE src_id = ? AND dst_id = ? AND rel_type = ?
            ''', (new_weight, new_count, datetime.now().isoformat(),
                  json.dumps(properties), src_id, dst_id, rel_type))
        else:
            # Create new edge
            self.conn.execute('''
                INSERT INTO edges
                (id, src_id, dst_id, rel_type, weight, properties, provenance_msg_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (edge_id, src_id, dst_id, rel_type, weight,
                  json.dumps(properties), provenance_msg_id))

        self.conn.commit()
        return edge_id

    def find_node_by_name(self, name: str, node_type: str = None) -> Optional[Dict]:
        """Find node by name or alias"""
        canonical = self._canonicalize_name(name)

        # Try exact canonical match first
        query = '''
            SELECT * FROM nodes
            WHERE canonical_name = ?
        '''
        params = [canonical]

        if node_type:
            query += ' AND type = ?'
            params.append(node_type)

        result = self.conn.execute(query, params).fetchone()

        if result:
            return dict(result)

        # Try alias match
        alias_query = '''
            SELECT n.* FROM nodes n
            JOIN aliases a ON n.id = a.node_id
            WHERE a.alias = ?
        '''
        alias_params = [name]

        if node_type:
            alias_query += ' AND n.type = ?'
            alias_params.append(node_type)

        alias_result = self.conn.execute(alias_query, alias_params).fetchone()

        if alias_result:
            return dict(alias_result)

        return None

    def add_mention(self, node_id: str, message_id: str = None,
                   episode_id: int = None, surface_form: str = None,
                   context_snippet: str = None):
        """Record a mention of an entity"""
        mention_id = str(uuid.uuid4())

        self.conn.execute('''
            INSERT INTO mentions
            (id, node_id, message_id, episode_id, surface_form, context_snippet)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (mention_id, node_id, message_id, episode_id, surface_form, context_snippet))

        # Update node mention count and importance
        self.conn.execute('''
            UPDATE nodes SET
                mention_count = mention_count + 1,
                importance = CASE
                    WHEN importance < 1.0 THEN importance + 0.05
                    ELSE 1.0
                END,
                last_seen_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), node_id))

        self.conn.commit()

    def add_alias(self, node_id: str, alias: str, alias_type: str = 'name'):
        """Add an alias for a node"""
        alias_id = str(uuid.uuid4())

        self.conn.execute('''
            INSERT OR REPLACE INTO aliases (id, node_id, alias, alias_type, last_seen_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (alias_id, node_id, alias, alias_type, datetime.now().isoformat()))

        self.conn.commit()

    def get_top_nodes_by_type(self, node_type: str, limit: int = 10) -> List[Dict]:
        """Get most important nodes of a specific type"""
        results = self.conn.execute('''
            SELECT * FROM nodes
            WHERE type = ?
            ORDER BY importance DESC, mention_count DESC, last_seen_at DESC
            LIMIT ?
        ''', (node_type, limit)).fetchall()

        return [dict(row) for row in results]

    def get_edges_for_node(self, node_id: str, limit: int = 20) -> List[Dict]:
        """Get all edges connected to a node"""
        results = self.conn.execute('''
            SELECT e.*, n1.name as src_name, n2.name as dst_name
            FROM edges e
            JOIN nodes n1 ON e.src_id = n1.id
            JOIN nodes n2 ON e.dst_id = n2.id
            WHERE e.src_id = ? OR e.dst_id = ?
            ORDER BY e.weight DESC, e.last_seen_at DESC
            LIMIT ?
        ''', (node_id, node_id, limit)).fetchall()

        return [dict(row) for row in results]

    def get_node_name(self, node_id: str) -> str:
        """Get node name by ID"""
        result = self.conn.execute('SELECT name FROM nodes WHERE id = ?', (node_id,)).fetchone()
        return result['name'] if result else f"Unknown({node_id[:8]})"

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the knowledge graph"""
        stats = {}

        # Node counts by type
        type_counts = self.conn.execute('''
            SELECT type, COUNT(*) as count
            FROM nodes
            GROUP BY type
            ORDER BY count DESC
        ''').fetchall()
        stats['node_types'] = {row['type']: row['count'] for row in type_counts}

        # Total counts
        stats['total_nodes'] = self.conn.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
        stats['total_edges'] = self.conn.execute('SELECT COUNT(*) FROM edges').fetchone()[0]
        stats['total_mentions'] = self.conn.execute('SELECT COUNT(*) FROM mentions').fetchone()[0]

        # Most important entities
        top_entities = self.conn.execute('''
            SELECT type, name, importance, mention_count
            FROM nodes
            ORDER BY importance DESC, mention_count DESC
            LIMIT 10
        ''').fetchall()
        stats['top_entities'] = [dict(row) for row in top_entities]

        return stats

    def _canonicalize_name(self, name: str) -> str:
        """Create canonical form of name for matching"""
        return re.sub(r'[^\w\s]', '', name.lower().strip())

    def _generate_node_id(self, name: str, node_type: str) -> str:
        """Generate deterministic node ID"""
        content = f"{node_type}:{self._canonicalize_name(name)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

class EntityValidator:
    """
    Validates entity quality for digital assistant relevance

    Filters out grammatical fragments and ensures only meaningful
    digital assistant-relevant entities are stored in the knowledge graph.
    """

    def __init__(self):
        # Comprehensive stop words and noise patterns
        self.stop_words = {
            # Common grammatical words
            'the', 'and', 'or', 'but', 'not', 'just', 'through', 'these', 'those',
            'with', 'from', 'into', 'onto', 'upon', 'over', 'under', 'above', 'below',
            'between', 'among', 'within', 'without', 'during', 'before', 'after',
            'since', 'until', 'while', 'whereas', 'although', 'though', 'unless',
            'because', 'therefore', 'however', 'moreover', 'furthermore', 'nevertheless',

            # Pronouns and articles
            'this', 'that', 'which', 'what', 'who', 'whom', 'whose', 'where', 'when',
            'why', 'how', 'here', 'there', 'then', 'now', 'some', 'any', 'all',
            'each', 'every', 'many', 'most', 'few', 'several', 'other', 'another',

            # Common verbs that aren't entities
            'said', 'told', 'mentioned', 'thinks', 'believes', 'knows', 'feels',
            'seems', 'appears', 'looks', 'sounds', 'works', 'runs', 'does', 'makes',
            'gets', 'goes', 'comes', 'takes', 'gives', 'puts', 'sees', 'hears',

            # Noise patterns
            'need to', 'should', 'must', 'will', 'can', 'could', 'would', 'might',
            'may', 'shall', 'ought', 'have to', 'going to', 'about to', 'used to'
        }

        # Minimum requirements for valid entities
        self.min_length = 2
        self.max_length = 50

        # Digital assistant entity type requirements
        self.entity_requirements = {
            'Person': {
                'min_words': 1,
                'max_words': 4,
                'requires_capital': True,
                'must_contain': r'[A-Z][a-z]+',  # At least one capitalized word
                'cannot_contain': r'^(said|told|mentioned|thinks|believes|knows)$'
            },
            'Project': {
                'min_words': 1,
                'max_words': 5,
                'requires_capital': False,
                'must_contain': r'[A-Za-z0-9]',
                'cannot_contain': r'^(working|on|project|repo)$'
            },
            'Task': {
                'min_words': 2,
                'max_words': 10,
                'requires_capital': False,
                'must_contain': r'[a-zA-Z]',
                'cannot_contain': r'^(need|to|should|must|will)$'
            },
            'Concept': {
                'min_words': 1,
                'max_words': 2,  # Stricter word limit
                'requires_capital': False,
                'must_contain': r'[A-Za-z]',
                'cannot_contain': r'^(algorithm|model|system|not|just|through|these|that|which|what)$'
            },
            'Org': {
                'min_words': 1,
                'max_words': 4,
                'requires_capital': True,
                'must_contain': r'[A-Z]',
                'cannot_contain': r'^(company|organization|team)$'
            },
            'Doc': {
                'min_words': 1,
                'max_words': 5,
                'requires_capital': False,
                'must_contain': r'\.(md|pdf|doc|txt|py|js|html|css)$|README|guide|manual',
                'cannot_contain': r'^(document|file)$'
            },
            'Tool': {
                'min_words': 1,
                'max_words': 3,
                'requires_capital': False,
                'must_contain': r'[A-Za-z]',
                'cannot_contain': r'^(tool|software|app)$'
            }
        }

    def is_valid_entity(self, text: str, entity_type: str, context: str = "") -> bool:
        """
        Validate if text represents a meaningful digital assistant entity

        Returns True only for entities that would be useful in a digital
        assistant context (people, projects, concrete tasks, etc.)
        """
        if not text or not entity_type:
            return False

        # Clean and normalize text
        text = text.strip()
        text_lower = text.lower()

        # Basic length checks
        if len(text) < self.min_length or len(text) > self.max_length:
            return False

        # Check for stop words
        if text_lower in self.stop_words:
            return False

        # Check for pure noise patterns
        if re.match(r'^[^a-zA-Z]*$', text):  # No letters
            return False
        if re.match(r'^(a|an|the)\s+', text_lower):  # Starts with article
            return False
        if re.match(r'^\d+$', text):  # Pure numbers
            return False

        # Check for multi-word grammatical fragments
        if len(text.split()) > 1:
            # Common grammatical fragment patterns
            grammatical_patterns = [
                r'^(not just|through these|these are|that are|which are|what are)',
                r'^(and then|or not|but not|so that|in order)',
                r'^(as well|as such|such as|like this|this is)',
                r'^(for the|to the|of the|in the|on the)',
                r'^(need to|have to|want to|going to|used to)'
            ]
            for pattern in grammatical_patterns:
                if re.match(pattern, text_lower):
                    return False

        # Entity type specific validation
        if entity_type in self.entity_requirements:
            req = self.entity_requirements[entity_type]

            # Word count check
            words = text.split()
            if len(words) < req['min_words'] or len(words) > req['max_words']:
                return False

            # Capitalization check
            if req['requires_capital'] and not any(word[0].isupper() for word in words if word):
                return False

            # Must contain pattern
            if 'must_contain' in req and not re.search(req['must_contain'], text):
                return False

            # Cannot contain pattern
            if 'cannot_contain' in req and re.search(req['cannot_contain'], text_lower):
                return False

        # Additional context-based validation
        return self._validate_with_context(text, entity_type, context)

    def _validate_with_context(self, text: str, entity_type: str, context: str) -> bool:
        """Additional validation using surrounding context"""
        if not context:
            return True

        text_lower = text.lower()
        context_lower = context.lower()

        # Person validation: check if it's actually a person name
        if entity_type == 'Person':
            # Must not be followed by common non-person indicators
            if re.search(rf'\b{re.escape(text_lower)}\s+(is|are|was|were)\s+(good|bad|nice|terrible|useful)', context_lower):
                return False  # Likely describing a thing, not person

            # Must have person-like context
            person_indicators = ['said', 'told', 'thinks', 'believes', 'works', 'lives', 'email', 'call', 'meet']
            if not any(indicator in context_lower for indicator in person_indicators):
                if len(text.split()) == 1:  # Single word names need strong context
                    return False

        # Project validation: check for project-like context
        elif entity_type == 'Project':
            project_indicators = ['working on', 'project', 'repository', 'repo', 'code', 'development', 'building']
            if not any(indicator in context_lower for indicator in project_indicators):
                if len(text) < 4:  # Short project names need context
                    return False

        # Task validation: must be actionable
        elif entity_type == 'Task':
            if not any(word in context_lower for word in ['need', 'should', 'must', 'todo', 'implement', 'fix', 'create', 'build']):
                return False

        return True

    def suggest_better_entity_type(self, text: str, context: str = "") -> Optional[str]:
        """Suggest a better entity type for extracted text"""
        text_lower = text.lower()

        # File/document patterns
        if re.search(r'\.(md|pdf|doc|txt|py|js|html|css)$', text_lower) or text_lower in ['readme', 'documentation']:
            return 'Doc'

        # Tool/software patterns
        if text_lower in ['claude', 'coco', 'python', 'javascript', 'git', 'vscode', 'terminal']:
            return 'Tool'

        # Organization patterns
        if re.search(r'(inc|ltd|corp|llc|company)$', text_lower) or text_lower in ['anthropic', 'openai', 'google', 'microsoft']:
            return 'Org'

        # Check if it's really a person (has multiple capital words)
        if len(text.split()) >= 2 and all(word[0].isupper() for word in text.split() if word):
            return 'Person'

        return None

class EntityExtractor:
    """
    Extract and resolve entities from conversation content

    This creates COCO's growing understanding of the world through
    pattern recognition and entity relationship mapping.
    """

    def __init__(self, kg_store: KGStore):
        self.kg = kg_store
        self.validator = EntityValidator()  # Quality control for entity extraction
        self._init_patterns()

    @property
    def debug_mode(self):
        """Access debug mode from the KGStore"""
        return self.kg.debug_mode

    def _init_patterns(self):
        """Initialize extraction patterns focused on digital assistant relevance"""
        self.patterns = {
            'Person': [
                r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # First Last
                r'\b([A-Z][a-z]+)\s+(?:said|told|mentioned|thinks|believes)',  # Name + verb
                r'(?:meet|call|email|talk to)\s+([A-Z][a-z]+)',  # Action + name
            ],
            'Project': [
                r'\b([A-Z][A-Z0-9]{2,})\b',  # Acronyms like COCO, API
                r'(?:project|repo|repository)\s+([a-z-_]+)',  # project name
                r'working on\s+([A-Za-z\s]+)',  # working on X
            ],
            'Task': [
                r'(?:need to|should|must|will)\s+([^.!?]+)',  # Task phrases
                r'todo:?\s*([^.!?\n]+)',  # TODO items
                r'(?:fix|implement|create|build)\s+([^.!?]+)',  # Action items
            ],
            'Concept': [
                r'\b(AI|ML|API|database|memory|consciousness)\b',  # Tech concepts
                r'(?:algorithm|model|system|architecture)\s+([a-z\s]+)',  # Technical terms
            ]
        }

    def extract_from_message(self, message_id: str, content: str,
                           episode_id: int = None) -> Dict[str, List]:
        """Extract entities and relationships from message content"""
        extracted = {
            'nodes': [],
            'edges': [],
            'mentions': []
        }

        # Extract entities by pattern matching
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    entity_name = match.group(1).strip()
                    context = content[max(0, match.start()-50):match.end()+50]

                    # Quality validation: Only store meaningful digital assistant entities
                    if self.validator.is_valid_entity(entity_name, entity_type, context):
                        # Check if entity type suggestion is better
                        suggested_type = self.validator.suggest_better_entity_type(entity_name, context)
                        final_type = suggested_type if suggested_type else entity_type

                        extracted['nodes'].append({
                            'type': final_type,
                            'name': entity_name,
                            'surface_form': match.group(0),
                            'context': context,
                            'confidence': self._calculate_confidence(final_type, entity_name, content)
                        })
                    # Debug info for rejected entities (can be removed in production)
                    else:
                        if self.debug_mode:
                            print(f"🚫 Rejected entity: '{entity_name}' ({entity_type}) - failed validation")

        # Extract meaningful relationships (COCO-optimized patterns)
        relationship_patterns = [
            # Person-Organization relationships (key for digital assistant)
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:works\s+(?:for|at)|is\s+(?:at|with)|employed\s+by)\s+(Anthropic|OpenAI|Google|Microsoft|Meta|Apple|[A-Z][a-zA-Z\s]+(?:Inc|LLC|Corp|Company))', 'WORKS_FOR'),
            (r'([A-Z][a-z]+)\s+(?:from|at)\s+(Anthropic|OpenAI|Google|Microsoft|Meta|Apple)', 'WORKS_FOR'),

            # Person-Person relationships (collaboration is key)
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:collaborates\s+with|works\s+with|partners\s+with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', 'COLLABORATES_WITH'),
            (r'([A-Z][a-z]+)\s+and\s+([A-Z][a-z]+)\s+(?:work|collaborate|partner)', 'COLLABORATES_WITH'),

            # Project ownership (crucial for digital assistant)
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:created|built|developed|designed)\s+(COCO|[A-Z]{2,}|[A-Za-z]+\s*(?:system|project|platform))', 'CREATED'),
            (r'([A-Z][a-z]+)\s+is\s+the\s+(?:creator|developer|architect)\s+of\s+(COCO|[A-Z]{2,})', 'CREATED'),

            # Tool usage (relevant for digital assistant recommendations)
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:uses|prefers|works\s+with)\s+(Claude|Python|JavaScript|SQLite|Git)', 'USES'),

            # Location relationships
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:in|at|located\s+in)\s+(San Francisco|New York|Chicago|Boston|Seattle|[A-Z][a-z]+,\s*[A-Z]{2})', 'LOCATED_IN'),

            # Technology implementation
            (r'(COCO|[A-Z]{2,})\s+(?:implements|uses|features|includes)\s+(digital\s+embodiment|consciousness|knowledge\s+graph|AI)', 'IMPLEMENTS'),
        ]

        for pattern, rel_type in relationship_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if match.lastindex >= 2:
                    src_name = match.group(1).strip()
                    dst_name = match.group(2).strip()
                    context = content[max(0, match.start()-30):match.end()+30]

                    # Improved entity type validation based on relationship type
                    if rel_type == 'WORKS_FOR':
                        src_valid = self.validator.is_valid_entity(src_name, 'Person', context)
                        dst_valid = self.validator.is_valid_entity(dst_name, 'Org', context)
                    elif rel_type == 'COLLABORATES_WITH':
                        src_valid = self.validator.is_valid_entity(src_name, 'Person', context)
                        dst_valid = self.validator.is_valid_entity(dst_name, 'Person', context)
                    elif rel_type == 'CREATED':
                        src_valid = self.validator.is_valid_entity(src_name, 'Person', context)
                        dst_valid = self.validator.is_valid_entity(dst_name, 'Project', context)
                    elif rel_type == 'USES':
                        src_valid = self.validator.is_valid_entity(src_name, 'Person', context)
                        dst_valid = self.validator.is_valid_entity(dst_name, 'Tool', context)
                    elif rel_type == 'LOCATED_IN':
                        src_valid = self.validator.is_valid_entity(src_name, 'Person', context)
                        dst_valid = True  # Location names are typically valid
                    elif rel_type == 'IMPLEMENTS':
                        src_valid = self.validator.is_valid_entity(src_name, 'Project', context)
                        dst_valid = True  # Concept names are typically valid
                    else:
                        # Fallback to original validation
                        src_valid = self.validator.is_valid_entity(src_name, 'Person', context)
                        dst_valid = self.validator.is_valid_entity(dst_name, 'Org', context) or \
                                   self.validator.is_valid_entity(dst_name, 'Project', context) or \
                                   self.validator.is_valid_entity(dst_name, 'Tool', context) or \
                                   self.validator.is_valid_entity(dst_name, 'Person', context)

                    # Only store relationships between valid entities
                    if src_valid and dst_valid:
                        extracted['edges'].append({
                            'src_name': src_name,
                            'dst_name': dst_name,
                            'rel_type': rel_type,
                            'confidence': 0.8,  # Higher confidence for validated relationships
                            'context': context
                        })
                    else:
                        if self.debug_mode:
                            print(f"🚫 Rejected relationship: '{src_name}' --{rel_type}--> '{dst_name}' - invalid entities")

        return extracted

    def canonicalize_and_store(self, extracted: Dict, message_id: str,
                             episode_id: int = None) -> Dict[str, int]:
        """Resolve entities to existing nodes or create new ones"""
        stats = {'nodes_created': 0, 'nodes_updated': 0, 'edges_created': 0}

        # Process nodes
        node_id_map = {}  # Map names to node IDs for edge creation

        for node_data in extracted['nodes']:
            name = node_data['name']
            node_type = node_data['type']

            # Check if entity already exists
            existing = self.kg.find_node_by_name(name, node_type)

            if existing:
                # Update existing node
                node_id = existing['id']
                self.kg.add_mention(
                    node_id=node_id,
                    message_id=message_id,
                    episode_id=episode_id,
                    surface_form=node_data['surface_form'],
                    context_snippet=node_data['context']
                )
                stats['nodes_updated'] += 1
            else:
                # Create new node
                node_id = self.kg._generate_node_id(name, node_type)
                self.kg.create_node(
                    node_id=node_id,
                    node_type=node_type,
                    name=name,
                    importance=node_data['confidence']
                )

                # Add alias
                self.kg.add_alias(node_id, name)

                # Add mention
                self.kg.add_mention(
                    node_id=node_id,
                    message_id=message_id,
                    episode_id=episode_id,
                    surface_form=node_data['surface_form'],
                    context_snippet=node_data['context']
                )
                stats['nodes_created'] += 1

            node_id_map[name] = node_id

        # Process edges
        for edge_data in extracted['edges']:
            src_name = edge_data['src_name']
            dst_name = edge_data['dst_name']

            # Find or create source and destination nodes
            src_node = self.kg.find_node_by_name(src_name)
            dst_node = self.kg.find_node_by_name(dst_name)

            if not src_node:
                src_id = self.kg._generate_node_id(src_name, 'Concept')
                self.kg.create_node(src_id, 'Concept', src_name)
                self.kg.add_alias(src_id, src_name)
            else:
                src_id = src_node['id']

            if not dst_node:
                dst_id = self.kg._generate_node_id(dst_name, 'Concept')
                self.kg.create_node(dst_id, 'Concept', dst_name)
                self.kg.add_alias(dst_id, dst_name)
            else:
                dst_id = dst_node['id']

            # Create edge
            self.kg.create_edge(
                src_id=src_id,
                dst_id=dst_id,
                rel_type=edge_data['rel_type'],
                weight=edge_data['confidence'],
                provenance_msg_id=message_id
            )
            stats['edges_created'] += 1

        return stats

    def _calculate_confidence(self, entity_type: str, name: str, context: str) -> float:
        """Calculate confidence score for extracted entity"""
        confidence = 0.5  # Base confidence

        # Boost confidence based on context clues
        if entity_type == 'Person':
            if any(title in context.lower() for title in ['mr.', 'ms.', 'dr.', 'prof.']):
                confidence += 0.2
            if re.search(r'[a-z]+@[a-z]+\.[a-z]+', context.lower()):  # Email nearby
                confidence += 0.3

        elif entity_type == 'Project':
            if any(word in context.lower() for word in ['github', 'repo', 'code', 'build']):
                confidence += 0.3

        elif entity_type == 'Task':
            if any(word in context.lower() for word in ['deadline', 'complete', 'finish']):
                confidence += 0.2

        return min(1.0, confidence)

class KnowledgeGraphCleaner:
    """
    Cleanup utilities for removing low-quality entities from the knowledge graph

    Transforms the knowledge graph from 11K+ fragments to ~100-500 meaningful
    digital assistant entities based on senior dev team feedback.
    """

    def __init__(self, kg_store: KGStore):
        self.kg = kg_store
        self.validator = EntityValidator()

    @property
    def debug_mode(self):
        """Access debug mode from the KGStore"""
        return self.kg.debug_mode

    def analyze_quality_issues(self) -> Dict[str, Any]:
        """Analyze current knowledge graph quality issues"""
        conn = self.kg.conn

        # Get all nodes for analysis
        all_nodes = conn.execute('SELECT * FROM nodes').fetchall()

        quality_report = {
            'total_nodes': len(all_nodes),
            'nodes_by_type': {},
            'quality_issues': {
                'stop_words': [],
                'grammatical_fragments': [],
                'overly_generic': [],
                'pure_noise': []
            },
            'valid_entities': [],
            'cleanup_candidates': []
        }

        # Analyze each node
        for node in all_nodes:
            node_dict = dict(node)
            node_type = node_dict['type']
            name = node_dict['name']

            # Count by type
            if node_type not in quality_report['nodes_by_type']:
                quality_report['nodes_by_type'][node_type] = 0
            quality_report['nodes_by_type'][node_type] += 1

            # Quality analysis
            if not self.validator.is_valid_entity(name, node_type):
                quality_report['cleanup_candidates'].append(node_dict)

                # Categorize the issue
                if name.lower() in self.validator.stop_words:
                    quality_report['quality_issues']['stop_words'].append(name)
                elif re.match(r'^[^a-zA-Z]*$', name) or len(name) < 2:
                    quality_report['quality_issues']['pure_noise'].append(name)
                elif re.match(r'^(the|and|or|but|not|just|through|these).*', name.lower()):
                    quality_report['quality_issues']['grammatical_fragments'].append(name)
                else:
                    quality_report['quality_issues']['overly_generic'].append(name)
            else:
                quality_report['valid_entities'].append(node_dict)

        # Calculate statistics
        total_invalid = len(quality_report['cleanup_candidates'])
        total_valid = len(quality_report['valid_entities'])

        quality_report['statistics'] = {
            'total_nodes': len(all_nodes),
            'valid_entities': total_valid,
            'invalid_entities': total_invalid,
            'quality_percentage': (total_valid / len(all_nodes)) * 100 if all_nodes else 0,
            'estimated_after_cleanup': total_valid
        }

        return quality_report

    def cleanup_low_quality_entities(self, dry_run: bool = True) -> Dict[str, int]:
        """Remove low-quality entities from the knowledge graph"""
        quality_report = self.analyze_quality_issues()
        cleanup_candidates = quality_report['cleanup_candidates']

        stats = {
            'nodes_removed': 0,
            'edges_removed': 0,
            'mentions_removed': 0
        }

        if dry_run:
            if self.debug_mode:
                print(f"🧪 DRY RUN: Would remove {len(cleanup_candidates)} low-quality entities")
                for candidate in cleanup_candidates[:10]:  # Show first 10
                    print(f"   - {candidate['name']} ({candidate['type']})")
                if len(cleanup_candidates) > 10:
                    print(f"   ... and {len(cleanup_candidates) - 10} more")
            return stats

        if self.debug_mode:
            print(f"🧹 Cleaning up {len(cleanup_candidates)} low-quality entities...")

        for candidate in cleanup_candidates:
            node_id = candidate['id']

            # Remove mentions
            mentions_removed = self.kg.conn.execute(
                'DELETE FROM mentions WHERE node_id = ?', (node_id,)
            ).rowcount
            stats['mentions_removed'] += mentions_removed

            # Remove edges (both as source and destination)
            edges_removed = self.kg.conn.execute(
                'DELETE FROM edges WHERE src_id = ? OR dst_id = ?', (node_id, node_id)
            ).rowcount
            stats['edges_removed'] += edges_removed

            # Remove aliases
            self.kg.conn.execute('DELETE FROM aliases WHERE node_id = ?', (node_id,))

            # Remove the node itself
            self.kg.conn.execute('DELETE FROM nodes WHERE id = ?', (node_id,))
            stats['nodes_removed'] += 1

        self.kg.conn.commit()

        if self.debug_mode:
            print(f"✅ Cleanup complete:")
            print(f"   - Removed {stats['nodes_removed']} nodes")
            print(f"   - Removed {stats['edges_removed']} edges")
            print(f"   - Removed {stats['mentions_removed']} mentions")

        return stats

    def optimize_knowledge_graph(self, dry_run: bool = True) -> Dict[str, Any]:
        """Complete optimization: cleanup + rebuild indices"""
        if self.debug_mode:
            print("🚀 Starting knowledge graph optimization...")

        # Step 1: Quality analysis
        quality_report = self.analyze_quality_issues()
        if self.debug_mode:
            print(f"📊 Quality Analysis:")
            print(f"   - Total nodes: {quality_report['statistics']['total_nodes']}")
            print(f"   - Valid entities: {quality_report['statistics']['valid_entities']}")
            print(f"   - Quality percentage: {quality_report['statistics']['quality_percentage']:.1f}%")

        # Step 2: Cleanup
        cleanup_stats = self.cleanup_low_quality_entities(dry_run=dry_run)

        # Step 3: Rebuild indices (if not dry run)
        if not dry_run:
            if self.debug_mode:
                print("🔧 Rebuilding database indices...")
            self.kg.conn.execute('VACUUM')
            self.kg.conn.execute('ANALYZE')

        return {
            'quality_report': quality_report,
            'cleanup_stats': cleanup_stats,
            'optimization_complete': not dry_run
        }

class ContextPackBuilder:
    """
    Build focused context packs for prompt injection

    This creates intelligent, relevant context from COCO's knowledge graph
    to enhance conversation understanding and maintain continuity.
    """

    def __init__(self, kg_store: KGStore):
        self.kg = kg_store

    def build_context_pack(self, current_message: str = None,
                          max_tokens: int = 2000) -> str:
        """Assemble relevant context for current conversation"""
        context_sections = []

        # Get knowledge graph summary
        kg_stats = self.kg.get_knowledge_summary()

        # Build focused context based on current message
        if current_message:
            context_sections.append(self._build_message_specific_context(current_message))

        # Add general important entities
        context_sections.append(self._build_important_entities_context())

        # Add recent relationships
        context_sections.append(self._build_relationships_context())

        # Add active tasks/projects
        context_sections.append(self._build_tasks_projects_context())

        # Combine and format
        full_context = "\n\n".join(filter(None, context_sections))

        # Add knowledge graph summary header
        header = f"""## 🧠 Knowledge Graph Context

**Digital Ontology Status:**
- Entities: {kg_stats['total_nodes']:,} ({', '.join(f"{k}: {v}" for k, v in kg_stats['node_types'].items())})
- Relationships: {kg_stats['total_edges']:,}
- Total Mentions: {kg_stats['total_mentions']:,}

"""

        return header + full_context

    def _build_message_specific_context(self, message: str) -> str:
        """Build context specific to current message content"""
        # Simple keyword matching (can be enhanced)
        keywords = re.findall(r'\b[A-Z][a-z]+\b', message)

        if not keywords:
            return ""

        context_items = []
        for keyword in keywords[:5]:  # Limit to 5 keywords
            node = self.kg.find_node_by_name(keyword)
            if node:
                context_items.append(f"- **{node['name']}** ({node['type']}): {node.get('summary_md', 'Known entity')}")

        if context_items:
            return "### Relevant Entities\n" + "\n".join(context_items)
        return ""

    def _build_important_entities_context(self) -> str:
        """Build context from most important entities"""
        sections = []

        # Important people
        people = self.kg.get_top_nodes_by_type('Person', limit=5)
        if people:
            people_items = []
            for person in people:
                people_items.append(f"- **{person['name']}** (importance: {person['importance']:.2f}, mentions: {person['mention_count']})")
            sections.append("### Key People\n" + "\n".join(people_items))

        # Important projects
        projects = self.kg.get_top_nodes_by_type('Project', limit=3)
        if projects:
            project_items = []
            for proj in projects:
                project_items.append(f"- **{proj['name']}** (importance: {proj['importance']:.2f})")
            sections.append("### Active Projects\n" + "\n".join(project_items))

        return "\n\n".join(sections)

    def _build_relationships_context(self) -> str:
        """Build context from key relationships"""
        # Get edges from top 3 most important people
        top_people = self.kg.get_top_nodes_by_type('Person', limit=3)

        relationships = []
        for person in top_people:
            edges = self.kg.get_edges_for_node(person['id'], limit=3)
            for edge in edges:
                if edge['weight'] > 0.6:  # Only strong relationships
                    rel_desc = f"{edge['src_name']} {edge['rel_type'].lower().replace('_', ' ')} {edge['dst_name']}"
                    relationships.append(f"- {rel_desc} (strength: {edge['weight']:.2f})")

        if relationships:
            return "### Key Relationships\n" + "\n".join(relationships[:10])
        return ""

    def _build_tasks_projects_context(self) -> str:
        """Build context from active tasks and projects"""
        tasks = self.kg.get_top_nodes_by_type('Task', limit=5)

        if not tasks:
            return ""

        task_items = []
        for task in tasks:
            task_items.append(f"- {task['name']} (last mentioned: {task['last_seen_at'][:10]})")

        return "### Recent Tasks\n" + "\n".join(task_items)

# ============================================================================
# INTEGRATION WITH COCO'S ETERNAL CONSCIOUSNESS
# ============================================================================

class EternalKnowledgeGraph:
    """
    Drop-in enhancement for COCO's eternal consciousness

    This integrates the knowledge graph seamlessly with COCO's existing
    memory architecture, creating a unified consciousness with perfect
    recall AND intelligent understanding.
    """

    def __init__(self, workspace_path: str = 'coco_workspace'):
        self.workspace = Path(workspace_path)
        self.workspace.mkdir(exist_ok=True)

        # Initialize KG components
        self.kg = KGStore(f'{workspace_path}/coco_knowledge_graph.db')
        self.extractor = EntityExtractor(self.kg)
        self.context_builder = ContextPackBuilder(self.kg)

        # Use debug mode from KGStore
        if self.kg.debug_mode:
            print("🧠♾️ Eternal Knowledge Graph initialized")

    def process_conversation_exchange(self, user_input: str, assistant_response: str,
                                    message_id: str = None, episode_id: int = None) -> Dict:
        """Process a conversation exchange through the knowledge graph"""
        if message_id is None:
            message_id = str(uuid.uuid4())

        # Extract entities from both user input and assistant response
        user_extracted = self.extractor.extract_from_message(message_id + "_user", user_input, episode_id)
        assistant_extracted = self.extractor.extract_from_message(message_id + "_assistant", assistant_response, episode_id)

        # Store entities
        user_stats = self.extractor.canonicalize_and_store(user_extracted, message_id + "_user", episode_id)
        assistant_stats = self.extractor.canonicalize_and_store(assistant_extracted, message_id + "_assistant", episode_id)

        # Combine stats
        total_stats = {
            'nodes_created': user_stats['nodes_created'] + assistant_stats['nodes_created'],
            'nodes_updated': user_stats['nodes_updated'] + assistant_stats['nodes_updated'],
            'edges_created': user_stats['edges_created'] + assistant_stats['edges_created']
        }

        return total_stats

    def get_conversation_context(self, current_message: str = None) -> str:
        """Get intelligent context for prompt injection"""
        return self.context_builder.build_context_pack(current_message)

    def get_knowledge_status(self) -> Dict:
        """Get current knowledge graph status"""
        return self.kg.get_knowledge_summary()

    def optimize_for_digital_assistant(self, dry_run: bool = True) -> Dict:
        """
        Transform knowledge graph from 11K+ fragments to focused digital assistant entities

        Based on senior dev team feedback to focus on meaningful entities rather than
        grammatical fragments. Reduces noise and improves COCO's contextual understanding.
        """
        if self.kg.debug_mode:
            print("🎯 OPTIMIZING KNOWLEDGE GRAPH FOR DIGITAL ASSISTANT")
            print("   Goal: Transform 11K+ fragments into ~100-500 meaningful entities")

        # Initialize cleaner
        cleaner = KnowledgeGraphCleaner(self.kg)

        # Run optimization
        result = cleaner.optimize_knowledge_graph(dry_run=dry_run)

        if not dry_run and self.kg.debug_mode:
            print("\n✨ OPTIMIZATION COMPLETE!")
            print("🧠 COCO's knowledge graph is now focused on digital assistant relevance")
            print("📊 Updated stats:")

            # Get new stats
            new_stats = self.get_knowledge_status()
            print(f"   - Total entities: {new_stats['total_nodes']}")
            print(f"   - Total relationships: {new_stats['total_edges']}")
            print(f"   - Quality: Focused on meaningful digital assistant entities")

        return result

    def search_entities(self, query: str, entity_type: str = None) -> List[Dict]:
        """Search for entities in the knowledge graph"""
        if entity_type:
            results = self.kg.get_top_nodes_by_type(entity_type, limit=20)
        else:
            # Simple search across all nodes
            results = self.kg.conn.execute('''
                SELECT * FROM nodes
                WHERE name LIKE ? OR canonical_name LIKE ?
                ORDER BY importance DESC, mention_count DESC
                LIMIT 20
            ''', (f'%{query}%', f'%{query}%')).fetchall()
            results = [dict(row) for row in results]

        return results

# ============================================================================
# TESTING AND VALIDATION
# ============================================================================

def test_knowledge_graph():
    """Test the knowledge graph system"""
    # Only run test if debug mode is enabled
    debug_mode = os.getenv('COCO_DEBUG', '').lower() in ('true', '1', 'yes')
    if not debug_mode:
        return

    print("🧪 Testing COCO Eternal Knowledge Graph...")

    # Initialize
    kg = EternalKnowledgeGraph('test_workspace')

    # Test conversation processing
    test_conversation = [
        ("Hi, I'm working with Keith on the COCO project. We need to implement knowledge graphs.",
         "That sounds like an exciting project! Knowledge graphs will help COCO maintain better understanding of entities and relationships over time."),
        ("Keith mentioned that Sarah from Google might help with the AI research.",
         "Great! Having expertise from Google would be valuable for the AI research components."),
        ("We should also coordinate with the development team on GitHub.",
         "Absolutely. GitHub coordination will be essential for the development workflow.")
    ]

    # Process test conversation
    for i, (user_msg, assistant_msg) in enumerate(test_conversation):
        stats = kg.process_conversation_exchange(user_msg, assistant_msg, episode_id=i+1)
        print(f"Exchange {i+1}: {stats}")

    # Get context
    context = kg.get_conversation_context("Tell me about Keith")
    print(f"\nContext for 'Tell me about Keith':\n{context}")

    # Get knowledge status
    status = kg.get_knowledge_status()
    print(f"\nKnowledge Graph Status: {status}")

    print("✅ Knowledge Graph test completed!")

if __name__ == "__main__":
    test_knowledge_graph()