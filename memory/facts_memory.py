"""
Facts Memory: Perfect Recall System for COCO

This module provides computer-perfect recall for:
- Commands (CLI, bash, COCO slash commands)
- Code snippets (Python, JavaScript, etc.)
- File operations (paths, CRUD)
- Decisions (user preferences, choices)
- URLs (web resources)
- Errors and solutions
- Configurations

Author: COCO Development Team
Date: October 24, 2025
Status: Phase 1 - Implementation
"""

import re
import json
import hashlib
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import os

class FactsMemory:
    """Perfect recall for specific items"""

    # Fact type definitions (Personal Assistant + Technical Support)
    FACT_TYPES = {
        # Personal Assistant Types (High Priority)
        'appointment': 'Meetings, events, calls, and scheduled items',
        'contact': 'People, email addresses, phone numbers, relationships',
        'preference': 'Personal preferences, likes, dislikes, and choices',
        'task': 'To-do items, action items, and reminders',
        'note': 'Important information to remember',
        'location': 'Places, addresses, venues, and directions',
        'recommendation': 'Suggestions and advice given by COCO or others',
        'routine': 'Daily habits, recurring activities, and patterns',
        'health': 'Health-related information, metrics, and activities',
        'financial': 'Budget items, expenses, and financial decisions',

        # Communication & Tools
        'communication': 'Emails, messages, calls: who, topic, outcome',
        'tool_use': 'COCO actions: docs created, emails sent, images generated',

        # Technical Support Types (Lower Priority)
        'command': 'Shell commands and CLI operations',
        'code': 'Code snippets and scripts',
        'file': 'File paths and operations',
        'url': 'URLs and web resources',
        'error': 'Errors and their solutions',
        'config': 'Configuration and settings'
    }

    def __init__(self, db_path: str):
        """
        Initialize Facts Memory

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for fact extraction (Personal Assistant + Technical)"""
        return {
            # === Personal Assistant Patterns (High Priority) ===

            # Appointments: meetings, events, calls, interviews
            'appointment': re.compile(
                r'(?:meeting|appointment|call|interview|event|conference)(?:\s+(?:with|at|on))?\s+(.+?)(?:\.|,|;|\n|$)',
                re.IGNORECASE
            ),

            # Tasks: todos, action items, reminders
            'task': re.compile(
                r'(?:todo|task|need to|should|must|have to|remember to|action item|followup)\s+(.+?)(?:\.|,|;|\n|$)',
                re.IGNORECASE
            ),

            # Contacts: people, email addresses, phone numbers
            'contact': re.compile(
                r'(?:email|call|contact|reach out to|talk to|meet with|spoke with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                re.MULTILINE
            ),

            # Notes: important information to remember
            'note': re.compile(
                r'(?:note|remember|important|don\'t forget|fyi|heads up):\s*(.+?)(?:\.|;|\n|$)',
                re.IGNORECASE
            ),

            # Locations: places, addresses, venues
            'location': re.compile(
                r'(?:at|in|near|on)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Building|Office|Restaurant|Cafe|Hotel))?)',
                re.MULTILINE
            ),

            # Preferences: likes, dislikes, choices (enhanced from decision)
            'preference': re.compile(
                r'(?:I |i )?(?:prefer|like|love|want|need|always|never|favorite|hate|dislike)\s+(.+?)(?:\.|,|;|\n|$)',
                re.IGNORECASE
            ),

            # Communications: emails, messages, calls (who, topic, outcome)
            # ENHANCED (Oct 25, 2025): Capture tool output formats like "Email sent successfully to"
            'communication': re.compile(
                r'(?:email|message|text|chat|call)(?:ed|ing)?\s+(?:to\s+)?(.+?)(?:\sabout\s+(.+?))?(?:\.|,|;|\n|$)|'
                r'(?:Email|Message)\s+(?:sent|delivered)\s+(?:successfully\s+)?to\s+(.+?)(?:\n|$)',
                re.IGNORECASE | re.MULTILINE
            ),

            # === Communication & Tools ===

            # Tool uses (from COCO's function calling)
            # ENHANCED (Oct 25, 2025): Capture actual tool execution formats
            'tool_use': re.compile(
                r'(?:✅|✓)?\s*(?:\*\*)?(Email|Document|Image|Video|Spreadsheet)\s+(?:sent|created|generated|uploaded)\s+(?:successfully|to)\s+(.+?)(?:\n|$)|'
                r'(?:called|using|executed|created|generated|sent|uploaded)\s+(\w+)\s+(?:tool|document|email|image|video)',
                re.IGNORECASE | re.MULTILINE
            ),

            # URLs (useful for shared resources)
            'url': re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),

            # === Technical Support Patterns (Lower Priority) ===

            # Shell commands (lines starting with $)
            'command': re.compile(r'(?:^|\n)\$\s*(.+?)(?:\n|$)', re.MULTILINE),

            # Code blocks with optional language
            'code': re.compile(r'```(?:(\w+))?\n(.*?)```', re.DOTALL),

            # File paths (Unix/Mac style)
            'file': re.compile(r'(?:/[\w\-\.]+)+(?:\.\w+)?'),

            # Errors
            'error': re.compile(r'(?:Error|Exception|Failed|WARNING):\s*(.+?)(?:\n|$)', re.IGNORECASE),
        }

    def extract_facts(self, exchange: Dict) -> List[Dict]:
        """
        Extract all facts from an exchange (Personal Assistant + Technical)

        Args:
            exchange: Dict with 'user', 'agent', optional 'timestamp'

        Returns:
            List of extracted facts
        """
        facts = []

        # Combine user input and agent response
        user_text = exchange.get('user', '')
        agent_text = exchange.get('agent', '')
        full_text = f"{user_text}\n{agent_text}"

        # === Personal Assistant Fact Extraction (High Priority) ===

        # Extract appointments
        for match in self.patterns['appointment'].finditer(full_text):
            appointment = match.group(1).strip()
            if len(appointment) > 5:
                facts.append({
                    'type': 'appointment',
                    'content': appointment,
                    'context': self._get_context(full_text, match.span()),
                    'importance': self._calculate_importance('appointment', appointment)
                })

        # Extract tasks
        for match in self.patterns['task'].finditer(user_text):
            task = match.group(1).strip()
            if len(task) > 5:
                facts.append({
                    'type': 'task',
                    'content': task,
                    'context': self._get_context(user_text, match.span()),
                    'importance': self._calculate_importance('task', task)
                })

        # Extract contacts
        for match in self.patterns['contact'].finditer(full_text):
            contact = match.group(1).strip()
            if len(contact) > 2:  # At least first name
                facts.append({
                    'type': 'contact',
                    'content': contact,
                    'context': self._get_context(full_text, match.span()),
                    'importance': self._calculate_importance('contact', contact)
                })

        # Extract notes
        for match in self.patterns['note'].finditer(full_text):
            note = match.group(1).strip()
            if len(note) > 5:
                facts.append({
                    'type': 'note',
                    'content': note,
                    'context': self._get_context(full_text, match.span()),
                    'importance': self._calculate_importance('note', note)
                })

        # Extract locations
        for match in self.patterns['location'].finditer(full_text):
            location = match.group(1).strip()
            if len(location) > 3:
                facts.append({
                    'type': 'location',
                    'content': location,
                    'context': self._get_context(full_text, match.span()),
                    'importance': self._calculate_importance('location', location)
                })

        # Extract preferences (enhanced from decision)
        for match in self.patterns['preference'].finditer(user_text):
            preference = match.group(1).strip()
            if len(preference) > 5:
                facts.append({
                    'type': 'preference',
                    'content': preference,
                    'context': self._get_context(user_text, match.span()),
                    'importance': self._calculate_importance('preference', preference)
                })

        # Extract communications
        for match in self.patterns['communication'].finditer(full_text):
            communication = match.group(0).strip()
            if len(communication) > 10:
                facts.append({
                    'type': 'communication',
                    'content': communication,
                    'context': self._get_context(full_text, match.span()),
                    'importance': self._calculate_importance('communication', communication)
                })

        # === Explicit Email Extraction (CRITICAL FIX - Oct 25, 2025) ===
        # Extract email sending explicitly from tool execution results
        # Captures: "✅ Email successfully sent to mom@example.com"
        email_sent_pattern = re.compile(
            r'(?:✅|✓)?\s*(?:\*\*)?Email\s+(?:sent|delivered)\s+(?:successfully\s+)?(?:to\s+)?(.+?)(?:\n|$)',
            re.IGNORECASE
        )

        for match in email_sent_pattern.finditer(agent_text):
            recipient = match.group(1).strip()
            # Clean up recipient (remove markdown formatting)
            recipient_clean = re.sub(r'\*\*|__|~~', '', recipient)

            # Extract just email or name (before any extra text)
            recipient_parts = recipient_clean.split()
            if recipient_parts:
                recipient_final = recipient_parts[0]  # First word/email

                facts.append({
                    'type': 'communication',
                    'content': f"Email sent to {recipient_final}",
                    'context': self._get_context(agent_text, match.span()),
                    'importance': 0.9  # High importance for sent communications
                })

        # === Communication & Tools ===

        # Extract tool uses (COCO actions)
        for match in self.patterns['tool_use'].finditer(agent_text):
            tool_use = match.group(0).strip()
            if len(tool_use) > 5:
                facts.append({
                    'type': 'tool_use',
                    'content': tool_use,
                    'context': self._get_context(agent_text, match.span()),
                    'importance': self._calculate_importance('tool_use', tool_use)
                })

        # Extract URLs (useful for shared resources)
        for match in self.patterns['url'].finditer(full_text):
            url = match.group(0)
            facts.append({
                'type': 'url',
                'content': url,
                'context': self._get_context(full_text, match.span(), window=50),
                'importance': self._calculate_importance('url', url)
            })

        # === Technical Support Fact Extraction (Lower Priority) ===

        # Extract shell commands (deprioritized)
        for match in self.patterns['command'].finditer(full_text):
            command = match.group(1).strip()
            if len(command) > 3:
                facts.append({
                    'type': 'command',
                    'content': command,
                    'context': self._get_context(full_text, match.span()),
                    'importance': self._calculate_importance('command', command)
                })

        # Extract code blocks (deprioritized)
        for match in self.patterns['code'].finditer(full_text):
            language = match.group(1) or 'unknown'
            code = match.group(2).strip()
            if len(code) > 10:
                facts.append({
                    'type': 'code',
                    'content': code,
                    'context': self._get_context(full_text, match.span()),
                    'importance': self._calculate_importance('code', code),
                    'metadata': {'language': language}
                })

        # Extract file operations (deprioritized)
        file_matches = self.patterns['file'].finditer(full_text)
        for match in file_matches:
            file_path = match.group(0)
            if not self._is_likely_filepath(file_path):
                continue
            facts.append({
                'type': 'file',
                'content': file_path,
                'context': self._get_context(full_text, match.span(), window=50),
                'importance': self._calculate_importance('file', file_path)
            })

        # Extract errors (deprioritized)
        for match in self.patterns['error'].finditer(full_text):
            error_text = match.group(0).strip()
            if len(error_text) > 10:
                facts.append({
                    'type': 'error',
                    'content': error_text,
                    'context': self._get_context(full_text, match.span()),
                    'importance': self._calculate_importance('error', error_text)
                })

        return facts

    def _get_context(self, text: str, span: Tuple[int, int], window: int = 100) -> str:
        """Get surrounding context for a fact"""
        start = max(0, span[0] - window)
        end = min(len(text), span[1] + window)
        context = text[start:end]

        # Truncate if too long
        if len(context) > 500:
            context = context[:500] + "..."

        return context

    def _is_likely_filepath(self, path: str) -> bool:
        """Filter out false positive file paths"""
        # Skip if looks like URL
        if path.startswith('http://') or path.startswith('https://'):
            return False

        # Skip if too short
        if len(path) < 5:
            return False

        # Skip common false positives
        false_positives = ['//', '/.', '/etc/']
        if any(fp in path for fp in false_positives):
            return False

        return True

    def _calculate_importance(self, fact_type: str, content: str) -> float:
        """Calculate importance score (0-1) - Personal Assistant Focused"""
        # Base importance by type (Personal Assistant > Communication > Technical)
        type_weights = {
            # Personal Assistant Types (High Priority: 0.6-0.8)
            'appointment': 0.8,
            'contact': 0.7,
            'preference': 0.7,
            'task': 0.8,
            'note': 0.7,
            'location': 0.6,
            'recommendation': 0.7,
            'routine': 0.6,
            'health': 0.8,
            'financial': 0.8,

            # Communication & Tools (Medium Priority: 0.7-0.8)
            'communication': 0.8,
            'tool_use': 0.7,

            # Technical Support Types (Lower Priority: 0.3-0.5)
            'command': 0.3,
            'code': 0.4,
            'file': 0.3,
            'url': 0.5,
            'error': 0.5,
            'config': 0.4,
        }

        importance = type_weights.get(fact_type, 0.5)

        # Boost for temporal urgency (personal assistant priority)
        temporal_keywords = ['today', 'tomorrow', 'urgent', 'asap', 'now', 'immediately', 'deadline']
        if any(kw in content.lower() for kw in temporal_keywords):
            importance = min(1.0, importance + 0.2)

        # Boost for importance indicators (reduced from 0.2 to 0.1)
        critical_keywords = ['critical', 'important', 'must', 'required', 'vital', 'essential']
        if any(kw in content.lower() for kw in critical_keywords):
            importance = min(1.0, importance + 0.1)

        # Boost for user emphasis
        if '!' in content or content.isupper():
            importance = min(1.0, importance + 0.1)

        return importance

    def _generate_tags(self, fact: Dict) -> List[str]:
        """Auto-generate tags for a fact"""
        tags = [fact['type']]

        content_lower = fact['content'].lower()

        # Language tags for code
        if fact['type'] == 'code':
            if 'metadata' in fact and 'language' in fact['metadata']:
                tags.append(fact['metadata']['language'])

        # Technology tags
        tech_keywords = {
            'docker': ['docker', 'container'],
            'python': ['python', 'py', 'pip'],
            'javascript': ['javascript', 'js', 'npm', 'node'],
            'git': ['git', 'commit', 'push', 'pull'],
            'database': ['database', 'sql', 'postgres', 'sqlite'],
        }

        for tag, keywords in tech_keywords.items():
            if any(kw in content_lower for kw in keywords):
                tags.append(tag)

        return tags

    def _generate_embedding(self, text: str) -> str:
        """
        Generate hash-based embedding for semantic search

        Uses MD5 hash of normalized text (simple but effective for exact/fuzzy matching)
        Can be upgraded to OpenAI embeddings later if needed
        """
        # Normalize text
        normalized = text.lower().strip()

        # Generate hash
        hash_obj = hashlib.md5(normalized.encode())

        return hash_obj.hexdigest()

    def store_facts(self, facts: List[Dict], episode_id: int, session_id: int = None) -> int:
        """
        Store extracted facts in database

        Args:
            facts: List of fact dictionaries
            episode_id: Episode ID from episodes table
            session_id: Optional session ID

        Returns:
            Number of facts stored
        """
        cursor = self.conn.cursor()
        stored_count = 0

        for fact in facts:
            try:
                # Generate embedding
                embedding = self._generate_embedding(fact['content'])

                # Generate tags
                tags = self._generate_tags(fact)
                tags_json = json.dumps(tags)

                # Prepare metadata
                metadata = fact.get('metadata', {})
                metadata_json = json.dumps(metadata)

                # Insert fact
                cursor.execute("""
                    INSERT INTO facts (
                        fact_type, content, context, session_id, episode_id,
                        timestamp, embedding, tags, importance, metadata
                    ) VALUES (?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?)
                """, (
                    fact['type'],
                    fact['content'],
                    fact.get('context', ''),
                    session_id,
                    episode_id,
                    embedding,
                    tags_json,
                    fact.get('importance', 0.5),
                    metadata_json
                ))

                stored_count += 1

            except Exception as e:
                print(f"Warning: Failed to store fact: {e}")
                continue

        self.conn.commit()
        return stored_count

    def search_facts(
        self,
        query: str,
        fact_type: Optional[str] = None,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> List[Dict]:
        """
        Search facts with optional type filtering

        Args:
            query: Search query
            fact_type: Optional fact type filter
            limit: Maximum results
            min_importance: Minimum importance score

        Returns:
            List of matching facts
        """
        cursor = self.conn.cursor()

        # Build SQL query
        sql = """
            SELECT
                id, fact_type, content, context, timestamp,
                tags, importance, access_count, metadata
            FROM facts
            WHERE importance >= ?
        """

        params = [min_importance]

        # Add type filter
        if fact_type:
            sql += " AND fact_type = ?"
            params.append(fact_type)

        # Add search filter
        if query:
            sql += " AND (content LIKE ? OR context LIKE ?)"
            search_pattern = f"%{query}%"
            params.extend([search_pattern, search_pattern])

        # Order by importance and recency
        sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        # Convert to dict list
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'type': row[1],
                'content': row[2],
                'context': row[3],
                'timestamp': row[4],
                'tags': json.loads(row[5]) if row[5] else [],
                'importance': row[6],
                'access_count': row[7],
                'metadata': json.loads(row[8]) if row[8] else {}
            })

        # Update access counts
        if results:
            fact_ids = [r['id'] for r in results]
            placeholders = ','.join('?' * len(fact_ids))
            cursor.execute(f"""
                UPDATE facts
                SET access_count = access_count + 1,
                    last_accessed = datetime('now')
                WHERE id IN ({placeholders})
            """, fact_ids)
            self.conn.commit()

        return results

    def get_stats(self) -> Dict:
        """Get facts database statistics"""
        cursor = self.conn.cursor()

        # Total facts
        cursor.execute("SELECT COUNT(*) FROM facts")
        total_facts = cursor.fetchone()[0]

        # Breakdown by type
        cursor.execute("""
            SELECT fact_type, COUNT(*) as count
            FROM facts
            GROUP BY fact_type
            ORDER BY count DESC
        """)
        type_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

        # Average importance
        cursor.execute("SELECT AVG(importance) FROM facts")
        avg_importance = cursor.fetchone()[0] or 0.0

        # Most accessed facts
        cursor.execute("""
            SELECT fact_type, content, access_count
            FROM facts
            ORDER BY access_count DESC
            LIMIT 5
        """)
        most_accessed = [
            {'type': row[0], 'content': row[1][:50] + '...', 'count': row[2]}
            for row in cursor.fetchall()
        ]

        # Latest facts
        cursor.execute("""
            SELECT fact_type, timestamp
            FROM facts
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        latest = cursor.fetchone()
        latest_timestamp = latest[1] if latest else None

        return {
            'total_facts': total_facts,
            'breakdown': type_breakdown,
            'avg_importance': float(avg_importance),
            'most_accessed': most_accessed,
            'latest_timestamp': latest_timestamp
        }

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Convenience function for easy integration
def create_facts_memory(db_path: str = None) -> FactsMemory:
    """
    Create FactsMemory instance with default database path

    Args:
        db_path: Optional custom database path

    Returns:
        FactsMemory instance
    """
    if db_path is None:
        db_path = os.path.join('coco_workspace', 'coco_memory.db')

    return FactsMemory(db_path)
