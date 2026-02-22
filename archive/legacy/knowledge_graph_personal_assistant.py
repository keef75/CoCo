#!/usr/bin/env python3
"""
COCO Personal Assistant Knowledge Graph
======================================

Focused on what a personal assistant actually needs to remember:
- People in your life and their roles
- Places you go/work/live
- Tasks you've completed or need to do
- Tools/systems you use regularly
- Basic preferences and patterns

Simple, practical, useful.
"""

import sqlite3
import json
import uuid
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class PersonalAssistantKG:
    """
    Knowledge graph designed for personal assistant functionality

    Remembers what matters: who, what, where, when, how
    """

    def __init__(self, db_path: str = 'coco_workspace/coco_personal_kg.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.debug_mode = os.getenv('COCO_DEBUG', '').lower() in ('true', '1', 'yes')

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

        # Core entity types for personal assistant
        self.entity_patterns = {
            # People - names, roles, relationships
            'PERSON': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',  # First Last names
                r'my (?:wife|husband|partner|friend|colleague|boss|assistant)\s+([A-Z][a-z]+)',
                r'(?:Dr\.|Mr\.|Mrs\.|Ms\.)\s+([A-Z][a-z]+)',
            ],

            # Places - work, home, locations
            'PLACE': [
                r'\b(?:at|in|to|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Location names
                r'office in ([A-Z][a-z\s]+)',
                r'(?:live|work|based)\s+in\s+([A-Z][a-z\s,]+)',
                r'meeting at ([A-Z][a-z\s]+)',
            ],

            # Things - tools, systems, objects
            'TOOL': [
                r'\b(Python|JavaScript|Claude|COCO|SQLite|Git|Docker|VSCode|Gmail|Slack|Zoom)\b',
                r'using ([A-Z][a-z]+)',
                r'(?:tool|system|platform|app)\s+([A-Z][a-z]+)',
            ],

            # Tasks - completed or planned actions
            'TASK': [
                r'(?:completed|finished|done)\s+([a-z][a-z\s]+)',
                r'need to ([a-z][a-z\s]+)',
                r'todo:?\s*([a-z][a-z\s]+)',
                r'working on ([a-z][a-z\s]+)',
            ],

            # Projects - ongoing work
            'PROJECT': [
                r'\b([A-Z]{2,})\b',  # Acronyms
                r'(?:project|repo|system)\s+([A-Za-z-_]+)',
                r'building ([A-Za-z\s]+)',
            ],

            # Preferences - likes, dislikes, patterns
            'PREFERENCE': [
                r'I (?:like|love|prefer|hate|dislike)\s+([a-z][a-z\s]+)',
                r'my favorite ([a-z][a-z\s]+)',
                r'I usually ([a-z][a-z\s]+)',
                r'I always ([a-z][a-z\s]+)',
            ]
        }

        # Relationship patterns that matter for personal assistant
        self.relationship_patterns = {
            # Who is who to the user
            'KNOWS': [
                r'(?:my|I know)\s+([A-Z][a-z]+)',
                r'([A-Z][a-z]+)\s+(?:is my|works with me)',
            ],

            # Family/personal relationships
            'FAMILY': [
                r'my (?:wife|husband|partner|spouse)\s+([A-Z][a-z]+)',
                r'([A-Z][a-z]+)\s+is my (?:wife|husband|partner)',
            ],

            # Work relationships
            'WORKS_WITH': [
                r'I work with ([A-Z][a-z]+)',
                r'([A-Z][a-z]+)\s+(?:and I|and me)\s+work',
                r'colleague ([A-Z][a-z]+)',
            ],

            # Tool usage
            'USES': [
                r'I use ([A-Z][a-z]+)',
                r'prefer ([A-Z][a-z]+)',
                r'working with ([A-Z][a-z]+)',
            ],

            # Task completion
            'COMPLETED': [
                r'I (?:completed|finished|done)\s+([a-z][a-z\s]+)',
                r'finished (?:the |)([a-z][a-z\s]+)',
            ],

            # Location associations
            'LOCATED_AT': [
                r'I (?:work|live|am)\s+(?:at|in)\s+([A-Z][a-z\s]+)',
                r'office (?:at|in)\s+([A-Z][a-z\s]+)',
            ],

            # Project involvement
            'WORKING_ON': [
                r'I(?:\'m| am) working on ([A-Za-z\s]+)',
                r'building ([A-Za-z\s]+)',
                r'project ([A-Za-z\s]+)',
            ]
        }

    def init_schema(self):
        """Simple schema for personal assistant knowledge"""
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            type TEXT CHECK(type IN ('PERSON','PLACE','TOOL','TASK','PROJECT','PREFERENCE')),
            description TEXT,
            importance REAL DEFAULT 0.5,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_mentioned TEXT DEFAULT CURRENT_TIMESTAMP,
            mention_count INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            user_entity TEXT NOT NULL,  -- Always relates to user or user's context
            related_entity TEXT NOT NULL,
            relationship_type TEXT NOT NULL, -- KNOWS, FAMILY, WORKS_WITH, USES, etc.
            details TEXT,
            strength REAL DEFAULT 1.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_confirmed TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(related_entity) REFERENCES entities(id),
            UNIQUE(user_entity, related_entity, relationship_type)
        );

        -- Track what tools were actually called (for learning user patterns)
        CREATE TABLE IF NOT EXISTS tool_usage (
            id TEXT PRIMARY KEY,
            tool_name TEXT NOT NULL,
            context TEXT,
            successful BOOLEAN DEFAULT TRUE,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
        CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
        ''')

    def process_conversation_exchange(self, user_input: str, assistant_response: str,
                                    tools_used: List[str] = None) -> Dict:
        """Process conversation focusing on personal assistant knowledge"""
        stats = {'entities_added': 0, 'relationships_added': 0, 'tools_recorded': 0}

        # Record tool usage (important for learning user patterns)
        if tools_used:
            for tool in tools_used:
                self._record_tool_usage(tool, user_input)
                stats['tools_recorded'] += 1

        # Extract entities from user input (what they care about)
        user_entities = self._extract_entities(user_input)

        # Focus on user-centric relationships
        relationships = self._extract_relationships(user_input)

        # Store entities
        for entity in user_entities:
            if self._add_entity(entity):
                stats['entities_added'] += 1

        # Store relationships (always user-centric)
        for rel in relationships:
            if self._add_relationship(rel):
                stats['relationships_added'] += 1

        return stats

    def _extract_entities(self, text: str) -> List[Dict]:
        """Extract entities relevant to personal assistant"""
        entities = []

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    name = match.group(1).strip()

                    # Clean and validate
                    name = self._clean_name(name)
                    if self._is_valid_entity(name, entity_type):
                        entities.append({
                            'name': name,
                            'type': entity_type,
                            'context': text[max(0, match.start()-30):match.end()+30]
                        })

        return entities

    def _extract_relationships(self, text: str) -> List[Dict]:
        """Extract user-centric relationships"""
        relationships = []

        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if match.lastindex >= 1:
                        entity_name = match.group(1).strip()
                        entity_name = self._clean_name(entity_name)

                        if self._is_valid_entity(entity_name, None):
                            relationships.append({
                                'user_entity': 'USER',  # Always user-centric
                                'related_entity': entity_name,
                                'relationship_type': rel_type,
                                'context': text[max(0, match.start()-30):match.end()+30]
                            })

        return relationships

    def _clean_name(self, name: str) -> str:
        """Clean entity names"""
        # Remove articles and common noise
        name = re.sub(r'\b(?:the|a|an)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[^\w\s]', '', name).strip()
        return ' '.join(name.split())  # Normalize whitespace

    def _is_valid_entity(self, name: str, entity_type: str) -> bool:
        """Quick validation"""
        if not name or len(name) < 2:
            return False

        # Skip overly common words
        skip_words = {'this', 'that', 'they', 'them', 'it', 'me', 'you', 'we', 'us', 'him', 'her'}
        if name.lower() in skip_words:
            return False

        return True

    def _add_entity(self, entity: Dict) -> bool:
        """Add or update entity"""
        try:
            # Check if exists
            existing = self.conn.execute(
                'SELECT id FROM entities WHERE name = ?', (entity['name'],)
            ).fetchone()

            if existing:
                # Update last mentioned
                self.conn.execute('''
                    UPDATE entities
                    SET last_mentioned = CURRENT_TIMESTAMP, mention_count = mention_count + 1
                    WHERE name = ?
                ''', (entity['name'],))
                return False
            else:
                # Create new
                entity_id = str(uuid.uuid4())[:8]
                self.conn.execute('''
                    INSERT INTO entities (id, name, type, description)
                    VALUES (?, ?, ?, ?)
                ''', (entity_id, entity['name'], entity['type'], entity.get('context', '')))
                self.conn.commit()
                return True

        except sqlite3.Error as e:
            if self.debug_mode:
                print(f"❌ Entity error: {e}")
            return False

    def _add_relationship(self, rel: Dict) -> bool:
        """Add or strengthen relationship"""
        try:
            # Ensure related entity exists
            entity_id = self.conn.execute(
                'SELECT id FROM entities WHERE name = ?', (rel['related_entity'],)
            ).fetchone()

            if not entity_id:
                # Create the entity first
                entity_id = str(uuid.uuid4())[:8]
                self.conn.execute('''
                    INSERT INTO entities (id, name, type)
                    VALUES (?, ?, ?)
                ''', (entity_id, rel['related_entity'], 'PERSON'))  # Default to person

            # Add/update relationship
            result = self.conn.execute('''
                UPDATE relationships
                SET strength = strength + 0.1, last_confirmed = CURRENT_TIMESTAMP
                WHERE user_entity = ? AND related_entity = ? AND relationship_type = ?
            ''', (rel['user_entity'], rel['related_entity'], rel['relationship_type']))

            if result.rowcount == 0:
                # Create new relationship
                rel_id = str(uuid.uuid4())[:8]
                self.conn.execute('''
                    INSERT INTO relationships (id, user_entity, related_entity, relationship_type, details)
                    VALUES (?, ?, ?, ?, ?)
                ''', (rel_id, rel['user_entity'], rel['related_entity'],
                      rel['relationship_type'], rel.get('context', '')))

            self.conn.commit()
            return True

        except sqlite3.Error as e:
            if self.debug_mode:
                print(f"❌ Relationship error: {e}")
            return False

    def _record_tool_usage(self, tool_name: str, context: str):
        """Record tool usage for pattern learning"""
        try:
            usage_id = str(uuid.uuid4())[:8]
            self.conn.execute('''
                INSERT INTO tool_usage (id, tool_name, context)
                VALUES (?, ?, ?)
            ''', (usage_id, tool_name, context[:200]))  # Limit context
            self.conn.commit()
        except sqlite3.Error:
            pass  # Non-critical

    def get_user_knowledge(self) -> Dict:
        """Get knowledge about the user's world"""
        # People the user knows
        people = self.conn.execute('''
            SELECT e.name, r.relationship_type, r.strength
            FROM entities e
            JOIN relationships r ON e.name = r.related_entity
            WHERE e.type = 'PERSON' AND r.user_entity = 'USER'
            ORDER BY r.strength DESC, e.mention_count DESC
        ''').fetchall()

        # Tools the user uses
        tools = self.conn.execute('''
            SELECT tool_name, COUNT(*) as usage_count
            FROM tool_usage
            GROUP BY tool_name
            ORDER BY usage_count DESC
            LIMIT 10
        ''').fetchall()

        # Recent tasks/projects
        tasks = self.conn.execute('''
            SELECT name, type, mention_count
            FROM entities
            WHERE type IN ('TASK', 'PROJECT')
            ORDER BY last_mentioned DESC
            LIMIT 10
        ''').fetchall()

        return {
            'people': [dict(row) for row in people],
            'preferred_tools': [dict(row) for row in tools],
            'recent_tasks': [dict(row) for row in tasks]
        }

    def get_context_for_query(self, query: str) -> str:
        """Get relevant context for a user query"""
        context_parts = []

        # Find relevant people
        query_lower = query.lower()
        people = self.conn.execute('''
            SELECT e.name, r.relationship_type
            FROM entities e
            JOIN relationships r ON e.name = r.related_entity
            WHERE e.type = 'PERSON' AND r.user_entity = 'USER'
            AND LOWER(e.name) LIKE ?
        ''', (f'%{query_lower}%',)).fetchall()

        if people:
            context_parts.append("People you know:")
            for person in people:
                context_parts.append(f"- {person['name']} ({person['relationship_type']})")

        # Find relevant tools/preferences
        tools = self.conn.execute('''
            SELECT tool_name, COUNT(*) as usage
            FROM tool_usage
            WHERE LOWER(tool_name) LIKE ? OR LOWER(context) LIKE ?
            GROUP BY tool_name
            ORDER BY usage DESC
            LIMIT 3
        ''', (f'%{query_lower}%', f'%{query_lower}%')).fetchall()

        if tools:
            context_parts.append("\nTools you use:")
            for tool in tools:
                context_parts.append(f"- {tool['tool_name']} ({tool['usage']} times)")

        return '\n'.join(context_parts) if context_parts else ""

def test_personal_assistant_kg():
    """Test personal assistant knowledge graph"""
    print("🧪 Testing Personal Assistant Knowledge Graph...")

    kg = PersonalAssistantKG('coco_workspace/test_personal_kg.db')

    # Test realistic personal assistant interactions
    test_exchanges = [
        ("My wife Kerry loves reading books", "I'll remember that Kerry is your wife and loves reading!", ['remember_fact']),
        ("I work with Sarah at the office in Chicago", "Got it - Sarah is a colleague and you work in Chicago.", ['remember_fact']),
        ("I use Python for development", "Python noted as your preferred development tool.", ['remember_preference']),
        ("I completed the COCO memory system", "Great work finishing the COCO memory system!", ['task_completed']),
        ("Need to call John tomorrow", "I'll remind you to call John tomorrow.", ['create_reminder']),
    ]

    for user_input, assistant_response, tools in test_exchanges:
        stats = kg.process_conversation_exchange(user_input, assistant_response, tools)
        print(f"Processed: {stats}")

    # Check user knowledge
    knowledge = kg.get_user_knowledge()
    print(f"\nUser Knowledge Summary:")
    print(f"People: {knowledge['people']}")
    print(f"Tools: {knowledge['preferred_tools']}")
    print(f"Tasks: {knowledge['recent_tasks']}")

    # Test context retrieval
    context = kg.get_context_for_query("Kerry")
    print(f"\nContext for 'Kerry': {context}")

if __name__ == "__main__":
    test_personal_assistant_kg()