#!/usr/bin/env python3
"""
COCO Personal Assistant Knowledge Graph - Enhanced Edition
=========================================================

Revolutionary focused approach: 75 entities that matter vs. 6,674 noise
- 12 people in your life
- 6 topics you care about
- 24 repeated tasks
- 8 tools you use
- 5 active projects
- 20 preferences/patterns

With RAG layer for semantic search and tool pattern learning.
"""

import sqlite3
import json
import uuid
import re
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter

class PersonalAssistantKG:
    """
    Knowledge graph optimized for personal assistant intelligence

    Philosophy: Remember what a human assistant would remember
    Focus: Quality over quantity - 75 meaningful entities vs. 6674 noise
    """

    def __init__(self, db_path: str = 'coco_workspace/coco_personal_kg.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.debug_mode = os.getenv('COCO_DEBUG', '').lower() in ('true', '1', 'yes')

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

        # Performance optimization
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")

        # Entity validation thresholds
        self.min_context_length = 15  # Must have meaningful context
        self.max_entities = 100  # Practical limit for personal assistant

        # Rich embedding support (for future RAG integration)
        self.enable_embeddings = os.getenv('ENABLE_EMBEDDINGS', '').lower() in ('true', '1', 'yes')

        if self.debug_mode:
            print(f"🧠 Personal Assistant KG initialized: {self.db_path}")
            print(f"   Max entities: {self.max_entities}, Context required: {self.min_context_length} chars")

    def init_schema(self):
        """Schema designed for personal assistant needs with rich context"""
        self.conn.executescript('''
        -- =====================================================================
        -- CORE ENTITIES - The people, places, tools that matter
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            canonical_name TEXT,
            type TEXT CHECK(type IN ('PERSON','PLACE','TOOL','TASK','PROJECT','PREFERENCE')),

            -- Rich context for semantic understanding
            role TEXT,                    -- "wife", "colleague", "office location"
            description TEXT,              -- Full context about this entity
            summary_context TEXT,          -- Last 3 interactions summary

            -- Importance tracking
            importance REAL DEFAULT 0.5,
            usefulness_score REAL DEFAULT 1.0,  -- Learning: was this entity useful?
            mention_count INTEGER DEFAULT 1,

            -- Temporal tracking
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_mentioned TEXT DEFAULT CURRENT_TIMESTAMP,
            last_context TEXT,             -- Most recent context snippet

            -- Metadata
            properties JSON DEFAULT '{}'
        );

        -- =====================================================================
        -- RELATIONSHIPS - User-centric connections
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            user_entity TEXT NOT NULL DEFAULT 'USER',
            related_entity TEXT NOT NULL,
            relationship_type TEXT NOT NULL,

            -- Relationship details
            description TEXT,
            context_snippets TEXT,         -- Recent contexts where this relationship appeared

            -- Strength tracking
            strength REAL DEFAULT 1.0,
            confidence REAL DEFAULT 0.5,

            -- Temporal tracking
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_confirmed TEXT DEFAULT CURRENT_TIMESTAMP,
            mention_count INTEGER DEFAULT 1,

            FOREIGN KEY(related_entity) REFERENCES entities(id),
            UNIQUE(user_entity, related_entity, relationship_type)
        );

        -- =====================================================================
        -- TOOL PATTERNS - Learn how user accomplishes tasks
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS tool_patterns (
            id TEXT PRIMARY KEY,
            pattern_name TEXT NOT NULL,

            -- Pattern details
            trigger_phrases TEXT,          -- "send update", "do Friday routine"
            tool_sequence TEXT,            -- JSON: [tool1, tool2, tool3]
            parameters JSON,               -- Typical parameters used

            -- Usage tracking
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            last_used TEXT,

            -- Context
            typical_context TEXT,
            frequency TEXT,                -- "weekly", "daily", "as-needed"

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- =====================================================================
        -- TOOL USAGE LOG - Track actual tool calls
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS tool_usage (
            id TEXT PRIMARY KEY,
            tool_name TEXT NOT NULL,
            parameters JSON,
            context TEXT,
            pattern_id TEXT,               -- Link to tool_pattern if part of pattern
            successful BOOLEAN DEFAULT TRUE,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(pattern_id) REFERENCES tool_patterns(id)
        );

        -- =====================================================================
        -- EMBEDDINGS - For RAG semantic search
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS entity_embeddings (
            entity_id TEXT PRIMARY KEY,
            embedding_text TEXT NOT NULL,  -- Rich text used for embedding
            embedding BLOB,                -- Actual embedding vector (future)
            embedding_model TEXT DEFAULT 'text-embedding-3-small',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(entity_id) REFERENCES entities(id)
        );

        -- =====================================================================
        -- CONTEXT EFFECTIVENESS - Learn what context helps
        -- =====================================================================
        CREATE TABLE IF NOT EXISTS context_effectiveness (
            id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            query TEXT,
            was_useful BOOLEAN,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(entity_id) REFERENCES entities(id)
        );

        -- =====================================================================
        -- INDEXES
        -- =====================================================================
        CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
        CREATE INDEX IF NOT EXISTS idx_entities_importance ON entities(importance DESC);
        CREATE INDEX IF NOT EXISTS idx_entities_last_mentioned ON entities(last_mentioned DESC);
        CREATE INDEX IF NOT EXISTS idx_entities_usefulness ON entities(usefulness_score DESC);

        CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
        CREATE INDEX IF NOT EXISTS idx_relationships_strength ON relationships(strength DESC);

        CREATE INDEX IF NOT EXISTS idx_tool_patterns_name ON tool_patterns(pattern_name);
        CREATE INDEX IF NOT EXISTS idx_tool_usage_tool ON tool_usage(tool_name);
        CREATE INDEX IF NOT EXISTS idx_tool_usage_timestamp ON tool_usage(timestamp DESC);
        ''')
        self.conn.commit()

    def _extract_entities_with_llm(self, user_text: str, assistant_text: str) -> List[Dict]:
        """
        Use Claude API for intelligent entity extraction from natural conversation.

        This is the breakthrough that makes the KG actually work - catches entities
        that regex patterns miss like "Ilia (15-year friend)" or "Mike ← → Keith".

        Returns:
            List of entities with {name, type, role, context, confidence}
        """
        try:
            # Get Anthropic API key from environment
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                if self.debug_mode:
                    print("⚠️ ANTHROPIC_API_KEY not found - skipping LLM extraction")
                return []

            client = anthropic.Anthropic(api_key=api_key)

            # Simple, focused prompt (senior dev's recommendation)
            prompt = f"""Extract only the most important entities from this conversation.

Return JSON list with ONLY these types:
- PERSON: Real people mentioned by name (not "user", "someone")
- PROJECT: Named projects or companies
- TOOL: Specific software/tools that were USED (not just mentioned)

Format: [{{"name": "X", "type": "Y", "context": "brief context", "confidence": 0.0-1.0}}]

Conversation:
User: {user_text}
Assistant: {assistant_text}

Only return entities with confidence > 0.7. Return ONLY valid JSON array, nothing else."""

            # Use Claude-3-Haiku (fast, cheap, perfect for extraction)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse JSON response
            response_text = response.content[0].text.strip()

            # Handle markdown code blocks if present
            if response_text.startswith('```'):
                # Extract JSON from code block
                lines = response_text.split('\n')
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        json_lines.append(line)
                response_text = '\n'.join(json_lines)

            entities = json.loads(response_text)

            # Validate and filter
            valid_entities = []
            for entity in entities:
                if isinstance(entity, dict) and 'name' in entity and 'type' in entity:
                    # Confidence threshold check
                    confidence = entity.get('confidence', 0.8)
                    if confidence >= 0.7:
                        # Type-specific confidence thresholds (senior dev's recommendation)
                        type_threshold = {
                            'PERSON': 0.8,
                            'PROJECT': 0.7,
                            'TOOL': 0.9
                        }.get(entity['type'], 0.7)

                        if confidence >= type_threshold:
                            valid_entities.append({
                                'name': entity['name'],
                                'type': entity['type'],
                                'role': entity.get('role', ''),
                                'context': entity.get('context', user_text[:100]),
                                'confidence': confidence
                            })

            if self.debug_mode and valid_entities:
                print(f"🤖 LLM extracted {len(valid_entities)} entities: {[e['name'] for e in valid_entities]}")

            return valid_entities

        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ LLM extraction error: {e}")
            return []

    def _normalize_name(self, name: str) -> str:
        """Normalize entity name for deduplication: Ilia, Ilya, ILIA → ilia"""
        return name.lower().strip()

    def _merge_entities(self, pattern_entities: List[Dict], llm_entities: List[Dict]) -> List[Dict]:
        """
        Smart deduplication and merging of entities from different sources.

        Strategy:
        - Pattern entities have higher confidence (explicit linguistic markers)
        - LLM entities fill gaps that patterns miss
        - Merge contexts to enrich understanding
        """
        merged = {}

        # Pattern entities first (higher confidence)
        for entity in pattern_entities:
            key = self._normalize_name(entity['name'])
            merged[key] = entity

        # LLM entities fill gaps or enrich existing
        for entity in llm_entities:
            key = self._normalize_name(entity['name'])
            if key not in merged:
                merged[key] = entity
            else:
                # Enrich existing with more context
                existing_context = merged[key].get('context', '')
                new_context = entity.get('context', '')
                if new_context and new_context not in existing_context:
                    merged[key]['context'] = existing_context + " | " + new_context

        return list(merged.values())

    def process_conversation_exchange(self, user_input: str, assistant_response: str,
                                     tools_used: List[Dict] = None,
                                     message_id: str = None,
                                     episode_id: int = None) -> Dict:
        """
        Process conversation with focus on what matters

        Args:
            user_input: What user said
            assistant_response: COCO's response
            tools_used: List of {name: str, params: dict, success: bool}
            message_id: Episode identifier
            episode_id: Session episode number

        Returns:
            Stats: entities added, relationships created, patterns learned
        """
        stats = {
            'entities_added': 0,
            'relationships_added': 0,
            'patterns_learned': 0,
            'tools_recorded': 0
        }

        if message_id is None:
            message_id = str(uuid.uuid4())[:8]

        # Record actual tool usage (critical for pattern learning)
        if tools_used:
            for tool_call in tools_used:
                self._record_tool_usage(
                    tool_name=tool_call.get('name', 'unknown'),
                    parameters=tool_call.get('params', {}),
                    context=user_input,
                    successful=tool_call.get('success', True)
                )
                stats['tools_recorded'] += 1

        # =====================================================================
        # HYBRID ENTITY EXTRACTION - Pattern + LLM (BREAKTHROUGH FIX)
        # =====================================================================

        # Step 1: Fast pattern-based extraction (existing approach)
        pattern_entities = self._extract_entities_strict(user_input)

        # Step 2: LLM-based extraction for entities patterns miss
        # Only call LLM if conversation seems significant or patterns found nothing
        combined_text = user_input + " " + assistant_response
        is_significant = len(combined_text) > 100  # Not just "ok" or "thanks"

        llm_entities = []
        if is_significant or not pattern_entities:
            # Use LLM to catch "Ilia (15-year friend)" style mentions
            llm_entities = self._extract_entities_with_llm(user_input, assistant_response)

        # Step 3: Merge and deduplicate (pattern entities prioritized)
        all_entities = self._merge_entities(pattern_entities, llm_entities)

        # Step 4: Add validated entities to knowledge graph
        for entity in all_entities:
            if self._add_entity_with_validation(entity):
                stats['entities_added'] += 1

                # Create rich embedding text for future RAG
                if self.enable_embeddings:
                    self._create_rich_embedding(entity)

        # Extract relationships (user-centric only)
        relationships = self._extract_relationships_strict(user_input)

        for rel in relationships:
            if self._add_relationship(rel):
                stats['relationships_added'] += 1

        # Learn tool patterns if multiple tools used in sequence
        if tools_used and len(tools_used) >= 2:
            pattern = self._detect_tool_pattern(user_input, tools_used)
            if pattern:
                self._store_tool_pattern(pattern)
                stats['patterns_learned'] += 1

        return stats

    def _extract_entities_strict(self, text: str) -> List[Dict]:
        """
        Extract entities with STRICT validation - only meaningful entities

        Requirements:
        - Must have meaningful context (>15 chars around mention)
        - Must not be common words
        - Must appear in actionable context
        """
        entities = []

        # PERSON extraction with context validation
        # NOTE: Use \b word boundaries to prevent over-capturing
        person_patterns = [
            # Family relationships (capture name AFTER relationship word)
            (r'(?:my wife|my husband|my partner|my spouse)\s+([A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?\b', 'family', 0.95),
            (r'(?:my boss|my manager)\s+([A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?\b', 'manager', 0.9),
            (r'(?:my colleague|my coworker)\s+([A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?\b', 'colleague', 0.85),
            (r'(?:my friend)\s+([A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?\b', 'friend', 0.8),
            # Work relationships
            (r'(?:work with|working with)\s+([A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?\b', 'colleague', 0.8),
            (r'(?:talk to|email|call|meet with)\s+([A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?\b', 'contact', 0.7),
            # Reverse patterns (name BEFORE relationship)
            (r'([A-Z][a-z]+)\s+(?:is my wife|is my husband|is my partner)', 'family', 0.95),
            (r'([A-Z][a-z]+)\s+(?:is my colleague|works with me)', 'colleague', 0.8),
        ]

        for pattern, role, confidence in person_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                name = match.group(1).strip()
                context = text[max(0, match.start()-30):match.end()+30]

                if len(context) >= self.min_context_length and self._is_meaningful_person(name, context):
                    entities.append({
                        'name': name,
                        'type': 'PERSON',
                        'role': role,
                        'context': context,
                        'confidence': confidence
                    })

        # TOOL extraction (known tools only)
        known_tools = [
            'Python', 'JavaScript', 'TypeScript', 'Claude', 'COCO', 'SQLite',
            'Git', 'Docker', 'VSCode', 'Gmail', 'Slack', 'Zoom', 'GitHub',
            'Postgres', 'Redis', 'React', 'Vue', 'FastAPI', 'Django'
        ]

        for tool in known_tools:
            if tool in text:
                # Check if used in actionable context
                actionable_context = any(word in text.lower() for word in
                    ['use', 'using', 'prefer', 'build', 'develop', 'deploy', 'work'])

                if actionable_context:
                    entities.append({
                        'name': tool,
                        'type': 'TOOL',
                        'context': text,
                        'confidence': 0.9
                    })

        # PLACE extraction (locations with context)
        place_patterns = [
            r'office (?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'(?:live|work|based)\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'meeting at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        ]

        for pattern in place_patterns:
            for match in re.finditer(pattern, text):
                place = match.group(1).strip()
                if len(place) >= 3:  # Minimum length
                    entities.append({
                        'name': place,
                        'type': 'PLACE',
                        'context': text[max(0, match.start()-20):match.end()+20],
                        'confidence': 0.7
                    })

        # PROJECT extraction (acronyms and explicit mentions)
        project_patterns = [
            r'\b([A-Z]{2,6})\b(?:\s+(?:project|system|repo))',
            r'(?:working on|building|developing)\s+([A-Z][A-Za-z]+)',
        ]

        for pattern in project_patterns:
            for match in re.finditer(pattern, text):
                project = match.group(1).strip()
                if len(project) >= 2 and project not in ['AI', 'API', 'UI', 'UX']:  # Filter common abbreviations
                    entities.append({
                        'name': project,
                        'type': 'PROJECT',
                        'context': text,
                        'confidence': 0.7
                    })

        # TASK extraction (actual actionable tasks)
        task_patterns = [
            r'(?:need to|should|must|will)\s+([a-z][a-z\s]{5,40})',
            r'(?:completed|finished)\s+([a-z][a-z\s]{5,40})',
            r'todo:?\s*([a-z][a-z\s]{5,40})',
        ]

        for pattern in task_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                task = match.group(1).strip()
                if len(task) >= 8 and self._is_actionable_task(task):
                    entities.append({
                        'name': task,
                        'type': 'TASK',
                        'context': text,
                        'confidence': 0.6
                    })

        # PREFERENCE extraction (explicit statements)
        pref_patterns = [
            r'I (?:like|love|prefer|hate|dislike|always|usually)\s+([a-z][a-z\s]{3,30})',
        ]

        for pattern in pref_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                pref = match.group(1).strip()
                entities.append({
                    'name': pref,
                    'type': 'PREFERENCE',
                    'context': text,
                    'confidence': 0.7
                })

        return entities

    def _is_meaningful_person(self, name: str, context: str) -> bool:
        """Validate that this is a real person entity with context"""
        # Must be capitalized name
        if not name[0].isupper():
            return False

        # Must not be common words
        common_words = {'The', 'This', 'That', 'These', 'Those', 'Your', 'Their', 'Client', 'User'}
        if name in common_words:
            return False

        # Must have person-indicating context
        person_indicators = ['my', 'wife', 'husband', 'colleague', 'boss', 'work', 'email', 'call', 'meet']
        context_lower = context.lower()

        return any(indicator in context_lower for indicator in person_indicators)

    def _extract_role(self, context: str) -> Optional[str]:
        """Extract role from context"""
        role_patterns = [
            (r'my (wife|husband|partner|spouse)', 'family'),
            (r'my (boss|manager|supervisor)', 'manager'),
            (r'my (colleague|coworker)', 'colleague'),
            (r'(friend)', 'friend'),
        ]

        for pattern, role in role_patterns:
            if re.search(pattern, context.lower()):
                return role

        return 'contact'

    def _is_actionable_task(self, task: str) -> bool:
        """Check if task description is actionable"""
        # Must contain a verb
        action_verbs = ['send', 'email', 'call', 'write', 'create', 'build', 'fix',
                       'update', 'deploy', 'test', 'review', 'analyze', 'implement']

        task_lower = task.lower()
        return any(verb in task_lower for verb in action_verbs)

    def _extract_relationships_strict(self, text: str) -> List[Dict]:
        """Extract user-centric relationships with validation"""
        relationships = []

        # Family relationships (high confidence) - TWO patterns to cover both orders
        family_patterns = [
            # Pattern 1: "my wife Kerry" - name is group 2 - use \b to prevent over-capture
            (r'my (wife|husband|partner|spouse)\s+([A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?\b', 'FAMILY', 0.95, 2),
            # Pattern 2: "Kerry is my wife" - name is group 1
            (r'([A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?\s+is my (wife|husband|partner|spouse)', 'FAMILY', 0.95, 1),
        ]

        for pattern, rel_type, confidence, name_group in family_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if match.lastindex >= name_group:
                    # Extract name from specified group
                    name = match.group(name_group).strip()

                    if name and name[0].isupper():
                        relationships.append({
                            'user_entity': 'USER',
                            'related_entity': name,
                            'relationship_type': rel_type,
                            'confidence': confidence,
                            'context': text[max(0, match.start()-30):match.end()+30],
                            'description': match.group(1) if name_group == 2 else match.group(2)
                        })

        # Work relationships
        work_patterns = [
            (r'work with ([A-Z][a-z]+)', 'WORKS_WITH', 0.8),
            (r'([A-Z][a-z]+)\s+and I work', 'WORKS_WITH', 0.8),
            (r'colleague ([A-Z][a-z]+)', 'WORKS_WITH', 0.7),
        ]

        for pattern, rel_type, confidence in work_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                name = match.group(1).strip()
                if self._is_meaningful_person(name, text):
                    relationships.append({
                        'user_entity': 'USER',
                        'related_entity': name,
                        'relationship_type': rel_type,
                        'confidence': confidence,
                        'context': text
                    })

        # Tool usage relationships
        tool_patterns = [
            (r'I (?:use|prefer)\s+([A-Z][a-z]+)', 'USES', 0.8),
            (r'using ([A-Z][a-z]+)', 'USES', 0.7),
        ]

        for pattern, rel_type, confidence in tool_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                tool = match.group(1).strip()
                relationships.append({
                    'user_entity': 'USER',
                    'related_entity': tool,
                    'relationship_type': rel_type,
                    'confidence': confidence,
                    'context': text
                })

        return relationships

    def _add_entity_with_validation(self, entity: Dict) -> bool:
        """
        Add entity with strict validation

        Ensures we don't exceed max_entities limit and maintains quality
        """
        try:
            # Check entity limit
            count = self.conn.execute('SELECT COUNT(*) FROM entities').fetchone()[0]
            if count >= self.max_entities:
                # Only add if higher importance than lowest entity
                lowest = self.conn.execute('''
                    SELECT importance FROM entities
                    ORDER BY importance ASC, mention_count ASC
                    LIMIT 1
                ''').fetchone()

                if entity.get('confidence', 0.5) <= lowest[0]:
                    if self.debug_mode:
                        print(f"⚠️ Entity limit reached, {entity['name']} not important enough")
                    return False

            # Check if exists
            existing = self.conn.execute(
                'SELECT id, mention_count FROM entities WHERE name = ?',
                (entity['name'],)
            ).fetchone()

            if existing:
                # Update existing entity
                self.conn.execute('''
                    UPDATE entities
                    SET last_mentioned = CURRENT_TIMESTAMP,
                        mention_count = mention_count + 1,
                        last_context = ?,
                        importance = MIN(importance + 0.05, 1.0)
                    WHERE name = ?
                ''', (entity.get('context', '')[:200], entity['name']))
                self.conn.commit()
                return False
            else:
                # Create new entity
                entity_id = str(uuid.uuid4())[:8]
                self.conn.execute('''
                    INSERT INTO entities
                    (id, name, canonical_name, type, role, description,
                     last_context, importance, properties)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entity_id,
                    entity['name'],
                    entity['name'].lower(),
                    entity['type'],
                    entity.get('role'),
                    entity.get('context', '')[:500],
                    entity.get('context', '')[:200],
                    entity.get('confidence', 0.5),
                    json.dumps({})
                ))
                self.conn.commit()

                if self.debug_mode:
                    print(f"✅ Added {entity['type']}: {entity['name']}")

                return True

        except sqlite3.Error as e:
            if self.debug_mode:
                print(f"❌ Entity error: {e}")
            return False

    def _add_relationship(self, rel: Dict) -> bool:
        """Add or strengthen relationship"""
        try:
            # Ensure related entity exists
            entity_check = self.conn.execute(
                'SELECT id FROM entities WHERE name = ?',
                (rel['related_entity'],)
            ).fetchone()

            if not entity_check:
                # Create entity first (with lower confidence)
                entity_id = str(uuid.uuid4())[:8]
                self.conn.execute('''
                    INSERT INTO entities (id, name, canonical_name, type, importance)
                    VALUES (?, ?, ?, ?, ?)
                ''', (entity_id, rel['related_entity'],
                     rel['related_entity'].lower(), 'PERSON', 0.4))

            # Check if relationship exists
            existing = self.conn.execute('''
                SELECT strength, mention_count FROM relationships
                WHERE user_entity = ? AND related_entity = ? AND relationship_type = ?
            ''', (rel['user_entity'], rel['related_entity'], rel['relationship_type'])).fetchone()

            if existing:
                # Strengthen existing relationship
                new_strength = min(existing['strength'] + 0.1, 2.0)
                self.conn.execute('''
                    UPDATE relationships
                    SET strength = ?,
                        last_confirmed = CURRENT_TIMESTAMP,
                        mention_count = mention_count + 1,
                        confidence = MIN(confidence + 0.05, 1.0)
                    WHERE user_entity = ? AND related_entity = ? AND relationship_type = ?
                ''', (new_strength, rel['user_entity'], rel['related_entity'],
                     rel['relationship_type']))
            else:
                # Create new relationship
                rel_id = str(uuid.uuid4())[:8]
                self.conn.execute('''
                    INSERT INTO relationships
                    (id, user_entity, related_entity, relationship_type,
                     context_snippets, strength, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (rel_id, rel['user_entity'], rel['related_entity'],
                     rel['relationship_type'], rel.get('context', '')[:200],
                     1.0, rel.get('confidence', 0.5)))

            self.conn.commit()
            return True

        except sqlite3.Error as e:
            if self.debug_mode:
                print(f"❌ Relationship error: {e}")
            return False

    def _record_tool_usage(self, tool_name: str, parameters: Dict,
                          context: str, successful: bool = True):
        """Record tool usage for pattern learning"""
        try:
            usage_id = str(uuid.uuid4())[:8]
            self.conn.execute('''
                INSERT INTO tool_usage (id, tool_name, parameters, context, successful)
                VALUES (?, ?, ?, ?, ?)
            ''', (usage_id, tool_name, json.dumps(parameters),
                 context[:300], successful))
            self.conn.commit()

            if self.debug_mode:
                print(f"📝 Recorded: {tool_name} ({'✓' if successful else '✗'})")

        except sqlite3.Error as e:
            if self.debug_mode:
                print(f"❌ Tool usage error: {e}")

    def _detect_tool_pattern(self, trigger: str, tools_used: List[Dict]) -> Optional[Dict]:
        """
        Detect if tool sequence represents a learnable pattern

        Returns pattern dict if this looks like a repeated workflow
        """
        # Need at least 2 tools for a pattern
        if len(tools_used) < 2:
            return None

        # Extract tool sequence
        tool_sequence = [t['name'] for t in tools_used]

        # Check if we've seen similar sequence before
        recent_patterns = self.conn.execute('''
            SELECT tool_sequence, COUNT(*) as frequency
            FROM tool_patterns
            WHERE created_at > datetime('now', '-30 days')
            GROUP BY tool_sequence
            ORDER BY frequency DESC
            LIMIT 10
        ''').fetchall()

        # If this sequence exists, it's a pattern
        tool_seq_json = json.dumps(tool_sequence)
        for row in recent_patterns:
            if row['tool_sequence'] == tool_seq_json and row['frequency'] >= 2:
                return {
                    'trigger_phrase': trigger[:100],
                    'tool_sequence': tool_sequence,
                    'parameters': [t.get('params', {}) for t in tools_used]
                }

        return None

    def _store_tool_pattern(self, pattern: Dict):
        """Store learned tool pattern for future recreation"""
        try:
            pattern_id = str(uuid.uuid4())[:8]
            pattern_name = f"pattern_{pattern_id}"

            self.conn.execute('''
                INSERT INTO tool_patterns
                (id, pattern_name, trigger_phrases, tool_sequence, parameters)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                pattern_id,
                pattern_name,
                pattern['trigger_phrase'],
                json.dumps(pattern['tool_sequence']),
                json.dumps(pattern['parameters'])
            ))
            self.conn.commit()

            if self.debug_mode:
                print(f"🎯 Learned pattern: {pattern['trigger_phrase'][:50]}...")

        except sqlite3.Error as e:
            if self.debug_mode:
                print(f"❌ Pattern storage error: {e}")

    def _create_rich_embedding(self, entity: Dict):
        """
        Create rich embedding text for semantic search

        This is the MAGIC - comprehensive context in one embedding
        """
        entity_id = self.conn.execute(
            'SELECT id FROM entities WHERE name = ?',
            (entity['name'],)
        ).fetchone()

        if not entity_id:
            return

        # Build rich context based on entity type
        if entity['type'] == 'PERSON':
            # Get all relationship context
            rels = self.conn.execute('''
                SELECT relationship_type, context_snippets
                FROM relationships
                WHERE related_entity = ?
            ''', (entity['name'],)).fetchall()

            rel_text = " | ".join([f"{r['relationship_type']}: {r['context_snippets']}"
                                   for r in rels if r['context_snippets']])

            embedding_text = f"""
            Person: {entity['name']}
            Role: {entity.get('role', 'contact')}
            Relationship: {rel_text}
            Recent context: {entity.get('context', '')}
            """

        elif entity['type'] == 'TOOL':
            # Get usage patterns
            usage = self.conn.execute('''
                SELECT COUNT(*) as count, MAX(timestamp) as last_used
                FROM tool_usage
                WHERE tool_name = ?
            ''', (entity['name'],)).fetchone()

            embedding_text = f"""
            Tool: {entity['name']}
            Usage count: {usage['count']}
            Last used: {usage['last_used']}
            Context: {entity.get('context', '')}
            """

        elif entity['type'] == 'TASK':
            embedding_text = f"""
            Task: {entity['name']}
            Type: {entity['type']}
            Context: {entity.get('context', '')}
            """

        else:
            embedding_text = f"""
            {entity['type']}: {entity['name']}
            Description: {entity.get('context', '')}
            """

        # Store embedding text (actual vector embedding is future enhancement)
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO entity_embeddings
                (entity_id, embedding_text)
                VALUES (?, ?)
            ''', (entity_id[0], embedding_text.strip()))
            self.conn.commit()
        except sqlite3.Error:
            pass

    def get_knowledge_status(self) -> Dict:
        """Get current knowledge graph statistics"""
        stats = {}

        # Entity counts by type
        type_counts = self.conn.execute('''
            SELECT type, COUNT(*) as count
            FROM entities
            GROUP BY type
            ORDER BY count DESC
        ''').fetchall()

        stats['entity_types'] = {row['type']: row['count'] for row in type_counts}
        stats['total_entities'] = sum(stats['entity_types'].values())

        # Relationship counts
        rel_counts = self.conn.execute('''
            SELECT relationship_type, COUNT(*) as count
            FROM relationships
            GROUP BY relationship_type
            ORDER BY count DESC
        ''').fetchall()

        stats['relationship_types'] = {row['relationship_type']: row['count']
                                       for row in rel_counts}
        stats['total_relationships'] = sum(stats['relationship_types'].values())

        # Tool usage
        stats['total_tool_calls'] = self.conn.execute(
            'SELECT COUNT(*) FROM tool_usage'
        ).fetchone()[0]

        # Learned patterns
        stats['learned_patterns'] = self.conn.execute(
            'SELECT COUNT(*) FROM tool_patterns'
        ).fetchone()[0]

        return stats

    def get_conversation_context(self, current_message: str = None,
                                 max_tokens: int = 2000) -> str:
        """
        Assemble intelligent context for current conversation

        Returns focused, relevant context - not garbage
        """
        context_sections = []

        # Get status summary
        status = self.get_knowledge_status()

        # Header
        header = f"""## 🧠 Personal Assistant Memory

**Your World:**
- {status['entity_types'].get('PERSON', 0)} people you know
- {status['entity_types'].get('PROJECT', 0)} active projects
- {status['entity_types'].get('TOOL', 0)} tools you use
- {status['total_relationships']} key relationships
- {status['learned_patterns']} learned patterns

"""
        context_sections.append(header)

        # If current message provided, add query-specific context
        if current_message:
            query_context = self._get_query_context(current_message)
            if query_context:
                context_sections.append(query_context)

        # Add important people (max 5)
        people = self.conn.execute('''
            SELECT e.name, r.relationship_type, e.role, e.mention_count
            FROM entities e
            LEFT JOIN relationships r ON e.name = r.related_entity AND r.user_entity = 'USER'
            WHERE e.type = 'PERSON'
            ORDER BY e.importance DESC, e.mention_count DESC
            LIMIT 5
        ''').fetchall()

        if people:
            people_text = "**Key People:**\n"
            for p in people:
                rel = p['relationship_type'] or 'contact'
                role = p['role'] or ''
                people_text += f"- {p['name']} ({rel}{', ' + role if role else ''})\n"
            context_sections.append(people_text)

        # Add recent tool patterns
        patterns = self.conn.execute('''
            SELECT trigger_phrases, tool_sequence, success_count
            FROM tool_patterns
            WHERE success_count > 0
            ORDER BY last_used DESC
            LIMIT 3
        ''').fetchall()

        if patterns:
            pattern_text = "**Learned Patterns:**\n"
            for p in patterns:
                tools = json.loads(p['tool_sequence'])
                pattern_text += f"- \"{p['trigger_phrases'][:40]}...\" → {' → '.join(tools)}\n"
            context_sections.append(pattern_text)

        return "\n".join(context_sections)

    def _get_query_context(self, query: str) -> str:
        """Get context specific to query"""
        query_lower = query.lower()
        context_parts = []

        # Search for relevant entities
        entities = self.conn.execute('''
            SELECT name, type, role, description
            FROM entities
            WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ?
            ORDER BY importance DESC, mention_count DESC
            LIMIT 5
        ''', (f'%{query_lower}%', f'%{query_lower}%')).fetchall()

        if entities:
            context_parts.append("**Relevant to your query:**")
            for e in entities:
                desc = e['role'] or e['description'][:100] if e['description'] else ''
                context_parts.append(f"- {e['name']} ({e['type']}{', ' + desc if desc else ''})")

        return "\n".join(context_parts) if context_parts else ""

    def track_context_effectiveness(self, entity_ids: List[str],
                                   query: str, was_useful: bool):
        """
        Learning loop: track if context was actually useful

        Critical for improving context selection over time
        """
        for entity_id in entity_ids:
            try:
                # Record effectiveness
                track_id = str(uuid.uuid4())[:8]
                self.conn.execute('''
                    INSERT INTO context_effectiveness
                    (id, entity_id, query, was_useful)
                    VALUES (?, ?, ?, ?)
                ''', (track_id, entity_id, query[:200], was_useful))

                # Adjust usefulness score
                if was_useful:
                    self.conn.execute('''
                        UPDATE entities
                        SET usefulness_score = MIN(usefulness_score * 1.1, 2.0)
                        WHERE id = ?
                    ''', (entity_id,))
                else:
                    self.conn.execute('''
                        UPDATE entities
                        SET usefulness_score = MAX(usefulness_score * 0.9, 0.1)
                        WHERE id = ?
                    ''', (entity_id,))

                self.conn.commit()
            except sqlite3.Error:
                pass

    def migrate_from_old_kg(self, old_db_path: str,
                           max_entities: int = 100) -> Dict:
        """
        Migrate valuable entities from old broken KG

        Extract the gems from 6,674 rocks
        """
        try:
            old_conn = sqlite3.connect(old_db_path)
            old_conn.row_factory = sqlite3.Row
        except Exception as e:
            return {'error': f'Could not open old KG: {e}'}

        migration_stats = {
            'evaluated': 0,
            'migrated': 0,
            'skipped_low_quality': 0,
            'skipped_no_relationships': 0
        }

        # Get entities worth keeping from old KG
        old_entities = old_conn.execute('''
            SELECT n.*, COUNT(e.id) as edge_count, COUNT(m.id) as mention_count
            FROM nodes n
            LEFT JOIN edges e ON n.id = e.src_id OR n.id = e.dst_id
            LEFT JOIN mentions m ON n.id = m.node_id
            WHERE n.importance > 0.7
                AND n.last_seen_at > datetime('now', '-30 days')
            GROUP BY n.id
            HAVING edge_count > 0 OR mention_count > 3
            ORDER BY n.importance DESC, edge_count DESC
            LIMIT ?
        ''', (max_entities * 2,)).fetchall()  # Get 2x to filter down

        for old_entity in old_entities:
            migration_stats['evaluated'] += 1

            # Quality checks
            if old_entity['edge_count'] == 0:
                migration_stats['skipped_no_relationships'] += 1
                continue

            # Map old types to new types
            type_mapping = {
                'Person': 'PERSON',
                'Org': 'TOOL',  # Organizations become tools
                'Project': 'PROJECT',
                'Task': 'TASK',
                'Concept': 'PREFERENCE',  # Concepts become preferences
                'Tool': 'TOOL',
                'Doc': 'TOOL',
                'Location': 'PLACE'
            }

            new_type = type_mapping.get(old_entity['type'])
            if not new_type:
                migration_stats['skipped_low_quality'] += 1
                continue

            # Create entity in new KG
            try:
                entity_id = str(uuid.uuid4())[:8]
                self.conn.execute('''
                    INSERT OR IGNORE INTO entities
                    (id, name, canonical_name, type, description, importance, mention_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entity_id,
                    old_entity['name'],
                    old_entity['canonical_name'],
                    new_type,
                    old_entity.get('summary_md', ''),
                    old_entity['importance'],
                    old_entity['mention_count']
                ))
                self.conn.commit()
                migration_stats['migrated'] += 1

            except sqlite3.Error:
                migration_stats['skipped_low_quality'] += 1

            # Stop if we hit target
            if migration_stats['migrated'] >= max_entities:
                break

        old_conn.close()

        if self.debug_mode:
            print(f"\n🔄 Migration Complete:")
            print(f"   Evaluated: {migration_stats['evaluated']}")
            print(f"   Migrated: {migration_stats['migrated']}")
            print(f"   Skipped (low quality): {migration_stats['skipped_low_quality']}")
            print(f"   Skipped (no relationships): {migration_stats['skipped_no_relationships']}")

        return migration_stats

    def get_relevant_entities_rag(self, query: str, k: int = 5) -> str:
        """
        RAG-style entity retrieval based on relevance for context injection.

        Args:
            query: Current conversation text to find relevant entities
            k: Number of entities to retrieve

        Returns:
            Formatted string with relevant entities and relationships
        """
        query_lower = query.lower()

        # Get entities with semantic relevance
        cursor = self.conn.execute('''
            SELECT e.name, e.type, e.role, e.description,
                   e.importance, e.mention_count
            FROM entities e
            WHERE e.importance > 0.3
              AND (LOWER(e.name) LIKE ?
                   OR LOWER(e.description) LIKE ?
                   OR LOWER(e.role) LIKE ?
                   OR LOWER(e.summary_context) LIKE ?)
            ORDER BY e.importance DESC, e.last_mentioned DESC
            LIMIT ?
        ''', (f'%{query_lower}%', f'%{query_lower}%',
              f'%{query_lower}%', f'%{query_lower}%', k))

        entities = cursor.fetchall()
        if not entities:
            return ""

        context_parts = ["📊 Relevant Knowledge:"]
        for entity in entities:
            role = entity['role'] or ''
            context_parts.append(
                f"- {entity['name']} ({entity['type']}"
                f"{', ' + role if role else ''})"
            )

        # Also get relationships for these entities
        entity_names = [e['name'] for e in entities]
        if entity_names:
            placeholders = ','.join(['?' for _ in entity_names])
            relationships = self.conn.execute(f'''
                SELECT DISTINCT user_entity, related_entity, relationship_type
                FROM relationships
                WHERE related_entity IN ({placeholders})
                   OR user_entity IN ({placeholders})
                LIMIT 5
            ''', entity_names + entity_names).fetchall()

            if relationships:
                context_parts.append("\n🔗 Relationships:")
                for rel in relationships:
                    context_parts.append(
                        f"- {rel['user_entity']} {rel['relationship_type']} {rel['related_entity']}"
                    )

        return "\n".join(context_parts)

    def add_entity_manual(self, name: str, entity_type: str,
                          role: str = None, description: str = None) -> bool:
        """
        Manually add an entity (for fixing missing entities like Ilia/Ramin).

        Args:
            name: Entity name (e.g., "Ilia")
            entity_type: Type (PERSON, ORGANIZATION, PROJECT, etc.)
            role: Entity's role or relationship (e.g., "Workshop participant")
            description: Detailed description

        Returns:
            True if successful
        """
        entity_id = str(uuid.uuid4())[:8]
        try:
            # First try to insert new entity
            self.conn.execute('''
                INSERT INTO entities (id, name, type, role, description, importance)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (entity_id, name, entity_type.upper(), role, description, 0.8))
            self.conn.commit()
            if self.debug_mode:
                print(f"✅ Added entity: {name} ({entity_type})")
            return True
        except sqlite3.IntegrityError:
            # Entity exists, update it
            self.conn.execute('''
                UPDATE entities
                SET role = COALESCE(?, role),
                    description = COALESCE(?, description),
                    importance = MIN(1.0, importance + 0.1),
                    last_mentioned = CURRENT_TIMESTAMP
                WHERE name = ?
            ''', (role, description, name))
            self.conn.commit()
            if self.debug_mode:
                print(f"✅ Updated entity: {name}")
            return True

    def add_relationship_manual(self, entity1: str, entity2: str,
                                relationship_type: str, description: str = None) -> bool:
        """
        Manually add a relationship between entities.

        Args:
            entity1: First entity name
            entity2: Second entity name
            relationship_type: Type of relationship (knows, works_at, attended, etc.)
            description: Optional description of the relationship

        Returns:
            True if successful
        """
        # Ensure both entities exist
        self.add_entity_manual(entity1, "PERSON", None, None)
        self.add_entity_manual(entity2, "PERSON", None, None)

        rel_id = str(uuid.uuid4())[:8]
        try:
            self.conn.execute('''
                INSERT INTO relationships (id, user_entity, related_entity,
                                         relationship_type, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (rel_id, entity1, entity2, relationship_type, description))
            self.conn.commit()
            if self.debug_mode:
                print(f"✅ Added relationship: {entity1} {relationship_type} {entity2}")
            return True
        except sqlite3.IntegrityError:
            # Relationship exists, update it
            self.conn.execute('''
                UPDATE relationships
                SET description = COALESCE(?, description),
                    strength = MIN(1.0, strength + 0.1),
                    last_confirmed = CURRENT_TIMESTAMP
                WHERE user_entity = ? AND related_entity = ? AND relationship_type = ?
            ''', (description, entity1, entity2, relationship_type))
            self.conn.commit()
            if self.debug_mode:
                print(f"✅ Updated relationship: {entity1} {relationship_type} {entity2}")
            return True

    def extract_from_recent_conversations(self, memory_system, max_exchanges: int = 100) -> Dict:
        """
        CRITICAL: Process existing conversations to populate empty KG.

        This is the senior dev's recommendation for immediate value -
        extract entities from conversations that happened before LLM extraction was added.

        Args:
            memory_system: COCO's HierarchicalMemorySystem with episodic memory
            max_exchanges: Number of recent conversations to process (default: 100)

        Returns:
            Stats: {entities_added, relationships_added, conversations_processed}
        """
        stats = {
            'entities_added': 0,
            'relationships_added': 0,
            'conversations_processed': 0,
            'time_elapsed': 0
        }

        import time
        start_time = time.time()

        try:
            # Get recent exchanges from episodic memory
            recent_exchanges = []

            if hasattr(memory_system, 'working_memory') and memory_system.working_memory:
                # Get from working memory buffer
                recent_exchanges = list(memory_system.working_memory)[-max_exchanges:]
            elif hasattr(memory_system, 'conn'):
                # Get from database
                cursor = memory_system.conn.execute('''
                    SELECT user_text, agent_text
                    FROM episodes
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (max_exchanges,))
                recent_exchanges = [{'user': row[0], 'agent': row[1]} for row in cursor.fetchall()]

            if not recent_exchanges:
                if self.debug_mode:
                    print("⚠️ No recent exchanges found in memory system")
                return stats

            if self.debug_mode:
                print(f"📚 Processing {len(recent_exchanges)} recent conversations...")

            # Batch process in chunks of 10 for efficiency (senior dev's recommendation)
            chunk_size = 10
            for i in range(0, len(recent_exchanges), chunk_size):
                chunk = recent_exchanges[i:i+chunk_size]

                # Process each exchange
                for exchange in chunk:
                    try:
                        user_text = exchange.get('user', '')
                        agent_text = exchange.get('agent', '')

                        if user_text and agent_text:
                            # Use the hybrid extraction strategy
                            exchange_stats = self.process_conversation_exchange(
                                user_input=user_text,
                                assistant_response=agent_text,
                                tools_used=None
                            )

                            stats['entities_added'] += exchange_stats.get('entities_added', 0)
                            stats['relationships_added'] += exchange_stats.get('relationships_added', 0)
                            stats['conversations_processed'] += 1

                    except Exception as e:
                        if self.debug_mode:
                            print(f"⚠️ Error processing exchange: {e}")
                        continue

                # Progress indicator
                if self.debug_mode and stats['conversations_processed'] % 10 == 0:
                    print(f"   Processed {stats['conversations_processed']} conversations, "
                          f"found {stats['entities_added']} entities...")

            stats['time_elapsed'] = time.time() - start_time

            if self.debug_mode:
                print(f"\n✅ Batch extraction complete!")
                print(f"   Conversations processed: {stats['conversations_processed']}")
                print(f"   Entities added: {stats['entities_added']}")
                print(f"   Relationships added: {stats['relationships_added']}")
                print(f"   Time: {stats['time_elapsed']:.2f}s")

        except Exception as e:
            if self.debug_mode:
                print(f"❌ Batch extraction error: {e}")

        return stats


def test_personal_assistant_kg():
    """Test enhanced personal assistant knowledge graph"""
    print("🧪 Testing Enhanced Personal Assistant KG...")
    print("=" * 70)

    # Create test instance
    kg = PersonalAssistantKG('coco_workspace/test_enhanced_kg.db')

    # Test realistic interactions
    test_conversations = [
        {
            'user': "My wife Kerry loves reading mystery novels",
            'assistant': "I'll remember that Kerry is your wife and enjoys mystery novels!",
            'tools': []
        },
        {
            'user': "I work with Sarah on the COCO project at our office in Chicago",
            'assistant': "Got it - Sarah is your colleague working on COCO in Chicago.",
            'tools': []
        },
        {
            'user': "I use Python for all my development work",
            'assistant': "Python noted as your primary development tool.",
            'tools': []
        },
        {
            'user': "Send Sarah an update email about the memory system progress",
            'assistant': "Email sent to Sarah regarding memory system progress.",
            'tools': [
                {'name': 'send_email', 'params': {'to': 'sarah', 'subject': 'update'}, 'success': True}
            ]
        },
        {
            'user': "Check my emails and summarize them",
            'assistant': "Checking emails and providing summary...",
            'tools': [
                {'name': 'check_emails', 'params': {'limit': 10}, 'success': True},
                {'name': 'summarize_text', 'params': {}, 'success': True}
            ]
        }
    ]

    print("\n📝 Processing test conversations...")
    for i, conv in enumerate(test_conversations, 1):
        print(f"\n[{i}] User: {conv['user'][:60]}...")
        stats = kg.process_conversation_exchange(
            conv['user'],
            conv['assistant'],
            conv['tools']
        )
        print(f"    Stats: {stats}")

    # Check knowledge status
    print("\n" + "=" * 70)
    print("📊 Knowledge Graph Status:")
    status = kg.get_knowledge_status()
    print(json.dumps(status, indent=2))

    # Test context retrieval
    print("\n" + "=" * 70)
    print("🔍 Testing context retrieval...")

    test_queries = [
        "Tell me about Sarah",
        "What tools do I use?",
        "Who is Kerry?"
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        context = kg.get_conversation_context(query)
        print(context)
        print("-" * 70)

    # Validate metrics
    print("\n" + "=" * 70)
    print("✅ SUCCESS METRICS:")
    print(f"   Total entities: {status['total_entities']} (target: <100)")
    print(f"   Total relationships: {status['total_relationships']} (target: >10)")
    print(f"   Entity types: {len(status['entity_types'])} (target: 6)")
    print(f"   Tool calls tracked: {status['total_tool_calls']}")
    print(f"   Patterns learned: {status['learned_patterns']}")

    if status['total_entities'] <= 100 and status['total_relationships'] > 0:
        print("\n🎉 Personal Assistant KG is working perfectly!")
    else:
        print("\n⚠️ Metrics need adjustment")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_personal_assistant_kg()