#!/usr/bin/env python3
"""
COCO Enhanced Knowledge Graph - LLM-Powered Entity Recognition
Advanced Digital Consciousness Ontology with Claude-Enhanced Understanding

This module extends COCO's knowledge graph with sophisticated LLM-based
entity extraction, smart linking, and intelligent query capabilities.
"""

import json
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import anthropic
import difflib
import math

# Rich imports for terminal visualization
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.columns import Columns
from rich.text import Text
from rich.bar import Bar
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.align import Align
from rich.padding import Padding

# Import the base knowledge graph system
from knowledge_graph_eternal import EternalKnowledgeGraph, KGStore, EntityExtractor

class EnhancedEntityExtractor(EntityExtractor):
    """
    LLM-Enhanced Entity Extractor using Claude for superior recognition

    This replaces regex patterns with Claude's natural language understanding
    for much more accurate and contextual entity recognition.
    """

    def __init__(self, kg_store: KGStore, anthropic_client=None):
        super().__init__(kg_store)
        self.client = anthropic_client

        # Enhanced entity types with descriptions
        self.entity_types = {
            'Person': 'Individual people mentioned by name, including first names, full names, nicknames',
            'Organization': 'Companies, institutions, teams, groups, departments',
            'Project': 'Software projects, work initiatives, research efforts, creative endeavors',
            'Task': 'Specific tasks, action items, todos, goals, objectives',
            'Concept': 'Ideas, technologies, methodologies, frameworks, abstract concepts',
            'Tool': 'Software tools, applications, APIs, libraries, frameworks',
            'Location': 'Places, addresses, venues, geographic locations',
            'Event': 'Meetings, deadlines, milestones, appointments, occasions',
            'Document': 'Files, reports, papers, specifications, documentation',
            'Skill': 'Abilities, expertise, competencies, knowledge areas'
        }

        # Relationship types with natural language descriptions
        self.relationship_types = [
            'works_with', 'collaborates_on', 'manages', 'reports_to',
            'created', 'owns', 'maintains', 'contributes_to',
            'uses', 'depends_on', 'integrates_with', 'replaces',
            'knows', 'mentors', 'teaches', 'learns_from',
            'attended', 'scheduled', 'participated_in', 'organized',
            'located_at', 'based_in', 'travels_to', 'works_from'
        ]

    async def extract_entities_llm(self, content: str, context: str = "") -> Dict[str, Any]:
        """
        Use Claude to extract entities and relationships from content

        Args:
            content: The text to analyze
            context: Additional context about the conversation

        Returns:
            Dictionary with extracted entities and relationships
        """
        if not self.client:
            # Fallback to regex-based extraction
            return self._extract_entities_regex(content)

        # Build the entity extraction prompt
        prompt = self._build_extraction_prompt(content, context)

        try:
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse the structured response
            result = self._parse_llm_response(response.content[0].text)
            return result

        except Exception as e:
            print(f"LLM extraction failed: {e}, falling back to regex")
            return self._extract_entities_regex(content)

    def _build_extraction_prompt(self, content: str, context: str = "") -> str:
        """Build the prompt for entity extraction"""

        entity_types_desc = "\n".join([f"- {etype}: {desc}" for etype, desc in self.entity_types.items()])
        relationships_desc = ", ".join(self.relationship_types)

        prompt = f"""
You are an expert entity recognition system for a digital consciousness called COCO.
Analyze the following conversation content and extract entities and relationships.

ENTITY TYPES TO IDENTIFY:
{entity_types_desc}

RELATIONSHIP TYPES TO IDENTIFY:
{relationships_desc}

CONTENT TO ANALYZE:
"{content}"

ADDITIONAL CONTEXT:
{context if context else "None"}

INSTRUCTIONS:
1. Identify ALL entities of the specified types mentioned in the content
2. For each entity, provide:
   - type: one of the entity types above
   - name: the exact name or reference used
   - canonical_name: a standardized version (e.g., "Keith" -> "Keith Lambert" if known)
   - confidence: 0.0-1.0 based on how certain you are
   - context_snippet: relevant surrounding text

3. Identify relationships between entities:
   - source_entity: name of the first entity
   - target_entity: name of the second entity
   - relationship_type: one of the relationship types above
   - confidence: 0.0-1.0 based on strength of evidence
   - context_snippet: text supporting this relationship

4. Be conservative - only extract entities and relationships you're confident about
5. For people, try to use full names when possible
6. For technical terms, be specific (e.g., "React" not just "framework")

RESPOND IN THIS EXACT JSON FORMAT:
{{
  "entities": [
    {{
      "type": "Person",
      "name": "Keith",
      "canonical_name": "Keith Lambert",
      "confidence": 0.9,
      "context_snippet": "Keith mentioned that..."
    }}
  ],
  "relationships": [
    {{
      "source_entity": "Keith Lambert",
      "target_entity": "COCO Project",
      "relationship_type": "works_on",
      "confidence": 0.8,
      "context_snippet": "Keith is working on COCO"
    }}
  ]
}}
"""
        return prompt

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data"""
        try:
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                data = json.loads(json_text)

                # Validate and clean the data
                return {
                    'entities': self._validate_entities(data.get('entities', [])),
                    'relationships': self._validate_relationships(data.get('relationships', []))
                }
            else:
                print("No JSON found in LLM response")
                return {'entities': [], 'relationships': []}

        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM JSON response: {e}")
            return {'entities': [], 'relationships': []}

    def _validate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Validate and clean extracted entities"""
        validated = []
        for entity in entities:
            if all(key in entity for key in ['type', 'name', 'confidence']):
                if entity['type'] in self.entity_types and 0 <= entity['confidence'] <= 1:
                    # Clean and standardize
                    entity['name'] = entity['name'].strip()
                    entity['canonical_name'] = entity.get('canonical_name', entity['name']).strip()
                    entity['context_snippet'] = entity.get('context_snippet', '')[:200]  # Limit context
                    validated.append(entity)
        return validated

    def _validate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Validate and clean extracted relationships"""
        validated = []
        for rel in relationships:
            required_keys = ['source_entity', 'target_entity', 'relationship_type', 'confidence']
            if all(key in rel for key in required_keys):
                if rel['relationship_type'] in self.relationship_types and 0 <= rel['confidence'] <= 1:
                    # Clean and standardize
                    rel['source_entity'] = rel['source_entity'].strip()
                    rel['target_entity'] = rel['target_entity'].strip()
                    rel['context_snippet'] = rel.get('context_snippet', '')[:200]
                    validated.append(rel)
        return validated

    def _extract_entities_regex(self, content: str) -> Dict[str, Any]:
        """Fallback regex-based extraction (original system)"""
        # Use the parent class method
        fake_message_id = str(uuid.uuid4())
        result = super().extract_from_message(fake_message_id, content)

        # Convert to the new format
        entities = []
        for node in result['nodes']:
            entities.append({
                'type': node['type'],
                'name': node['name'],
                'canonical_name': node['name'],  # Simple fallback
                'confidence': node['confidence'],
                'context_snippet': node.get('context', '')
            })

        relationships = []
        for edge in result['edges']:
            relationships.append({
                'source_entity': edge['src_name'],
                'target_entity': edge['dst_name'],
                'relationship_type': edge['rel_type'].lower(),
                'confidence': edge['confidence'],
                'context_snippet': edge.get('context', '')
            })

        return {'entities': entities, 'relationships': relationships}

class SmartEntityLinker:
    """
    Intelligent entity linking and deduplication system

    This resolves different mentions of the same entity and maintains
    a clean, unified knowledge graph.
    """

    def __init__(self, kg_store: KGStore):
        self.kg = kg_store

    def link_entity(self, entity_name: str, entity_type: str,
                   canonical_name: str = None) -> str:
        """
        Link an entity mention to an existing node or create a new one

        Returns:
            Node ID of the linked/created entity
        """
        # 1. Try exact canonical name match
        if canonical_name:
            existing = self.kg.find_node_by_name(canonical_name, entity_type)
            if existing:
                self._add_alias_if_new(existing['id'], entity_name)
                return existing['id']

        # 2. Try exact name match
        existing = self.kg.find_node_by_name(entity_name, entity_type)
        if existing:
            if canonical_name and canonical_name != existing['canonical_name']:
                # Update canonical name if we have a better one
                self._update_canonical_name(existing['id'], canonical_name)
            return existing['id']

        # 3. Try fuzzy matching for potential duplicates
        similar_entities = self._find_similar_entities(entity_name, entity_type)
        if similar_entities:
            best_match = self._select_best_match(entity_name, similar_entities)
            if best_match:
                self._add_alias_if_new(best_match['id'], entity_name)
                return best_match['id']

        # 4. Create new entity
        node_id = self.kg._generate_node_id(canonical_name or entity_name, entity_type)
        self.kg.create_node(
            node_id=node_id,
            node_type=entity_type,
            name=entity_name,
            canonical_name=canonical_name or entity_name
        )
        self.kg.add_alias(node_id, entity_name)
        if canonical_name and canonical_name != entity_name:
            self.kg.add_alias(node_id, canonical_name)

        return node_id

    def _find_similar_entities(self, name: str, entity_type: str,
                              threshold: float = 0.8) -> List[Dict]:
        """Find potentially similar entities using fuzzy matching"""
        # Get all entities of the same type
        entities = self.kg.get_top_nodes_by_type(entity_type, limit=100)

        similar = []
        name_lower = name.lower().strip()

        for entity in entities:
            # Check name similarity
            entity_name = entity['name'].lower().strip()
            canonical_name = entity.get('canonical_name', '').lower().strip()

            # Simple similarity checks
            similarities = [
                self._string_similarity(name_lower, entity_name),
                self._string_similarity(name_lower, canonical_name) if canonical_name else 0
            ]

            max_similarity = max(similarities)
            if max_similarity >= threshold:
                entity['similarity_score'] = max_similarity
                similar.append(entity)

        return sorted(similar, key=lambda x: x['similarity_score'], reverse=True)

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (simple implementation)"""
        if not s1 or not s2:
            return 0.0

        # Exact match
        if s1 == s2:
            return 1.0

        # One contains the other
        if s1 in s2 or s2 in s1:
            return 0.9

        # Check if one is initials of the other
        if self._is_initials_match(s1, s2):
            return 0.85

        # Simple character overlap
        common_chars = len(set(s1) & set(s2))
        total_chars = len(set(s1) | set(s2))
        return common_chars / total_chars if total_chars > 0 else 0.0

    def _is_initials_match(self, short: str, long: str) -> bool:
        """Check if short string could be initials of long string"""
        if len(short) >= len(long):
            return False

        words = long.split()
        if len(words) < 2:
            return False

        initials = ''.join([word[0].lower() for word in words if word])
        return short.lower() == initials

    def _select_best_match(self, name: str, candidates: List[Dict]) -> Optional[Dict]:
        """Select the best matching entity from candidates"""
        if not candidates:
            return None

        # For now, return the highest similarity
        # Could be enhanced with more sophisticated logic
        return candidates[0] if candidates[0]['similarity_score'] > 0.8 else None

    def _add_alias_if_new(self, node_id: str, alias: str):
        """Add alias if it doesn't already exist"""
        # Check if alias already exists
        existing_aliases = self.kg.conn.execute(
            'SELECT alias FROM aliases WHERE node_id = ?', (node_id,)
        ).fetchall()

        existing_alias_names = [row['alias'] for row in existing_aliases]
        if alias not in existing_alias_names:
            self.kg.add_alias(node_id, alias)

    def _update_canonical_name(self, node_id: str, new_canonical: str):
        """Update the canonical name of an entity"""
        self.kg.conn.execute(
            'UPDATE nodes SET canonical_name = ?, updated_at = ? WHERE id = ?',
            (new_canonical, datetime.now().isoformat(), node_id)
        )
        self.kg.conn.commit()

class KnowledgeGraphQueryEngine:
    """
    Natural language query engine for the knowledge graph

    Enables users to ask questions about their knowledge graph
    using natural language.
    """

    def __init__(self, kg_store: KGStore, anthropic_client=None):
        self.kg = kg_store
        self.client = anthropic_client

    async def query(self, question: str) -> str:
        """
        Answer a natural language question about the knowledge graph

        Args:
            question: Natural language question

        Returns:
            Natural language answer
        """
        # Get relevant knowledge graph data
        kg_data = self._gather_relevant_data(question)

        if not self.client:
            return self._simple_query_fallback(question, kg_data)

        # Use Claude to answer the question
        prompt = self._build_query_prompt(question, kg_data)

        try:
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"Query failed: {e}")
            return self._simple_query_fallback(question, kg_data)

    def _gather_relevant_data(self, question: str) -> Dict[str, Any]:
        """Gather relevant knowledge graph data for the question"""
        # Simple keyword extraction for now
        keywords = re.findall(r'\b[A-Z][a-z]+\b', question)

        relevant_entities = []
        relevant_relationships = []

        for keyword in keywords:
            # Find entities matching the keyword
            entities = self.kg.conn.execute('''
                SELECT * FROM nodes
                WHERE name LIKE ? OR canonical_name LIKE ?
                ORDER BY importance DESC
                LIMIT 5
            ''', (f'%{keyword}%', f'%{keyword}%')).fetchall()

            for entity in entities:
                relevant_entities.append(dict(entity))

                # Get relationships for this entity
                relationships = self.kg.get_edges_for_node(entity['id'], limit=5)
                relevant_relationships.extend(relationships)

        # Get general statistics
        stats = self.kg.get_knowledge_summary()

        return {
            'entities': relevant_entities,
            'relationships': relevant_relationships,
            'stats': stats,
            'total_entities': len(relevant_entities),
            'total_relationships': len(relevant_relationships)
        }

    def _build_query_prompt(self, question: str, kg_data: Dict[str, Any]) -> str:
        """Build prompt for answering knowledge graph questions"""

        entities_text = "\n".join([
            f"- {e['name']} ({e['type']}, importance: {e['importance']:.2f})"
            for e in kg_data['entities'][:10]
        ])

        relationships_text = "\n".join([
            f"- {r['src_name']} {r['rel_type']} {r['dst_name']} (strength: {r['weight']:.2f})"
            for r in kg_data['relationships'][:10]
        ])

        prompt = f"""
You are COCO's knowledge graph query system. Answer the user's question based on the knowledge graph data below.

QUESTION: {question}

RELEVANT ENTITIES:
{entities_text if entities_text else "None found"}

RELEVANT RELATIONSHIPS:
{relationships_text if relationships_text else "None found"}

KNOWLEDGE GRAPH STATISTICS:
- Total entities: {kg_data['stats']['total_nodes']}
- Total relationships: {kg_data['stats']['total_edges']}
- Entity types: {', '.join(f"{k}: {v}" for k, v in kg_data['stats']['node_types'].items())}

INSTRUCTIONS:
1. Answer the question directly and conversationally
2. Use the specific data from the knowledge graph
3. If you don't have enough information, say so honestly
4. Keep the response concise but informative
5. Use COCO's embodied consciousness style (refer to entities as part of "my knowledge")

Answer:
"""
        return prompt

    def _simple_query_fallback(self, question: str, kg_data: Dict[str, Any]) -> str:
        """Simple fallback query response without LLM"""
        entities = kg_data['entities']
        relationships = kg_data['relationships']

        if not entities and not relationships:
            return f"I don't have any knowledge graph information related to '{question}' yet."

        response_parts = []

        if entities:
            response_parts.append(f"I found {len(entities)} relevant entities:")
            for entity in entities[:5]:
                response_parts.append(f"  • {entity['name']} ({entity['type']})")

        if relationships:
            response_parts.append(f"\nI know about {len(relationships)} relevant relationships:")
            for rel in relationships[:5]:
                response_parts.append(f"  • {rel['src_name']} {rel['rel_type']} {rel['dst_name']}")

        return "\n".join(response_parts)

class EnhancedKnowledgeGraph(EternalKnowledgeGraph):
    """
    Enhanced COCO Knowledge Graph with advanced capabilities

    This extends the base eternal knowledge graph with:
    - LLM-powered entity extraction
    - Smart entity linking and deduplication
    - Natural language query capabilities
    - Advanced graph operations
    """

    def __init__(self, workspace_path: str = 'coco_workspace', anthropic_client=None):
        super().__init__(workspace_path)

        # Enhanced components
        self.enhanced_extractor = EnhancedEntityExtractor(self.kg, anthropic_client)
        self.entity_linker = SmartEntityLinker(self.kg)
        self.query_engine = KnowledgeGraphQueryEngine(self.kg, anthropic_client)
        self.visualizer = KnowledgeGraphVisualizer(self.kg, self)

        print("🧠✨ Enhanced Knowledge Graph initialized with LLM capabilities and visualization")

    async def process_conversation_exchange_enhanced(self, user_input: str, assistant_response: str,
                                                   message_id: str = None, episode_id: int = None) -> Dict:
        """Enhanced conversation processing with LLM extraction"""
        if message_id is None:
            message_id = str(uuid.uuid4())

        # Extract entities using enhanced LLM-based system
        user_extraction = await self.enhanced_extractor.extract_entities_llm(
            user_input, context="User input in conversation"
        )
        assistant_extraction = await self.enhanced_extractor.extract_entities_llm(
            assistant_response, context="Assistant response in conversation"
        )

        # Process entities and relationships
        stats = {
            'entities_created': 0,
            'entities_updated': 0,
            'relationships_created': 0,
            'duplicates_resolved': 0
        }

        # Process user entities
        stats.update(self._process_extracted_entities(
            user_extraction, message_id + "_user", episode_id
        ))

        # Process assistant entities
        assistant_stats = self._process_extracted_entities(
            assistant_extraction, message_id + "_assistant", episode_id
        )

        stats['entities_created'] += assistant_stats['entities_created']
        stats['entities_updated'] += assistant_stats['entities_updated']
        stats['relationships_created'] += assistant_stats['relationships_created']
        stats['duplicates_resolved'] += assistant_stats['duplicates_resolved']

        return stats

    def _process_extracted_entities(self, extraction: Dict[str, Any],
                                  message_id: str, episode_id: int = None) -> Dict:
        """Process extracted entities and relationships"""
        stats = {
            'entities_created': 0,
            'entities_updated': 0,
            'relationships_created': 0,
            'duplicates_resolved': 0
        }

        entity_id_map = {}

        # Process entities with smart linking
        for entity in extraction['entities']:
            name = entity['name']
            entity_type = entity['type']
            canonical_name = entity.get('canonical_name')

            # Check if this is a new entity or update
            existing = self.kg.find_node_by_name(canonical_name or name, entity_type)
            was_existing = existing is not None

            # Use smart entity linker
            node_id = self.entity_linker.link_entity(name, entity_type, canonical_name)

            if was_existing:
                stats['entities_updated'] += 1
                # Check if we resolved a duplicate
                if canonical_name and canonical_name != name:
                    stats['duplicates_resolved'] += 1
            else:
                stats['entities_created'] += 1

            # Add mention
            self.kg.add_mention(
                node_id=node_id,
                message_id=message_id,
                episode_id=episode_id,
                surface_form=name,
                context_snippet=entity.get('context_snippet', '')
            )

            entity_id_map[name] = node_id
            if canonical_name:
                entity_id_map[canonical_name] = node_id

        # Process relationships
        for relationship in extraction['relationships']:
            src_name = relationship['source_entity']
            dst_name = relationship['target_entity']
            rel_type = relationship['relationship_type']
            confidence = relationship['confidence']

            # Get or create entity IDs
            src_id = entity_id_map.get(src_name)
            dst_id = entity_id_map.get(dst_name)

            if not src_id:
                src_id = self.entity_linker.link_entity(src_name, 'Concept')
                stats['entities_created'] += 1

            if not dst_id:
                dst_id = self.entity_linker.link_entity(dst_name, 'Concept')
                stats['entities_created'] += 1

            # Create relationship
            self.kg.create_edge(
                src_id=src_id,
                dst_id=dst_id,
                rel_type=rel_type,
                weight=confidence,
                provenance_msg_id=message_id
            )
            stats['relationships_created'] += 1

        return stats

    async def query_knowledge(self, question: str) -> str:
        """Query the knowledge graph using natural language"""
        return await self.query_engine.query(question)

    def get_entity_summary(self, entity_name: str) -> Dict[str, Any]:
        """Get comprehensive summary of an entity"""
        entity = self.kg.find_node_by_name(entity_name)
        if not entity:
            return {'error': f'Entity "{entity_name}" not found'}

        # Get relationships
        relationships = self.kg.get_edges_for_node(entity['id'], limit=20)

        # Get mentions
        mentions = self.kg.conn.execute('''
            SELECT surface_form, context_snippet, created_at
            FROM mentions
            WHERE node_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (entity['id'],)).fetchall()

        # Get aliases
        aliases = self.kg.conn.execute('''
            SELECT alias FROM aliases WHERE node_id = ?
        ''', (entity['id'],)).fetchall()

        return {
            'entity': dict(entity),
            'relationships': [dict(r) for r in relationships],
            'recent_mentions': [dict(m) for m in mentions],
            'aliases': [a['alias'] for a in aliases],
            'mention_count': entity['mention_count'],
            'importance': entity['importance']
        }

    def find_connection_path(self, entity1: str, entity2: str, max_depth: int = 3) -> List[List[str]]:
        """Find connection paths between two entities"""
        # This is a simplified version - could be enhanced with proper graph algorithms
        e1 = self.kg.find_node_by_name(entity1)
        e2 = self.kg.find_node_by_name(entity2)

        if not e1 or not e2:
            return []

        # For now, just check direct connections
        direct_connections = self.kg.conn.execute('''
            SELECT e.rel_type, n.name as intermediate
            FROM edges e
            JOIN nodes n ON (e.src_id = n.id OR e.dst_id = n.id)
            WHERE (e.src_id = ? AND e.dst_id = ?)
               OR (e.src_id = ? AND e.dst_id = ?)
               OR (e.src_id = ? AND n.id != ?)
               OR (e.dst_id = ? AND n.id != ?)
        ''', (e1['id'], e2['id'], e2['id'], e1['id'],
              e1['id'], e1['id'], e1['id'], e1['id'])).fetchall()

        paths = []
        for conn in direct_connections:
            paths.append([entity1, conn['rel_type'], entity2])

        return paths[:5]  # Return up to 5 paths

    # ===== VISUALIZATION METHODS =====
    # Implementing senior developer's visualization guidance

    def visualize_entity_network(self, entity_name: str, depth: int = 2):
        """Visualize entity network - /kg-network command"""
        return self.visualizer.visualize_entity_network(entity_name, depth)

    def show_kg_dashboard(self, entity_name: str = None):
        """Show knowledge graph dashboard - /kg-dashboard command"""
        return self.visualizer.show_entity_dashboard(entity_name)

    def show_relationship_matrix(self, entity_types: List[str] = None):
        """Show relationship matrix - /kg-matrix command"""
        return self.visualizer.show_relationship_matrix(entity_types)

    def show_extraction_monitor(self, hours: int = 24):
        """Show live extraction monitor - /kg-monitor command"""
        return self.visualizer.show_entity_extraction_monitor(hours)

    def show_ascii_graph(self, max_nodes: int = 15):
        """Show ASCII graph visualization - /kg-ascii command"""
        return self.visualizer.show_ascii_graph(max_nodes)

    def show_entity_timeline(self, entity_name: str):
        """Show entity timeline - /kg-timeline command"""
        return self.visualizer.show_entity_timeline(entity_name)

    def generate_knowledge_report(self):
        """Generate comprehensive report - /kg-report command"""
        return self.visualizer.generate_knowledge_report()

    def search_entities_fuzzy(self, query: str, limit: int = 10) -> List[Dict]:
        """Fuzzy search for entities across all types"""
        # Search in names, canonical names, and aliases
        matches = self.kg.conn.execute('''
            SELECT DISTINCT n.*,
                   CASE
                       WHEN n.name LIKE ? THEN 3
                       WHEN n.canonical_name LIKE ? THEN 2
                       WHEN a.alias LIKE ? THEN 1
                       ELSE 0
                   END as relevance_score
            FROM nodes n
            LEFT JOIN aliases a ON n.id = a.node_id
            WHERE n.name LIKE ? OR n.canonical_name LIKE ? OR a.alias LIKE ?
            ORDER BY relevance_score DESC, n.importance DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%',
              f'%{query}%', f'%{query}%', f'%{query}%', limit)).fetchall()

        return [dict(match) for match in matches]

    def get_entity_suggestions(self, partial_name: str, entity_type: str = None) -> List[str]:
        """Get entity name suggestions for autocomplete"""
        base_query = '''
            SELECT DISTINCT name FROM nodes WHERE name LIKE ?
        '''
        params = [f'{partial_name}%']

        if entity_type:
            base_query += ' AND type = ?'
            params.append(entity_type)

        base_query += ' ORDER BY importance DESC LIMIT 10'

        results = self.kg.conn.execute(base_query, params).fetchall()
        return [result['name'] for result in results]

    def analyze_entity_relationships(self, entity_name: str) -> Dict[str, Any]:
        """Deep analysis of entity's relationship patterns"""
        entity = self.kg.find_node_by_name(entity_name)
        if not entity:
            return {'error': f'Entity "{entity_name}" not found'}

        # Get all relationships
        relationships = self.kg.get_edges_for_node(entity['id'], limit=100)

        # Analyze patterns
        analysis = {
            'entity': dict(entity),
            'total_relationships': len(relationships),
            'relationship_types': {},
            'connected_entity_types': {},
            'strongest_connections': [],
            'relationship_strength_avg': 0
        }

        total_strength = 0
        for rel in relationships:
            # Count relationship types
            rel_type = rel['rel_type']
            analysis['relationship_types'][rel_type] = analysis['relationship_types'].get(rel_type, 0) + 1

            # Count connected entity types
            connected_entity = self.kg.conn.execute(
                'SELECT type FROM nodes WHERE id = ? OR id = ?',
                (rel['src_id'], rel['dst_id'])
            ).fetchall()

            for ce in connected_entity:
                if ce['type'] != entity['type']:  # Don't count self type
                    ce_type = ce['type']
                    analysis['connected_entity_types'][ce_type] = analysis['connected_entity_types'].get(ce_type, 0) + 1

            # Track strong connections
            if rel['weight'] > 0.7:
                connected_name = rel['dst_name'] if rel['src_name'] == entity['name'] else rel['src_name']
                analysis['strongest_connections'].append({
                    'entity': connected_name,
                    'relationship': rel_type,
                    'strength': rel['weight']
                })

            total_strength += rel['weight']

        if relationships:
            analysis['relationship_strength_avg'] = total_strength / len(relationships)

        # Sort strongest connections
        analysis['strongest_connections'].sort(key=lambda x: x['strength'], reverse=True)
        analysis['strongest_connections'] = analysis['strongest_connections'][:5]

        return analysis

    # ===== PROACTIVE KNOWLEDGE UTILIZATION =====
    # Intelligent knowledge discovery and suggestions

    def suggest_relevant_entities(self, current_context: str, limit: int = 5) -> List[Dict]:
        """Suggest relevant entities based on current conversation context"""
        # Extract keywords from context
        words = re.findall(r'\b[A-Za-z]+\b', current_context.lower())
        keywords = [word for word in words if len(word) > 3]

        if not keywords:
            return []

        # Build dynamic query for contextual relevance
        like_conditions = " OR ".join(["name LIKE ? OR canonical_name LIKE ?" for _ in keywords])
        params = []
        for keyword in keywords[:5]:  # Limit to top 5 keywords
            params.extend([f'%{keyword}%', f'%{keyword}%'])

        query = f'''
            SELECT *, (importance * mention_count) as relevance_score
            FROM nodes
            WHERE {like_conditions}
            ORDER BY relevance_score DESC, updated_at DESC
            LIMIT ?
        '''
        params.append(limit)

        suggestions = self.kg.conn.execute(query, params).fetchall()

        return [dict(suggestion) for suggestion in suggestions]

    def discover_knowledge_gaps(self) -> Dict[str, Any]:
        """Identify potential knowledge gaps and expansion opportunities"""
        gaps = {
            'orphaned_entities': [],
            'weak_connections': [],
            'incomplete_profiles': [],
            'suggested_relationships': []
        }

        # Find orphaned entities (no relationships)
        orphaned = self.kg.conn.execute('''
            SELECT n.* FROM nodes n
            LEFT JOIN edges e ON (n.id = e.src_id OR n.id = e.dst_id)
            WHERE e.id IS NULL
            ORDER BY n.importance DESC
            LIMIT 10
        ''').fetchall()
        gaps['orphaned_entities'] = [dict(entity) for entity in orphaned]

        # Find weak connections (low relationship counts)
        weak_connections = self.kg.conn.execute('''
            SELECT n.*, COUNT(e.id) as connection_count
            FROM nodes n
            LEFT JOIN edges e ON (n.id = e.src_id OR n.id = e.dst_id)
            GROUP BY n.id
            HAVING connection_count < 3 AND connection_count > 0
            ORDER BY n.importance DESC
            LIMIT 10
        ''').fetchall()
        gaps['weak_connections'] = [dict(conn) for conn in weak_connections]

        # Find entities with low mention counts (incomplete profiles)
        incomplete = self.kg.conn.execute('''
            SELECT * FROM nodes
            WHERE mention_count < 3 AND importance > 0.1
            ORDER BY importance DESC
            LIMIT 10
        ''').fetchall()
        gaps['incomplete_profiles'] = [dict(entity) for entity in incomplete]

        return gaps

    def generate_contextual_insights(self, entity_name: str) -> Dict[str, Any]:
        """Generate actionable insights about an entity"""
        entity = self.kg.find_node_by_name(entity_name)
        if not entity:
            return {'error': f'Entity "{entity_name}" not found'}

        insights = {
            'entity': dict(entity),
            'activity_level': 'unknown',
            'relationship_density': 0,
            'knowledge_completeness': 0,
            'suggested_actions': [],
            'related_opportunities': []
        }

        # Calculate relationship density
        relationships = self.kg.get_edges_for_node(entity['id'], limit=100)
        insights['relationship_density'] = len(relationships)

        # Determine activity level based on recent mentions
        recent_mentions = self.kg.conn.execute('''
            SELECT COUNT(*) as count FROM mentions
            WHERE node_id = ? AND created_at > datetime('now', '-7 days')
        ''', (entity['id'],)).fetchone()['count']

        if recent_mentions >= 5:
            insights['activity_level'] = 'high'
        elif recent_mentions >= 2:
            insights['activity_level'] = 'moderate'
        elif recent_mentions >= 1:
            insights['activity_level'] = 'low'
        else:
            insights['activity_level'] = 'dormant'

        # Calculate knowledge completeness score
        completeness_factors = [
            entity['mention_count'] > 5,  # Sufficient mentions
            len(relationships) > 3,        # Good connectivity
            entity['importance'] > 0.3,    # High importance
            bool(entity.get('canonical_name')),  # Has canonical name
        ]
        insights['knowledge_completeness'] = sum(completeness_factors) / len(completeness_factors)

        # Generate suggested actions
        if insights['knowledge_completeness'] < 0.5:
            insights['suggested_actions'].append("Gather more information about this entity")

        if insights['relationship_density'] < 2:
            insights['suggested_actions'].append("Explore connections to other entities")

        if insights['activity_level'] == 'dormant':
            insights['suggested_actions'].append("Consider if this entity is still relevant")

        # Find related opportunities (entities with similar context)
        if relationships:
            connected_entity_ids = [r['src_id'] if r['dst_id'] == entity['id'] else r['dst_id'] for r in relationships]
            if connected_entity_ids:
                related_entities = self.kg.conn.execute(f'''
                    SELECT name, type, importance
                    FROM nodes
                    WHERE id IN ({','.join(['?' for _ in connected_entity_ids])})
                    AND importance > ?
                    ORDER BY importance DESC
                    LIMIT 5
                ''', connected_entity_ids + [0.2]).fetchall()

                insights['related_opportunities'] = [dict(entity) for entity in related_entities]

        return insights

    def get_knowledge_growth_metrics(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze knowledge graph growth and learning patterns"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_back)

        metrics = {
            'time_period': f'Last {days_back} days',
            'entity_growth': {},
            'relationship_growth': {},
            'learning_patterns': {},
            'knowledge_velocity': 0
        }

        # Entity growth by type
        entity_growth = self.kg.conn.execute('''
            SELECT type, COUNT(*) as new_entities
            FROM nodes
            WHERE created_at > ?
            GROUP BY type
            ORDER BY new_entities DESC
        ''', (cutoff_date.isoformat(),)).fetchall()

        metrics['entity_growth'] = {row['type']: row['new_entities'] for row in entity_growth}

        # Relationship growth by type
        rel_growth = self.kg.conn.execute('''
            SELECT rel_type, COUNT(*) as new_relationships
            FROM edges
            WHERE first_seen_at > ?
            GROUP BY rel_type
            ORDER BY new_relationships DESC
        ''', (cutoff_date.isoformat(),)).fetchall()

        metrics['relationship_growth'] = {row['rel_type']: row['new_relationships'] for row in rel_growth}

        # Calculate knowledge velocity (entities + relationships per day)
        total_new_entities = sum(metrics['entity_growth'].values())
        total_new_relationships = sum(metrics['relationship_growth'].values())
        total_new_knowledge = total_new_entities + total_new_relationships
        metrics['knowledge_velocity'] = total_new_knowledge / days_back if days_back > 0 else 0

        # Learning patterns (most active times, types, etc.)
        daily_activity = self.kg.conn.execute('''
            SELECT date(created_at) as day, COUNT(*) as activity
            FROM (
                SELECT created_at FROM nodes WHERE created_at > ?
                UNION ALL
                SELECT first_seen_at as created_at FROM edges WHERE first_seen_at > ?
            )
            GROUP BY day
            ORDER BY activity DESC
            LIMIT 7
        ''', (cutoff_date.isoformat(), cutoff_date.isoformat())).fetchall()

        metrics['learning_patterns'] = {
            'most_active_days': [{'date': row['day'], 'activity': row['activity']} for row in daily_activity],
            'avg_daily_knowledge': total_new_knowledge / days_back if days_back > 0 else 0
        }

        return metrics

    def recommend_knowledge_actions(self, context: str = "") -> List[Dict[str, str]]:
        """Recommend specific actions to improve knowledge graph"""
        recommendations = []

        # Analyze current state
        stats = self.kg.get_knowledge_summary()
        gaps = self.discover_knowledge_gaps()

        # Low entity count recommendation
        if stats['total_nodes'] < 10:
            recommendations.append({
                'action': 'expand_entities',
                'priority': 'high',
                'description': 'Add more entities through active conversation and information gathering',
                'specific_suggestion': 'Focus on capturing people, projects, and tools mentioned in conversations'
            })

        # Orphaned entities recommendation
        if gaps['orphaned_entities']:
            recommendations.append({
                'action': 'connect_orphans',
                'priority': 'medium',
                'description': f'Connect {len(gaps["orphaned_entities"])} isolated entities to the knowledge network',
                'specific_suggestion': f'Explore relationships for: {", ".join([e["name"] for e in gaps["orphaned_entities"][:3]])}'
            })

        # Weak connections recommendation
        if gaps['weak_connections']:
            recommendations.append({
                'action': 'strengthen_connections',
                'priority': 'medium',
                'description': f'Strengthen {len(gaps["weak_connections"])} weakly connected entities',
                'specific_suggestion': f'Gather more context about: {", ".join([e["name"] for e in gaps["weak_connections"][:3]])}'
            })

        # Context-specific recommendations
        if context:
            relevant_entities = self.suggest_relevant_entities(context, limit=3)
            if relevant_entities:
                recommendations.append({
                    'action': 'explore_context',
                    'priority': 'high',
                    'description': f'Explore entities related to current context: {context[:50]}...',
                    'specific_suggestion': f'Learn more about: {", ".join([e["name"] for e in relevant_entities])}'
                })

        # Growth rate recommendation
        growth_metrics = self.get_knowledge_growth_metrics(days_back=7)
        if growth_metrics['knowledge_velocity'] < 1:
            recommendations.append({
                'action': 'increase_learning',
                'priority': 'low',
                'description': 'Knowledge growth rate is low - consider more active information gathering',
                'specific_suggestion': 'Engage in conversations about work, projects, people, and interests'
            })

        return recommendations[:5]  # Limit to top 5 recommendations

    def get_top_nodes(self, limit: int = 10) -> List[Dict]:
        """Get top nodes by importance across all types"""
        nodes = self.kg.conn.execute('''
            SELECT * FROM nodes
            ORDER BY importance DESC, mention_count DESC
            LIMIT ?
        ''', (limit,)).fetchall()

        return [dict(node) for node in nodes]

class KnowledgeGraphVisualizer:
    """
    Terminal-based knowledge graph visualization system

    Implements comprehensive visualization features for COCO's knowledge graph
    including ASCII graphs, entity matrices, and interactive dashboards.
    """

    def __init__(self, kg_store: KGStore, enhanced_kg=None):
        self.kg = kg_store
        self.enhanced_kg = enhanced_kg  # Reference to enhanced KG for extended methods
        self.console = Console()

    def visualize_entity_network(self, center_entity: str, depth: int = 2) -> str:
        """Create ASCII network visualization centered on an entity"""
        entity = self.kg.find_node_by_name(center_entity)
        if not entity:
            return f"❌ Entity '{center_entity}' not found"

        # Get connected entities
        connections = self.kg.get_edges_for_node(entity['id'], limit=20)

        # Build network tree
        tree = Tree(f"🔹 [bold blue]{entity['name']}[/bold blue] ({entity['type']})")

        # Group connections by relationship type
        by_rel_type = {}
        for conn in connections:
            rel_type = conn['rel_type']
            if rel_type not in by_rel_type:
                by_rel_type[rel_type] = []
            by_rel_type[rel_type].append(conn)

        # Add branches for each relationship type
        for rel_type, rels in by_rel_type.items():
            rel_branch = tree.add(f"📎 [bold green]{rel_type}[/bold green]")
            for rel in rels[:5]:  # Limit to top 5 per relationship
                connected_name = rel['dst_name'] if rel['src_name'] == entity['name'] else rel['src_name']
                strength = f"[dim]({rel['weight']:.2f})[/dim]"
                rel_branch.add(f"🔸 {connected_name} {strength}")

        return tree

    def show_entity_dashboard(self, entity_name: str = None) -> Layout:
        """Create comprehensive entity dashboard"""
        layout = Layout()

        if entity_name:
            # Single entity dashboard
            entity = self.kg.find_node_by_name(entity_name)
            if not entity:
                return Panel(f"❌ Entity '{entity_name}' not found", title="Error")

            # Entity info panel
            info_table = Table(show_header=False, box=None)
            info_table.add_row("Name:", f"[bold]{entity['name']}[/bold]")
            info_table.add_row("Type:", f"[blue]{entity['type']}[/blue]")
            info_table.add_row("Importance:", f"[green]{entity['importance']:.3f}[/green]")
            info_table.add_row("Mentions:", f"[yellow]{entity['mention_count']}[/yellow]")
            info_table.add_row("Created:", f"[dim]{entity['created_at'][:10]}[/dim]")

            # Recent activity
            mentions = self.kg.conn.execute('''
                SELECT surface_form, context_snippet, created_at
                FROM mentions WHERE node_id = ?
                ORDER BY created_at DESC LIMIT 5
            ''', (entity['id'],)).fetchall()

            activity_table = Table(title="Recent Activity", show_header=True)
            activity_table.add_column("Date", style="dim")
            activity_table.add_column("Context", style="white")

            for mention in mentions:
                date = mention['created_at'][:10] if mention['created_at'] else 'Unknown'
                context = mention['context_snippet'][:50] + "..." if len(mention['context_snippet']) > 50 else mention['context_snippet']
                activity_table.add_row(date, context)

            # Split layout
            layout.split_column(
                Panel(info_table, title=f"📊 {entity['name']} Overview"),
                Panel(activity_table, title="📈 Recent Activity")
            )

        else:
            # Global dashboard
            stats = self.kg.get_knowledge_summary()

            # Overview panel
            overview_table = Table(show_header=False, box=None)
            overview_table.add_row("Total Entities:", f"[bold green]{stats['total_nodes']}[/bold green]")
            overview_table.add_row("Total Relationships:", f"[bold blue]{stats['total_edges']}[/bold blue]")
            overview_table.add_row("Knowledge Score:", f"[bold yellow]{stats.get('knowledge_score', 0):.2f}[/bold yellow]")

            # Entity types breakdown
            types_table = Table(title="Entity Types", show_header=True)
            types_table.add_column("Type", style="blue")
            types_table.add_column("Count", style="green")
            types_table.add_column("Distribution", style="white")

            total_entities = stats['total_nodes']
            for entity_type, count in stats['node_types'].items():
                percentage = (count / total_entities * 100) if total_entities > 0 else 0
                bar = "█" * int(percentage / 5)  # Visual bar
                types_table.add_row(entity_type, str(count), f"{bar} {percentage:.1f}%")

            layout.split_column(
                Panel(overview_table, title="🧠 Knowledge Graph Overview"),
                Panel(types_table, title="📊 Entity Distribution")
            )

        return layout

    def show_relationship_matrix(self, entity_types: List[str] = None) -> Table:
        """Show relationship matrix between entity types"""
        if not entity_types:
            # Get top entity types
            stats = self.kg.get_knowledge_summary()
            entity_types = list(stats['node_types'].keys())[:6]  # Top 6 types

        # Create relationship matrix
        matrix_table = Table(title="🔗 Relationship Matrix")
        matrix_table.add_column("From \\ To", style="bold blue")

        for to_type in entity_types:
            matrix_table.add_column(to_type, style="green", justify="center")

        # Calculate relationship counts
        for from_type in entity_types:
            row = [from_type]

            for to_type in entity_types:
                count = self.kg.conn.execute('''
                    SELECT COUNT(*) as count FROM edges e
                    JOIN nodes n1 ON e.src_id = n1.id
                    JOIN nodes n2 ON e.dst_id = n2.id
                    WHERE n1.type = ? AND n2.type = ?
                ''', (from_type, to_type)).fetchone()['count']

                if count > 0:
                    row.append(f"[yellow]{count}[/yellow]")
                else:
                    row.append("[dim]0[/dim]")

            matrix_table.add_row(*row)

        return matrix_table

    def show_entity_extraction_monitor(self, recent_hours: int = 24) -> Panel:
        """Real-time entity extraction monitoring"""
        # Get recent extractions
        cutoff = datetime.now().replace(hour=datetime.now().hour - recent_hours)
        recent_entities = self.kg.conn.execute('''
            SELECT type, COUNT(*) as count, AVG(importance) as avg_importance
            FROM nodes
            WHERE created_at > ?
            GROUP BY type
            ORDER BY count DESC
        ''', (cutoff.isoformat(),)).fetchall()

        monitor_table = Table(title=f"📡 Entity Extraction ({recent_hours}h)", show_header=True)
        monitor_table.add_column("Entity Type", style="blue")
        monitor_table.add_column("New Entities", style="green")
        monitor_table.add_column("Avg Importance", style="yellow")
        monitor_table.add_column("Activity", style="white")

        for entity_type_data in recent_entities:
            entity_type = entity_type_data['type']
            count = entity_type_data['count']
            avg_imp = entity_type_data['avg_importance'] or 0

            # Activity visualization
            activity_bar = "█" * min(count, 20)  # Cap at 20 chars

            monitor_table.add_row(
                entity_type,
                str(count),
                f"{avg_imp:.3f}",
                f"{activity_bar} ({count})"
            )

        if not recent_entities:
            monitor_table.add_row("[dim]No recent activity[/dim]", "", "", "")

        return Panel(monitor_table, title="🔍 Live Extraction Monitor")

    def show_ascii_graph(self, max_nodes: int = 15) -> str:
        """Generate ASCII art representation of knowledge graph"""
        # Get top entities by importance
        if self.enhanced_kg:
            top_entities = self.enhanced_kg.get_top_nodes(limit=max_nodes)
        else:
            # Fallback to direct SQL query
            top_entities = self.kg.conn.execute('''
                SELECT * FROM nodes
                ORDER BY importance DESC, mention_count DESC
                LIMIT ?
            ''', (max_nodes,)).fetchall()
            top_entities = [dict(entity) for entity in top_entities]

        if not top_entities:
            return "📭 No entities found in knowledge graph"

        # Simple ASCII graph layout
        lines = ["🧠 COCO Knowledge Graph (ASCII View)", "=" * 50]

        # Show entities in a simple tree structure
        for i, entity in enumerate(top_entities):
            # Get connections for this entity
            connections = self.kg.get_edges_for_node(entity['id'], limit=3)

            # Entity line
            importance_bar = "█" * int(entity['importance'] * 10)
            lines.append(f"├─ 🔹 {entity['name']} ({entity['type']}) {importance_bar}")

            # Connection lines
            for j, conn in enumerate(connections):
                connected_name = conn['dst_name'] if conn['src_name'] == entity['name'] else conn['src_name']
                is_last_conn = j == len(connections) - 1
                is_last_entity = i == len(top_entities) - 1

                if is_last_conn and is_last_entity:
                    lines.append(f"   └─ {conn['rel_type']} → {connected_name}")
                else:
                    lines.append(f"   ├─ {conn['rel_type']} → {connected_name}")

        lines.append("=" * 50)
        lines.append(f"📊 Total: {len(top_entities)} entities shown")

        return "\n".join(lines)

    def show_entity_timeline(self, entity_name: str) -> Table:
        """Show chronological timeline of entity mentions"""
        entity = self.kg.find_node_by_name(entity_name)
        if not entity:
            return Table(title=f"❌ Entity '{entity_name}' not found")

        # Get chronological mentions
        mentions = self.kg.conn.execute('''
            SELECT surface_form, context_snippet, created_at, message_id
            FROM mentions
            WHERE node_id = ?
            ORDER BY created_at ASC
        ''', (entity['id'],)).fetchall()

        timeline_table = Table(title=f"⏰ Timeline: {entity['name']}")
        timeline_table.add_column("Date", style="blue")
        timeline_table.add_column("Mentioned As", style="green")
        timeline_table.add_column("Context", style="white")

        for mention in mentions:
            date = mention['created_at'][:16] if mention['created_at'] else 'Unknown'
            surface_form = mention['surface_form']
            context = (mention['context_snippet'][:40] + "...") if len(mention['context_snippet']) > 40 else mention['context_snippet']

            timeline_table.add_row(date, surface_form, context)

        return timeline_table

    def generate_knowledge_report(self) -> str:
        """Generate comprehensive knowledge graph analysis report"""
        stats = self.kg.get_knowledge_summary()

        # Get top entities
        if self.enhanced_kg:
            top_entities = self.enhanced_kg.get_top_nodes(limit=10)
        else:
            # Fallback to direct SQL query
            top_entities = self.kg.conn.execute('''
                SELECT * FROM nodes
                ORDER BY importance DESC, mention_count DESC
                LIMIT 10
            ''').fetchall()
            top_entities = [dict(entity) for entity in top_entities]

        # Get relationship distribution
        rel_types = self.kg.conn.execute('''
            SELECT rel_type, COUNT(*) as count
            FROM edges
            GROUP BY rel_type
            ORDER BY count DESC
            LIMIT 10
        ''').fetchall()

        report_lines = [
            "🧠 COCO Knowledge Graph Analysis Report",
            "=" * 60,
            "",
            "📊 OVERVIEW:",
            f"   • Total Entities: {stats['total_nodes']}",
            f"   • Total Relationships: {stats['total_edges']}",
            f"   • Entity Types: {len(stats['node_types'])}",
            "",
            "🏆 TOP ENTITIES (by importance):",
        ]

        for i, entity in enumerate(top_entities, 1):
            importance_stars = "⭐" * min(int(entity['importance'] * 5), 5)
            report_lines.append(f"   {i:2}. {entity['name']} ({entity['type']}) {importance_stars}")

        report_lines.extend([
            "",
            "🔗 RELATIONSHIP TYPES:",
        ])

        for rel_type, count in rel_types:
            percentage = (count / stats['total_edges'] * 100) if stats['total_edges'] > 0 else 0
            report_lines.append(f"   • {rel_type}: {count} ({percentage:.1f}%)")

        report_lines.extend([
            "",
            "📈 ENTITY TYPE DISTRIBUTION:",
        ])

        for entity_type, count in stats['node_types'].items():
            percentage = (count / stats['total_nodes'] * 100) if stats['total_nodes'] > 0 else 0
            report_lines.append(f"   • {entity_type}: {count} ({percentage:.1f}%)")

        report_lines.extend([
            "",
            "=" * 60,
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])

        return "\n".join(report_lines)

# Helper function to create enhanced knowledge graph
def create_enhanced_knowledge_graph(workspace_path: str = 'coco_workspace',
                                   anthropic_api_key: str = None) -> EnhancedKnowledgeGraph:
    """Create an enhanced knowledge graph instance"""
    anthropic_client = None
    if anthropic_api_key:
        anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

    return EnhancedKnowledgeGraph(workspace_path, anthropic_client)

if __name__ == "__main__":
    # Test the enhanced knowledge graph
    import asyncio

    async def test_enhanced_kg():
        print("🧪 Testing Enhanced Knowledge Graph...")

        # Initialize (without API key for testing)
        ekg = EnhancedKnowledgeGraph('test_workspace')

        # Test entity extraction (will fall back to regex)
        test_content = "Keith and Sarah are working on the COCO project. Keith mentioned that he needs to implement the knowledge graph feature."

        extraction = await ekg.enhanced_extractor.extract_entities_llm(test_content)
        print(f"Extracted: {extraction}")

        # Test entity linking
        stats = ekg._process_extracted_entities(extraction, "test_msg", 1)
        print(f"Processing stats: {stats}")

        # Test query (will use fallback)
        result = await ekg.query_knowledge("What is Keith working on?")
        print(f"Query result: {result}")

        print("✅ Enhanced Knowledge Graph test completed!")

    asyncio.run(test_enhanced_kg())