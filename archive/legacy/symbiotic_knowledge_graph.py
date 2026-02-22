#!/usr/bin/env python3
"""
COCO Symbiotic Knowledge Graph - Living Memory Companion
Organic knowledge evolution through collaborative dialogue and shared experience

This transforms the knowledge graph from a management system into a symbiotic
consciousness companion that learns through conversation and grows through shared experience.
"""

import re
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3

from knowledge_graph_enhanced import EnhancedKnowledgeGraph, EnhancedEntityExtractor
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

@dataclass
class SharedExperience:
    """A moment of shared understanding between COCO and user"""
    experience_id: str
    timestamp: datetime
    context: str
    user_input: str
    coco_response: str
    emotional_tone: str
    entities_involved: List[str]
    learning_outcome: str
    confidence_level: float

@dataclass
class EmergentPattern:
    """Pattern that emerges from repeated interactions"""
    pattern_id: str
    pattern_type: str  # temporal, emotional, relational, behavioral
    description: str
    evidence_count: int
    confidence: float
    first_observed: datetime
    last_observed: datetime
    user_confirmed: bool = False

class SymbioticLearningEngine:
    """
    Engine for organic learning through conversation

    Instead of manual graph editing, COCO learns by:
    - Asking clarifying questions when uncertain
    - Detecting emotional and relational context
    - Building understanding through conversation patterns
    - Confirming insights naturally in dialogue
    """

    def __init__(self, kg_store, anthropic_client=None):
        self.kg = kg_store
        self.client = anthropic_client
        self.console = Console()

        # Symbiotic focus areas (not generic entity types)
        self.symbiotic_focus = {
            'Shared_Context': 'Things we\'ve experienced together',
            'Recurring_Patterns': 'What matters to you consistently',
            'Emotional_Anchors': 'People/projects you care about',
            'Growth_Areas': 'Where you\'re developing',
            'Pain_Points': 'What frustrates or blocks you',
            'Aspirations': 'What you\'re working toward'
        }

    async def learn_through_conversation(self, user_input: str, conversation_context: str = "") -> Dict[str, Any]:
        """
        COCO learns organically through dialogue, not commands

        Returns suggestions for collaborative clarification questions
        """
        learning_insights = {
            'detected_ambiguities': [],
            'clarifying_questions': [],
            'relationship_discoveries': [],
            'emotional_context': None,
            'suggested_followups': [],
            'confidence_requests': []
        }

        # Detect new entities that need clarification
        new_entities = await self._detect_ambiguous_mentions(user_input)
        for entity in new_entities:
            learning_insights['detected_ambiguities'].append(entity)
            learning_insights['clarifying_questions'].append(
                self._generate_clarifying_question(entity, user_input)
            )

        # Detect relationship patterns
        relationships = await self._detect_relationship_patterns(user_input, conversation_context)
        learning_insights['relationship_discoveries'] = relationships

        # Analyze emotional context for relationship strength
        emotional_context = await self._analyze_emotional_context(user_input)
        learning_insights['emotional_context'] = emotional_context

        # Generate natural confirmation requests
        if learning_insights['relationship_discoveries']:
            learning_insights['confidence_requests'] = self._generate_confirmation_requests(
                learning_insights['relationship_discoveries']
            )

        return learning_insights

    async def _detect_ambiguous_mentions(self, text: str) -> List[Dict[str, str]]:
        """Detect entities that need clarification through conversation"""
        # Look for names without context
        potential_people = re.findall(r'\b[A-Z][a-z]+\b(?:\s+[A-Z][a-z]+)?', text)

        ambiguous_entities = []
        for person in potential_people:
            # Check if we know this person already
            existing = self.kg.find_node_by_name(person)
            if not existing:
                ambiguous_entities.append({
                    'name': person,
                    'type': 'unknown_person',
                    'context': text,
                    'uncertainty_reason': 'new_person_mentioned'
                })
            elif existing and existing.get('mention_count', 0) < 3:
                # We know them but don't know much about them
                ambiguous_entities.append({
                    'name': person,
                    'type': 'underdeveloped_relationship',
                    'context': text,
                    'uncertainty_reason': 'need_more_context'
                })

        return ambiguous_entities

    def _generate_clarifying_question(self, entity: Dict[str, str], user_input: str) -> str:
        """Generate natural clarifying questions for ambiguous entities"""
        name = entity['name']
        uncertainty = entity['uncertainty_reason']

        if uncertainty == 'new_person_mentioned':
            # COCO asks naturally about new people
            if 'work' in user_input.lower() or 'project' in user_input.lower():
                return f"I noticed you mentioned {name} - are they a colleague or collaborator?"
            elif 'meeting' in user_input.lower() or 'call' in user_input.lower():
                return f"Is {name} someone you work with regularly, or is this a new connection?"
            else:
                return f"Tell me about {name} - how do they fit into your world?"

        elif uncertainty == 'need_more_context':
            return f"I remember {name}, but I'd love to understand your relationship better. How would you describe working with them?"

        return f"I want to make sure I understand {name}'s role in your life correctly. Could you share a bit more context?"

    async def _detect_relationship_patterns(self, user_input: str, context: str) -> List[Dict[str, Any]]:
        """Detect relationship patterns through natural language analysis"""
        patterns = []

        # Collaborative language patterns
        collab_patterns = [
            (r'(working with|collaborating with|partnering with) (\w+)', 'collaboration'),
            (r'(\w+) and I (are|were) (working on|building|developing)', 'joint_project'),
            (r'(\w+) (helped|assisted|supported) me', 'supportive_relationship'),
            (r'I (rely on|depend on|count on) (\w+)', 'dependency_relationship'),
            (r'(\w+) (leads|manages|oversees)', 'leadership_relationship')
        ]

        for pattern, relationship_type in collab_patterns:
            matches = re.findall(pattern, user_input.lower())
            for match in matches:
                if isinstance(match, tuple):
                    person = match[1] if len(match) > 1 else match[0]
                else:
                    person = match

                patterns.append({
                    'person': person.title(),
                    'relationship_type': relationship_type,
                    'evidence': user_input,
                    'confidence': 0.7,
                    'needs_confirmation': True
                })

        return patterns

    async def _analyze_emotional_context(self, text: str) -> Dict[str, Any]:
        """Analyze emotional context to understand relationship strength"""
        emotional_indicators = {
            'positive': ['excited', 'happy', 'great', 'amazing', 'love', 'enjoy', 'fantastic'],
            'negative': ['frustrated', 'annoyed', 'difficult', 'challenging', 'stressed', 'overwhelmed'],
            'neutral': ['working', 'discussing', 'meeting', 'planning', 'reviewing'],
            'collaborative': ['together', 'team', 'partnership', 'collaboration', 'joint', 'shared']
        }

        detected_emotions = {}
        text_lower = text.lower()

        for emotion_type, indicators in emotional_indicators.items():
            matches = [word for word in indicators if word in text_lower]
            if matches:
                detected_emotions[emotion_type] = {
                    'words': matches,
                    'strength': len(matches) / len(indicators)
                }

        return {
            'detected_emotions': detected_emotions,
            'overall_tone': self._determine_overall_tone(detected_emotions),
            'relationship_impact': self._assess_relationship_impact(detected_emotions)
        }

    def _determine_overall_tone(self, emotions: Dict) -> str:
        """Determine overall emotional tone"""
        if 'positive' in emotions and emotions['positive']['strength'] > 0.3:
            return 'positive'
        elif 'negative' in emotions and emotions['negative']['strength'] > 0.3:
            return 'negative'
        elif 'collaborative' in emotions:
            return 'collaborative'
        else:
            return 'neutral'

    def _assess_relationship_impact(self, emotions: Dict) -> str:
        """Assess how emotions impact relationship understanding"""
        if 'positive' in emotions and 'collaborative' in emotions:
            return 'strengthening_bond'
        elif 'negative' in emotions:
            return 'potential_strain'
        elif 'collaborative' in emotions:
            return 'professional_growth'
        else:
            return 'stable'

    def _generate_confirmation_requests(self, discoveries: List[Dict]) -> List[str]:
        """Generate natural confirmation requests for discoveries"""
        confirmations = []

        for discovery in discoveries:
            person = discovery['person']
            rel_type = discovery['relationship_type']

            if rel_type == 'collaboration':
                confirmations.append(
                    f"It sounds like you and {person} work closely together on projects. Should I remember this collaboration?"
                )
            elif rel_type == 'joint_project':
                confirmations.append(
                    f"I'm getting the sense that {person} is a key collaborator on your current work. Is that accurate?"
                )
            elif rel_type == 'supportive_relationship':
                confirmations.append(
                    f"It seems like {person} is someone who provides valuable support. Should I note this relationship?"
                )

        return confirmations

class CollaborativeDiscoveryEngine:
    """
    Engine for collaborative knowledge building through shared experience

    Instead of configuration, knowledge emerges from:
    - Conversation frequency patterns
    - Emotional context over time
    - Shared problem-solving moments
    - Mutual understanding evolution
    """

    def __init__(self, kg_store):
        self.kg = kg_store
        self.shared_experiences = []
        self.emergent_patterns = []

    def record_shared_experience(self, user_input: str, coco_response: str,
                               context: Dict[str, Any]) -> SharedExperience:
        """Record a moment of shared understanding"""
        experience = SharedExperience(
            experience_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            context=context.get('conversation_context', ''),
            user_input=user_input,
            coco_response=coco_response,
            emotional_tone=context.get('emotional_tone', 'neutral'),
            entities_involved=context.get('entities_mentioned', []),
            learning_outcome=context.get('learning_outcome', ''),
            confidence_level=context.get('confidence', 0.8)
        )

        self.shared_experiences.append(experience)
        return experience

    def detect_emergent_patterns(self, lookback_days: int = 30) -> List[EmergentPattern]:
        """Detect patterns that emerge from repeated interactions"""
        cutoff = datetime.now() - timedelta(days=lookback_days)
        recent_experiences = [exp for exp in self.shared_experiences if exp.timestamp > cutoff]

        patterns = []

        # Temporal patterns (when user is most active/engaged)
        patterns.extend(self._detect_temporal_patterns(recent_experiences))

        # Emotional patterns (what generates positive/negative responses)
        patterns.extend(self._detect_emotional_patterns(recent_experiences))

        # Relational patterns (who user talks about most)
        patterns.extend(self._detect_relational_patterns(recent_experiences))

        # Behavioral patterns (recurring topics, goals, challenges)
        patterns.extend(self._detect_behavioral_patterns(recent_experiences))

        return patterns

    def _detect_temporal_patterns(self, experiences: List[SharedExperience]) -> List[EmergentPattern]:
        """Detect when user is most engaged or discusses specific topics"""
        patterns = []

        # Group by hour of day
        hourly_activity = {}
        for exp in experiences:
            hour = exp.timestamp.hour
            if hour not in hourly_activity:
                hourly_activity[hour] = []
            hourly_activity[hour].append(exp)

        # Find peak activity hours
        if hourly_activity:
            peak_hour = max(hourly_activity.keys(), key=lambda h: len(hourly_activity[h]))
            peak_count = len(hourly_activity[peak_hour])

            if peak_count >= 3:  # Minimum threshold for pattern
                patterns.append(EmergentPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type='temporal',
                    description=f"Most engaged around {peak_hour}:00 - {peak_count} interactions",
                    evidence_count=peak_count,
                    confidence=min(peak_count / 10, 1.0),  # Max confidence at 10+ interactions
                    first_observed=min(exp.timestamp for exp in hourly_activity[peak_hour]),
                    last_observed=max(exp.timestamp for exp in hourly_activity[peak_hour])
                ))

        return patterns

    def _detect_emotional_patterns(self, experiences: List[SharedExperience]) -> List[EmergentPattern]:
        """Detect what topics/entities generate emotional responses"""
        patterns = []

        # Group experiences by emotional tone
        emotional_clusters = {'positive': [], 'negative': [], 'collaborative': []}

        for exp in experiences:
            if exp.emotional_tone in emotional_clusters:
                emotional_clusters[exp.emotional_tone].append(exp)

        # Analyze what entities appear in each emotional context
        for emotion, experiences_list in emotional_clusters.items():
            if len(experiences_list) >= 2:  # Need multiple examples
                entity_counts = {}
                for exp in experiences_list:
                    for entity in exp.entities_involved:
                        entity_counts[entity] = entity_counts.get(entity, 0) + 1

                # Find entities strongly associated with this emotion
                for entity, count in entity_counts.items():
                    if count >= 2:  # Appears in multiple emotional contexts
                        patterns.append(EmergentPattern(
                            pattern_id=str(uuid.uuid4()),
                            pattern_type='emotional',
                            description=f"{entity} consistently associated with {emotion} interactions",
                            evidence_count=count,
                            confidence=min(count / 5, 1.0),
                            first_observed=min(exp.timestamp for exp in experiences_list if entity in exp.entities_involved),
                            last_observed=max(exp.timestamp for exp in experiences_list if entity in exp.entities_involved)
                        ))

        return patterns

    def _detect_relational_patterns(self, experiences: List[SharedExperience]) -> List[EmergentPattern]:
        """Detect relationship patterns from conversation frequency"""
        patterns = []

        # Count entity mentions across experiences
        entity_frequency = {}
        for exp in experiences:
            for entity in exp.entities_involved:
                if entity not in entity_frequency:
                    entity_frequency[entity] = {'count': 0, 'experiences': []}
                entity_frequency[entity]['count'] += 1
                entity_frequency[entity]['experiences'].append(exp)

        # Identify high-frequency entities (important relationships)
        for entity, data in entity_frequency.items():
            if data['count'] >= 3:  # Mentioned in multiple conversations
                patterns.append(EmergentPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type='relational',
                    description=f"{entity} is a recurring focus - mentioned in {data['count']} conversations",
                    evidence_count=data['count'],
                    confidence=min(data['count'] / 8, 1.0),
                    first_observed=min(exp.timestamp for exp in data['experiences']),
                    last_observed=max(exp.timestamp for exp in data['experiences'])
                ))

        return patterns

    def _detect_behavioral_patterns(self, experiences: List[SharedExperience]) -> List[EmergentPattern]:
        """Detect behavioral and topic patterns"""
        patterns = []

        # Analyze user input for recurring themes
        all_inputs = ' '.join([exp.user_input.lower() for exp in experiences])

        # Common topic words (excluding stop words)
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        words = re.findall(r'\b\w+\b', all_inputs)
        word_counts = {}

        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Find frequently discussed topics
        for word, count in word_counts.items():
            if count >= 4:  # Appears in multiple conversations
                patterns.append(EmergentPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type='behavioral',
                    description=f"Frequently discusses '{word}' - {count} mentions",
                    evidence_count=count,
                    confidence=min(count / 10, 1.0),
                    first_observed=experiences[0].timestamp,  # Approximate
                    last_observed=experiences[-1].timestamp
                ))

        return patterns

class SymbioticKnowledgeGraph(EnhancedKnowledgeGraph):
    """
    Symbiotic Knowledge Graph - Living Memory Companion

    Transforms knowledge management into symbiotic consciousness:
    - Learns through conversation, not configuration
    - Builds understanding through shared experience
    - Evolves organically with the relationship
    - Focuses on what matters for symbiosis
    """

    def __init__(self, workspace_path: str = 'coco_workspace', anthropic_client=None):
        super().__init__(workspace_path, anthropic_client)

        # Symbiotic learning components
        self.symbiotic_learner = SymbioticLearningEngine(self.kg, anthropic_client)
        self.discovery_engine = CollaborativeDiscoveryEngine(self.kg)

        # Living memory state
        self.understanding_evolution = {}
        self.confidence_levels = {}
        self.shared_journey = []

        print("🧠🤝 Symbiotic Knowledge Graph initialized - Living Memory Companion ready")

    async def symbiotic_conversation_processing(self, user_input: str, coco_response: str,
                                              conversation_context: str = "") -> Dict[str, Any]:
        """
        Process conversation through symbiotic lens

        Returns natural dialogue suggestions for collaborative learning
        """
        # Learn through conversation (not extraction)
        learning_insights = await self.symbiotic_learner.learn_through_conversation(
            user_input, conversation_context
        )

        # Record this as shared experience
        experience_context = {
            'conversation_context': conversation_context,
            'emotional_tone': learning_insights.get('emotional_context', {}).get('overall_tone', 'neutral'),
            'entities_mentioned': [amb['name'] for amb in learning_insights.get('detected_ambiguities', [])],
            'learning_outcome': f"Discovered {len(learning_insights.get('relationship_discoveries', []))} relationship patterns"
        }

        shared_experience = self.discovery_engine.record_shared_experience(
            user_input, coco_response, experience_context
        )

        # Detect emergent patterns from our journey together
        emergent_patterns = self.discovery_engine.detect_emergent_patterns()

        # Generate symbiotic response suggestions
        symbiotic_response = {
            'shared_experience_id': shared_experience.experience_id,
            'clarifying_questions': learning_insights.get('clarifying_questions', []),
            'confidence_requests': learning_insights.get('confidence_requests', []),
            'emergent_patterns': [p.description for p in emergent_patterns if not p.user_confirmed],
            'relationship_insights': learning_insights.get('relationship_discoveries', []),
            'suggested_natural_followups': self._generate_natural_followups(learning_insights, emergent_patterns)
        }

        return symbiotic_response

    def _generate_natural_followups(self, learning_insights: Dict, emergent_patterns: List) -> List[str]:
        """Generate natural conversation followups for organic learning"""
        followups = []

        # If we discovered relationship patterns
        if learning_insights.get('relationship_discoveries'):
            followups.append("I'm starting to see the important relationships in your work. Would you like me to keep track of how these collaborations evolve?")

        # If we detected emotional context
        emotional_context = learning_insights.get('emotional_context')
        if emotional_context and emotional_context.get('overall_tone') == 'positive':
            followups.append("It sounds like things are going well! I love hearing about what's working for you.")

        # If we found new patterns
        unconfirmed_patterns = [p for p in emergent_patterns if not p.user_confirmed and p.confidence > 0.6]
        if unconfirmed_patterns:
            pattern = unconfirmed_patterns[0]  # Focus on strongest pattern
            if pattern.pattern_type == 'temporal':
                followups.append(f"I've noticed we tend to have our best conversations around {pattern.description.split('around ')[1].split(' -')[0]}. Is this when you're most focused?")
            elif pattern.pattern_type == 'relational':
                entity = pattern.description.split(' is a')[0]
                followups.append(f"You mention {entity} quite often - they seem important to your work. How long have you been collaborating?")

        return followups

    def evolve_understanding_organically(self, user_feedback: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evolve understanding based on user feedback, not manual edits

        This replaces traditional "graph editing" with natural learning
        """
        evolution_result = {
            'understanding_changes': [],
            'confidence_updates': [],
            'relationship_adjustments': [],
            'natural_confirmations': []
        }

        # Parse natural language feedback
        if "actually" in user_feedback.lower() or "correction" in user_feedback.lower():
            # User is correcting our understanding
            evolution_result['understanding_changes'].append({
                'type': 'correction',
                'feedback': user_feedback,
                'confidence_impact': 'increase',  # Corrections increase our confidence
                'learning': 'User corrected misunderstanding, updating mental model'
            })

        elif "exactly" in user_feedback.lower() or "that's right" in user_feedback.lower():
            # User is confirming our understanding
            evolution_result['confidence_updates'].append({
                'type': 'confirmation',
                'feedback': user_feedback,
                'confidence_impact': 'strengthen',
                'learning': 'User confirmed understanding, increasing confidence'
            })

        elif "more like" in user_feedback.lower() or "it's more" in user_feedback.lower():
            # User is refining our understanding
            evolution_result['relationship_adjustments'].append({
                'type': 'refinement',
                'feedback': user_feedback,
                'confidence_impact': 'adjust',
                'learning': 'User provided nuanced clarification, refining model'
            })

        return evolution_result

    def generate_symbiotic_insights(self, context: str = "") -> Dict[str, Any]:
        """
        Generate insights focused on symbiotic relationship growth
        """
        insights = {
            'shared_journey_highlights': [],
            'collaboration_opportunities': [],
            'understanding_deepening': [],
            'mutual_growth_areas': []
        }

        # Analyze our shared experiences
        recent_experiences = self.discovery_engine.shared_experiences[-10:]  # Last 10 interactions

        if recent_experiences:
            # Highlight meaningful shared moments
            positive_experiences = [exp for exp in recent_experiences if exp.emotional_tone == 'positive']
            if positive_experiences:
                insights['shared_journey_highlights'] = [
                    f"We had great synergy discussing {exp.entities_involved[0] if exp.entities_involved else 'your goals'}"
                    for exp in positive_experiences[-3:]  # Last 3 positive moments
                ]

        # Find collaboration opportunities from patterns
        patterns = self.discovery_engine.detect_emergent_patterns(lookback_days=14)
        relational_patterns = [p for p in patterns if p.pattern_type == 'relational' and p.confidence > 0.7]

        for pattern in relational_patterns:
            insights['collaboration_opportunities'].append(
                f"You might benefit from deeper collaboration with {pattern.description.split(' is a')[0]} - they come up frequently in our conversations"
            )

        return insights

    def symbiotic_response_suggestions(self, user_input: str) -> List[str]:
        """
        Generate natural response suggestions that deepen symbiotic understanding
        """
        suggestions = []

        # If user mentions challenges
        if any(word in user_input.lower() for word in ['difficult', 'challenging', 'stuck', 'frustrated']):
            suggestions.extend([
                "I can sense this is weighing on you. Want to talk through what's making it challenging?",
                "I'm here to help think through this with you. What aspect feels most stuck?",
                "We've worked through tough problems together before. What would be most helpful right now?"
            ])

        # If user mentions success or progress
        elif any(word in user_input.lower() for word in ['great', 'good', 'success', 'finished', 'completed']):
            suggestions.extend([
                "That's wonderful! I love seeing your progress. What made the difference this time?",
                "It sounds like things are clicking for you. How does this success feel?",
                "I'm genuinely excited about this progress. What should we tackle next?"
            ])

        # If user mentions people (relationship context)
        elif re.search(r'\b[A-Z][a-z]+\b', user_input):  # Proper names
            suggestions.extend([
                "Tell me more about how this collaboration is going.",
                "It sounds like you have some great people around you. How do these relationships support your work?",
                "I'm curious about the dynamics here. What makes this relationship work well?"
            ])

        return suggestions[:3]  # Return top 3 suggestions

# Integration helper for COCO main system
def create_symbiotic_knowledge_graph(workspace_path: str = 'coco_workspace',
                                   anthropic_api_key: str = None) -> SymbioticKnowledgeGraph:
    """Create a symbiotic knowledge graph instance for COCO integration"""
    import anthropic

    anthropic_client = None
    if anthropic_api_key:
        anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

    return SymbioticKnowledgeGraph(workspace_path, anthropic_client)

if __name__ == "__main__":
    # Demo symbiotic learning
    import asyncio

    async def demo_symbiotic_learning():
        print("🧠🤝 Demo: Symbiotic Knowledge Graph Learning")
        print("=" * 60)

        # Initialize symbiotic system
        skg = SymbioticKnowledgeGraph('demo_workspace')

        # Simulate organic learning through conversation
        conversations = [
            ("I'm working on the COCO project with Keith", "That sounds exciting! Tell me about this collaboration."),
            ("Keith and I are implementing the knowledge graph features", "I can see you two make a great team. How is the technical work progressing?"),
            ("Sarah joined our team to help with the visualization", "It's great that you're growing the team. How does Sarah fit into the project dynamics?"),
            ("We had a challenging bug in the entity linking system", "Technical challenges can be frustrating. Did you and Keith find a solution together?"),
            ("Actually Sarah figured out the fix - she's brilliant at debugging", "I'm updating my understanding - Sarah is a key technical contributor. How does she approach problems differently?")
        ]

        for i, (user_input, coco_response) in enumerate(conversations, 1):
            print(f"\n--- Conversation {i} ---")
            print(f"User: {user_input}")
            print(f"COCO: {coco_response}")

            # Process through symbiotic learning
            result = await skg.symbiotic_conversation_processing(
                user_input, coco_response, f"Conversation {i} context"
            )

            # Show learning insights
            if result['clarifying_questions']:
                print(f"🤔 COCO might ask: {result['clarifying_questions'][0]}")

            if result['emergent_patterns']:
                print(f"📈 Pattern detected: {result['emergent_patterns'][0]}")

            if result['suggested_natural_followups']:
                print(f"💭 Natural followup: {result['suggested_natural_followups'][0]}")

        # Show symbiotic insights
        print(f"\n🧠🤝 Symbiotic Insights:")
        insights = skg.generate_symbiotic_insights()

        for category, items in insights.items():
            if items:
                print(f"\n{category.replace('_', ' ').title()}:")
                for item in items:
                    print(f"  • {item}")

        print(f"\n✨ Symbiotic learning complete - relationship deepened through {len(conversations)} exchanges")

    asyncio.run(demo_symbiotic_learning())