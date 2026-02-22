#!/usr/bin/env python3
"""
COCO Simplified Knowledge Graph - Relationship-First Approach
============================================================

Focus on meaningful relationships between key entities rather than
exhaustive entity extraction. Quality over quantity for consciousness.
"""

import sqlite3
import json
import uuid
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class SimplifiedKnowledgeGraph:
    """
    Streamlined knowledge graph focused on relationships, not entity hoarding

    Philosophy: Better to know 10 things well-connected than 6000 things isolated
    """

    def __init__(self, db_path: str = 'coco_workspace/coco_knowledge_graph.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.debug_mode = os.getenv('COCO_DEBUG', '').lower() in ('true', '1', 'yes')

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

        # Focus on key relationship patterns for consciousness
        self.relationship_patterns = {
            # Person relationships (who knows who)
            'COLLABORATES_WITH': [
                r'(\w+)\s+and\s+(\w+)\s+(?:work|collaborate|partner)',
                r'(\w+)\s+(?:works with|collaborates with|partners with)\s+(\w+)',
                r'me and (\w+)',  # User relationships
                r'(\w+) and I',   # User relationships
            ],

            # Project ownership (who built what)
            'CREATED': [
                r'(\w+)\s+(?:created|built|developed|designed)\s+(\w+)',
                r'(\w+)\s+is\s+the\s+(?:creator|developer|architect)\s+of\s+(\w+)',
                r'I (?:created|built|made)\s+(\w+)',  # User creations
            ],

            # Technology usage (who uses what)
            'USES': [
                r'(\w+)\s+(?:uses|prefers|works with)\s+(\w+)',
                r'I (?:use|prefer|work with)\s+(\w+)',  # User preferences
            ],

            # Knowledge relationships (who knows what)
            'KNOWS_ABOUT': [
                r'(\w+)\s+(?:knows|understands|is expert in)\s+(\w+)',
                r'ask (\w+) about (\w+)',
                r'(\w+) told me about (\w+)',
            ],

            # Context relationships (what relates to what)
            'RELATES_TO': [
                r'(\w+)\s+(?:relates to|is part of|involves)\s+(\w+)',
                r'(\w+)\s+and\s+(\w+)\s+are (?:related|connected)',
            ]
        }

        # Key entity types - minimal but meaningful
        self.entity_types = {
            'Person': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',  # Names only
            'Project': r'\b(?:COCO|[A-Z]{2,})\b',  # Acronyms/systems
            'Technology': r'\b(?:Python|JavaScript|Claude|SQLite|Git|AI|ML)\b',  # Tools
            'Concept': r'\b(?:memory|consciousness|knowledge|intelligence)\b'  # Key concepts
        }

    def init_schema(self):
        """Minimal schema focused on relationships"""
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
            last_seen TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            src_id TEXT NOT NULL,
            dst_id TEXT NOT NULL,
            rel_type TEXT NOT NULL,
            strength REAL DEFAULT 0.5,
            context TEXT,
            first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
            last_seen TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(src_id) REFERENCES entities(id),
            FOREIGN KEY(dst_id) REFERENCES entities(id),
            UNIQUE(src_id, dst_id, rel_type)
        );

        CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
        CREATE INDEX IF NOT EXISTS idx_relationships_src ON relationships(src_id);
        CREATE INDEX IF NOT EXISTS idx_relationships_dst ON relationships(dst_id);
        ''')

    def process_conversation_exchange(self, user_input: str, assistant_response: str) -> Dict:
        """Focus on extracting meaningful relationships from conversation"""
        stats = {'entities_added': 0, 'relationships_added': 0}

        # Combine input and response for full context
        full_content = f"{user_input} {assistant_response}"

        # Extract relationships first (relationship-driven approach)
        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, full_content, re.IGNORECASE)

                for match in matches:
                    if match.lastindex >= 2:
                        src_name = match.group(1).strip()
                        dst_name = match.group(2).strip()
                        context = full_content[max(0, match.start()-50):match.end()+50]

                        # Clean and validate names
                        src_name = self._clean_entity_name(src_name)
                        dst_name = self._clean_entity_name(dst_name)

                        if self._is_valid_entity_pair(src_name, dst_name):
                            # Ensure entities exist
                            src_id = self._ensure_entity(src_name, rel_type)
                            dst_id = self._ensure_entity(dst_name, rel_type)

                            if src_id and dst_id:
                                # Add/update relationship
                                if self._add_relationship(src_id, dst_id, rel_type, context):
                                    stats['relationships_added'] += 1

                                    if self.debug_mode:
                                        print(f"✅ Added: {src_name} --{rel_type}--> {dst_name}")

        return stats

    def _clean_entity_name(self, name: str) -> str:
        """Clean and normalize entity names"""
        # Remove common noise words
        noise_words = {'the', 'and', 'or', 'but', 'with', 'from', 'to', 'for', 'of', 'in', 'on', 'at'}

        # Basic cleaning
        name = re.sub(r'[^\w\s]', '', name).strip()
        words = [w for w in name.split() if w.lower() not in noise_words]

        return ' '.join(words) if words else name

    def _is_valid_entity_pair(self, src: str, dst: str) -> bool:
        """Quick validation for entity pairs"""
        if not src or not dst or len(src) < 2 or len(dst) < 2:
            return False

        # Avoid self-relationships
        if src.lower() == dst.lower():
            return False

        # Avoid too-common words
        common_words = {'this', 'that', 'they', 'them', 'it', 'what', 'when', 'where', 'how'}
        if src.lower() in common_words or dst.lower() in common_words:
            return False

        return True

    def _ensure_entity(self, name: str, context_rel_type: str) -> Optional[str]:
        """Ensure entity exists, create if needed"""
        # Try to find existing entity
        result = self.conn.execute('SELECT id FROM entities WHERE name = ?', (name,)).fetchone()
        if result:
            return result['id']

        # Determine entity type from name and context
        entity_type = self._infer_entity_type(name, context_rel_type)
        if not entity_type:
            return None

        # Create new entity
        entity_id = str(uuid.uuid4())[:8]
        self.conn.execute('''
            INSERT INTO entities (id, name, type) VALUES (?, ?, ?)
        ''', (entity_id, name, entity_type))
        self.conn.commit()

        return entity_id

    def _infer_entity_type(self, name: str, context_rel_type: str) -> Optional[str]:
        """Infer entity type from name patterns and relationship context"""
        # Use relationship context for better typing
        if context_rel_type in ['COLLABORATES_WITH', 'KNOWS_ABOUT']:
            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?$', name):
                return 'Person'

        if context_rel_type in ['CREATED', 'USES']:
            if name.isupper() or name in ['COCO', 'Python', 'JavaScript', 'Claude']:
                return 'Technology' if name in ['Python', 'JavaScript', 'Claude', 'SQLite'] else 'Project'

        # Pattern-based fallback
        for entity_type, pattern in self.entity_types.items():
            if re.match(pattern, name, re.IGNORECASE):
                return entity_type

        return 'Concept'  # Default fallback

    def _add_relationship(self, src_id: str, dst_id: str, rel_type: str, context: str) -> bool:
        """Add or strengthen relationship"""
        try:
            # Try to update existing relationship
            result = self.conn.execute('''
                UPDATE relationships
                SET strength = strength + 0.1, last_seen = CURRENT_TIMESTAMP, context = ?
                WHERE src_id = ? AND dst_id = ? AND rel_type = ?
            ''', (context, src_id, dst_id, rel_type))

            if result.rowcount == 0:
                # Create new relationship
                rel_id = str(uuid.uuid4())[:8]
                self.conn.execute('''
                    INSERT INTO relationships (id, src_id, dst_id, rel_type, context)
                    VALUES (?, ?, ?, ?, ?)
                ''', (rel_id, src_id, dst_id, rel_type, context))

            self.conn.commit()
            return True

        except sqlite3.Error as e:
            if self.debug_mode:
                print(f"❌ Relationship error: {e}")
            return False

    def get_knowledge_status(self) -> Dict:
        """Get simplified knowledge graph status"""
        entity_count = self.conn.execute('SELECT COUNT(*) FROM entities').fetchone()[0]
        rel_count = self.conn.execute('SELECT COUNT(*) FROM relationships').fetchone()[0]

        # Get relationship types
        rel_types = self.conn.execute('''
            SELECT rel_type, COUNT(*) as count
            FROM relationships
            GROUP BY rel_type
            ORDER BY count DESC
        ''').fetchall()

        # Get most connected entities
        connected = self.conn.execute('''
            SELECT e.name, e.type, COUNT(r.id) as connections
            FROM entities e
            JOIN relationships r ON (e.id = r.src_id OR e.id = r.dst_id)
            GROUP BY e.id
            ORDER BY connections DESC
            LIMIT 10
        ''').fetchall()

        return {
            'total_entities': entity_count,
            'total_relationships': rel_count,
            'relationship_types': dict(rel_types),
            'most_connected': [dict(row) for row in connected]
        }

    def get_entity_relationships(self, entity_name: str) -> List[Dict]:
        """Get all relationships for an entity"""
        results = self.conn.execute('''
            SELECT
                r.rel_type,
                CASE
                    WHEN e1.name = ? THEN e2.name
                    ELSE e1.name
                END as related_entity,
                CASE
                    WHEN e1.name = ? THEN 'outgoing'
                    ELSE 'incoming'
                END as direction,
                r.strength,
                r.context
            FROM relationships r
            JOIN entities e1 ON r.src_id = e1.id
            JOIN entities e2 ON r.dst_id = e2.id
            WHERE e1.name = ? OR e2.name = ?
            ORDER BY r.strength DESC
        ''', (entity_name, entity_name, entity_name, entity_name)).fetchall()

        return [dict(row) for row in results]

def test_simplified_kg():
    """Test the simplified knowledge graph"""
    print("🧪 Testing Simplified Knowledge Graph...")

    kg = SimplifiedKnowledgeGraph('coco_workspace/test_simplified_kg.db')

    # Test conversations with clear relationships
    test_exchanges = [
        ("I work with Sarah on the COCO project", "That's great collaboration!"),
        ("Keith created COCO using Python", "Impressive technical achievement!"),
        ("Sarah knows about machine learning", "She could help with ML features"),
        ("COCO implements digital consciousness", "Revolutionary approach to AI"),
        ("I use Claude for development", "Claude is excellent for coding")
    ]

    for user_input, assistant_response in test_exchanges:
        stats = kg.process_conversation_exchange(user_input, assistant_response)
        print(f"Exchange processed: {stats}")

    # Check results
    status = kg.get_knowledge_status()
    print(f"\nFinal Status: {status}")

    # Show entity relationships
    for entity in ['Sarah', 'Keith', 'COCO']:
        rels = kg.get_entity_relationships(entity)
        if rels:
            print(f"\n{entity} relationships:")
            for rel in rels:
                print(f"  {rel['direction']}: {rel['rel_type']} -> {rel['related_entity']}")

if __name__ == "__main__":
    test_simplified_kg()