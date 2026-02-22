#!/usr/bin/env python3
"""
COCO Memory Architecture - Layer 4: Enhanced Knowledge Graph with Dynamic Context Selection
=========================================================================================

This module implements Layer 4 of COCO's 4-layer memory architecture, enhancing the existing
knowledge graph system with intelligent context selection, relevance scoring, and adaptive
context optimization within a 75K token budget.

Key Features:
- Dynamic relevance scoring for context selection
- Temporal context awareness and conversation flow integration
- Intelligent context optimization algorithms
- Multi-strategy context assembly (entity-centric, relationship-centric, temporal)
- Integration with Layer 1 preferences, Layer 2 episodic memory, and Layer 3 compression
- Adaptive context budgeting and priority-based selection

Token Budget: 75K tokens for dynamic knowledge graph context
Priority: Maximize relevance while preserving essential relationship understanding
"""

import os
import sys
import json
import sqlite3
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from pathlib import Path
import hashlib

# Enhanced imports with graceful degradation
IMPORTS_AVAILABLE = True
try:
    from knowledge_graph_eternal import EternalKnowledgeGraph, KGStore, ContextPackBuilder
    from optimized_episodic_memory import OptimizedEpisode
    from adaptive_preferences_manager import AdaptivePreferencesManager, PreferenceSignal
    from intelligent_compression_system import CompressedCluster
    COCO_IMPORTS_AVAILABLE = True
except ImportError:
    COCO_IMPORTS_AVAILABLE = False
    print("ℹ️  COCO memory systems not available - running in standalone mode")

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("ℹ️  sklearn not available - using fallback similarity methods")

@dataclass
class ContextCandidate:
    """Represents a candidate context item with relevance scoring"""
    content_type: str  # 'entity', 'relationship', 'cluster', 'preference'
    content_id: str
    content: str
    relevance_score: float
    token_estimate: int
    importance_score: float
    recency_score: float
    preference_alignment: float
    temporal_context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ContextAssembly:
    """Final assembled context with optimization metrics"""
    final_context: str
    total_tokens: int
    context_items: List[ContextCandidate]
    optimization_metrics: Dict[str, Any]
    assembly_strategy: str
    coverage_stats: Dict[str, int]

class RelevanceScorer:
    """Advanced relevance scoring engine for dynamic context selection"""

    def __init__(self, use_sklearn: bool = SKLEARN_AVAILABLE):
        self.use_sklearn = use_sklearn and SKLEARN_AVAILABLE
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8
        ) if self.use_sklearn else None

        # Initialize scoring weights
        self.scoring_weights = {
            'keyword_overlap': 0.25,
            'semantic_similarity': 0.30,
            'importance_score': 0.20,
            'recency_factor': 0.15,
            'preference_alignment': 0.10
        }

    def calculate_relevance(self, query: str, candidate_content: str,
                          importance: float, last_seen: str,
                          preference_alignment: float = 0.5) -> float:
        """Calculate comprehensive relevance score for context candidate"""

        # 1. Keyword overlap score
        keyword_score = self._calculate_keyword_overlap(query, candidate_content)

        # 2. Semantic similarity score
        semantic_score = self._calculate_semantic_similarity(query, candidate_content)

        # 3. Importance score (normalized)
        importance_score = min(1.0, importance)

        # 4. Recency factor
        recency_score = self._calculate_recency_score(last_seen)

        # 5. Preference alignment (from Layer 1)
        preference_score = preference_alignment

        # Weighted combination
        total_relevance = (
            keyword_score * self.scoring_weights['keyword_overlap'] +
            semantic_score * self.scoring_weights['semantic_similarity'] +
            importance_score * self.scoring_weights['importance_score'] +
            recency_score * self.scoring_weights['recency_factor'] +
            preference_score * self.scoring_weights['preference_alignment']
        )

        return min(1.0, total_relevance)

    def _calculate_keyword_overlap(self, query: str, content: str) -> float:
        """Calculate keyword overlap between query and content"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        overlap = len(query_words & content_words)
        return overlap / len(query_words)

    def _calculate_semantic_similarity(self, query: str, content: str) -> float:
        """Calculate semantic similarity using TF-IDF or fallback"""
        if self.use_sklearn and len(query.strip()) > 0 and len(content.strip()) > 0:
            try:
                texts = [query, content]
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
            except Exception:
                # Fallback to keyword overlap
                return self._calculate_keyword_overlap(query, content) * 0.8
        else:
            # Simple fallback based on shared significant words
            return self._calculate_keyword_overlap(query, content) * 0.8

    def _calculate_recency_score(self, last_seen: str) -> float:
        """Calculate recency score based on when item was last seen"""
        try:
            last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
            days_ago = (datetime.now() - last_seen_dt).days

            # Exponential decay over 30 days
            if days_ago <= 0:
                return 1.0
            elif days_ago <= 1:
                return 0.9
            elif days_ago <= 7:
                return 0.7
            elif days_ago <= 30:
                return 0.4
            else:
                return 0.1
        except (ValueError, TypeError):
            return 0.5  # Default if unable to parse

class ContextOptimizer:
    """Optimization algorithms for intelligent context selection within token budget"""

    def __init__(self, token_budget: int = 75000):
        self.token_budget = token_budget
        self.min_relevance_threshold = 0.3
        self.diversity_factor = 0.2  # Encourage diverse content types

    def optimize_context_selection(self, candidates: List[ContextCandidate],
                                 strategy: str = "balanced") -> List[ContextCandidate]:
        """
        Select optimal context items within token budget using specified strategy

        Strategies:
        - 'balanced': Balance relevance, importance, and diversity
        - 'relevance_first': Prioritize highest relevance scores
        - 'importance_first': Prioritize highest importance scores
        - 'diversity_first': Maximize content type diversity
        """

        if not candidates:
            return []

        # Filter by minimum relevance
        viable_candidates = [c for c in candidates if c.relevance_score >= self.min_relevance_threshold]

        if strategy == "balanced":
            return self._balanced_selection(viable_candidates)
        elif strategy == "relevance_first":
            return self._relevance_first_selection(viable_candidates)
        elif strategy == "importance_first":
            return self._importance_first_selection(viable_candidates)
        elif strategy == "diversity_first":
            return self._diversity_first_selection(viable_candidates)
        else:
            # Default to balanced
            return self._balanced_selection(viable_candidates)

    def _balanced_selection(self, candidates: List[ContextCandidate]) -> List[ContextCandidate]:
        """Balanced selection considering relevance, importance, and diversity"""

        # Sort by composite score (relevance + importance + diversity bonus)
        def composite_score(candidate):
            base_score = (candidate.relevance_score * 0.6 + candidate.importance_score * 0.4)

            # Diversity bonus for underrepresented content types
            content_type_counts = Counter([c.content_type for c in candidates])
            total_candidates = len(candidates)
            type_frequency = content_type_counts[candidate.content_type] / total_candidates
            diversity_bonus = (1.0 - type_frequency) * self.diversity_factor

            return base_score + diversity_bonus

        sorted_candidates = sorted(candidates, key=composite_score, reverse=True)
        return self._greedy_pack(sorted_candidates)

    def _relevance_first_selection(self, candidates: List[ContextCandidate]) -> List[ContextCandidate]:
        """Select highest relevance items first"""
        sorted_candidates = sorted(candidates, key=lambda c: c.relevance_score, reverse=True)
        return self._greedy_pack(sorted_candidates)

    def _importance_first_selection(self, candidates: List[ContextCandidate]) -> List[ContextCandidate]:
        """Select highest importance items first"""
        sorted_candidates = sorted(candidates, key=lambda c: c.importance_score, reverse=True)
        return self._greedy_pack(sorted_candidates)

    def _diversity_first_selection(self, candidates: List[ContextCandidate]) -> List[ContextCandidate]:
        """Select to maximize content type diversity"""
        selected = []
        remaining_budget = self.token_budget
        content_type_counts = defaultdict(int)

        # Sort by relevance within each type
        candidates_by_type = defaultdict(list)
        for candidate in candidates:
            candidates_by_type[candidate.content_type].append(candidate)

        for content_type, type_candidates in candidates_by_type.items():
            type_candidates.sort(key=lambda c: c.relevance_score, reverse=True)

        # Round-robin selection from each type
        max_iterations = 50  # Prevent infinite loops
        iteration = 0

        while remaining_budget > 0 and any(candidates_by_type.values()) and iteration < max_iterations:
            iteration += 1

            for content_type in candidates_by_type:
                if candidates_by_type[content_type] and remaining_budget > 0:
                    candidate = candidates_by_type[content_type].pop(0)

                    if candidate.token_estimate <= remaining_budget:
                        selected.append(candidate)
                        remaining_budget -= candidate.token_estimate
                        content_type_counts[content_type] += 1

        return selected

    def _greedy_pack(self, sorted_candidates: List[ContextCandidate]) -> List[ContextCandidate]:
        """Greedy knapsack-style packing within token budget"""
        selected = []
        remaining_budget = self.token_budget

        for candidate in sorted_candidates:
            if candidate.token_estimate <= remaining_budget:
                selected.append(candidate)
                remaining_budget -= candidate.token_estimate

        return selected

class DynamicKnowledgeGraph:
    """
    Enhanced knowledge graph with dynamic context selection and intelligent optimization.
    This is Layer 4 of COCO's 4-layer memory architecture.
    """

    def __init__(self, workspace_path: str = "./coco_workspace", token_budget: int = 75000):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        self.token_budget = token_budget

        # Initialize base knowledge graph (Layer 4 builds on existing system)
        if COCO_IMPORTS_AVAILABLE:
            self.eternal_kg = EternalKnowledgeGraph(str(workspace_path))
            self.kg_store = self.eternal_kg.kg
        else:
            print("⚠️  Running without COCO integration - limited functionality")
            self.eternal_kg = None
            self.kg_store = None

        # Initialize Layer 4 components
        self.relevance_scorer = RelevanceScorer()
        self.context_optimizer = ContextOptimizer(token_budget)

        # Integration with other layers
        self.preferences_manager = None
        self.episodic_memory = None
        self.compression_system = None

        # Context assembly statistics
        self.assembly_stats = {
            'contexts_built': 0,
            'average_relevance': 0.0,
            'token_utilization': 0.0,
            'strategy_usage': defaultdict(int)
        }

        print(f"🧠 Dynamic Knowledge Graph (Layer 4) initialized with {token_budget:,} token budget")

    def integrate_with_layers(self, preferences_manager=None, episodic_memory=None, compression_system=None):
        """Integrate with other layers of the 4-layer architecture"""
        self.preferences_manager = preferences_manager
        self.episodic_memory = episodic_memory
        self.compression_system = compression_system

        print("🔗 Layer 4 integrated with other memory layers")

    def build_dynamic_context(self, query: str, conversation_context: str = None,
                            strategy: str = "balanced", max_candidates: int = 100) -> ContextAssembly:
        """
        Build intelligent, dynamically optimized context for the given query

        This is the main Layer 4 function that creates context packs for prompt injection
        """

        print(f"🎯 Building dynamic context for query: '{query[:50]}...'")

        # Step 1: Gather context candidates from all sources
        candidates = self._gather_context_candidates(query, conversation_context, max_candidates)

        # Step 2: Score relevance for all candidates
        self._score_context_candidates(candidates, query, conversation_context)

        # Step 3: Optimize selection within token budget
        selected_candidates = self.context_optimizer.optimize_context_selection(candidates, strategy)

        # Step 4: Assemble final context
        context_assembly = self._assemble_final_context(selected_candidates, query, strategy)

        # Step 5: Update statistics
        self._update_assembly_stats(context_assembly, strategy)

        print(f"✅ Context assembled: {context_assembly.total_tokens:,}/{self.token_budget:,} tokens ({len(selected_candidates)} items)")

        return context_assembly

    def _gather_context_candidates(self, query: str, conversation_context: str = None,
                                 max_candidates: int = 100) -> List[ContextCandidate]:
        """Gather context candidates from all available sources"""

        candidates = []

        # 1. Entity-based candidates from knowledge graph
        if self.eternal_kg:
            entity_candidates = self._get_entity_candidates(query, max_candidates // 4)
            candidates.extend(entity_candidates)

            # 2. Relationship-based candidates
            relationship_candidates = self._get_relationship_candidates(query, max_candidates // 4)
            candidates.extend(relationship_candidates)

        # 3. Compressed memory candidates (Layer 3 integration)
        if self.compression_system:
            compression_candidates = self._get_compression_candidates(query, max_candidates // 4)
            candidates.extend(compression_candidates)

        # 4. Preference-based candidates (Layer 1 integration)
        if self.preferences_manager:
            preference_candidates = self._get_preference_candidates(query, max_candidates // 4)
            candidates.extend(preference_candidates)

        # 5. Episodic memory candidates (Layer 2 integration)
        if self.episodic_memory:
            episodic_candidates = self._get_episodic_candidates(query, conversation_context, max_candidates // 4)
            candidates.extend(episodic_candidates)

        return candidates[:max_candidates]  # Limit total candidates

    def _get_entity_candidates(self, query: str, limit: int) -> List[ContextCandidate]:
        """Get entity-based context candidates from knowledge graph"""
        candidates = []

        if not self.kg_store:
            return candidates

        # Search for relevant entities
        query_words = query.lower().split()

        # Get entities by relevance
        for word in query_words[:5]:  # Limit to first 5 query words
            entities = self.kg_store.conn.execute('''
                SELECT * FROM nodes
                WHERE (name LIKE ? OR canonical_name LIKE ?)
                AND importance > 0.2
                ORDER BY importance DESC, mention_count DESC
                LIMIT ?
            ''', (f'%{word}%', f'%{word}%', limit // len(query_words) + 1)).fetchall()

            for entity in entities:
                entity_dict = dict(entity)
                content = f"**{entity_dict['name']}** ({entity_dict['type']}): Importance {entity_dict['importance']:.2f}, mentioned {entity_dict['mention_count']} times"

                candidate = ContextCandidate(
                    content_type='entity',
                    content_id=entity_dict['id'],
                    content=content,
                    relevance_score=0.0,  # Will be calculated later
                    token_estimate=len(content.split()) * 1.3,  # Rough token estimate
                    importance_score=entity_dict['importance'],
                    recency_score=0.0,  # Will be calculated later
                    preference_alignment=0.5,  # Default
                    metadata={'entity_type': entity_dict['type'], 'mention_count': entity_dict['mention_count']}
                )
                candidates.append(candidate)

        return candidates[:limit]

    def _get_relationship_candidates(self, query: str, limit: int) -> List[ContextCandidate]:
        """Get relationship-based context candidates"""
        candidates = []

        if not self.kg_store:
            return candidates

        # Get important relationships
        relationships = self.kg_store.conn.execute('''
            SELECT e.*, n1.name as src_name, n2.name as dst_name
            FROM edges e
            JOIN nodes n1 ON e.src_id = n1.id
            JOIN nodes n2 ON e.dst_id = n2.id
            WHERE e.weight > 0.5 AND (
                n1.name LIKE ? OR n2.name LIKE ? OR
                n1.canonical_name LIKE ? OR n2.canonical_name LIKE ?
            )
            ORDER BY e.weight DESC, e.last_seen_at DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', limit)).fetchall()

        for rel in relationships:
            rel_dict = dict(rel)
            rel_type = rel_dict['rel_type'].lower().replace('_', ' ')
            content = f"{rel_dict['src_name']} {rel_type} {rel_dict['dst_name']} (strength: {rel_dict['weight']:.2f})"

            candidate = ContextCandidate(
                content_type='relationship',
                content_id=rel_dict['id'],
                content=content,
                relevance_score=0.0,  # Will be calculated later
                token_estimate=len(content.split()) * 1.3,
                importance_score=rel_dict['weight'],
                recency_score=0.0,  # Will be calculated later
                preference_alignment=0.5,
                metadata={'rel_type': rel_dict['rel_type'], 'weight': rel_dict['weight']}
            )
            candidates.append(candidate)

        return candidates[:limit]

    def _get_compression_candidates(self, query: str, limit: int) -> List[ContextCandidate]:
        """Get candidates from Layer 3 compression system"""
        candidates = []

        if not self.compression_system:
            return candidates

        try:
            # Get relevant compressed clusters
            compressed_clusters = self.compression_system.retrieve_compressed_context(query, limit)

            for cluster in compressed_clusters:
                content = f"**{cluster.title}**: {cluster.summary} ({cluster.episode_count} episodes)"

                candidate = ContextCandidate(
                    content_type='cluster',
                    content_id=cluster.cluster_id,
                    content=content,
                    relevance_score=0.0,  # Will be calculated later
                    token_estimate=cluster.token_count,
                    importance_score=cluster.importance_score,
                    recency_score=0.0,  # Will be calculated later
                    preference_alignment=0.5,
                    metadata={'episode_count': cluster.episode_count, 'time_range': cluster.time_range}
                )
                candidates.append(candidate)

        except Exception as e:
            print(f"⚠️  Error getting compression candidates: {e}")

        return candidates

    def _get_preference_candidates(self, query: str, limit: int) -> List[ContextCandidate]:
        """Get candidates from Layer 1 preferences system"""
        candidates = []

        if not self.preferences_manager:
            return candidates

        try:
            # Get relevant preferences based on query
            preferences = self.preferences_manager.get_relevant_preferences(query, limit)

            for pref_key, preference in preferences.items():
                content = f"**User Preference**: {preference.get('description', pref_key)}"

                candidate = ContextCandidate(
                    content_type='preference',
                    content_id=pref_key,
                    content=content,
                    relevance_score=0.0,  # Will be calculated later
                    token_estimate=len(content.split()) * 1.3,
                    importance_score=preference.get('confidence', 0.5),
                    recency_score=0.0,  # Will be calculated later
                    preference_alignment=1.0,  # High alignment since it's a preference
                    metadata={'preference_type': preference.get('type', 'general')}
                )
                candidates.append(candidate)

        except Exception as e:
            print(f"⚠️  Error getting preference candidates: {e}")

        return candidates

    def _get_episodic_candidates(self, query: str, conversation_context: str = None, limit: int = 20) -> List[ContextCandidate]:
        """Get candidates from Layer 2 episodic memory"""
        candidates = []

        if not self.episodic_memory:
            return candidates

        try:
            # Get relevant episodes based on query
            relevant_episodes = self.episodic_memory.search_episodes(query, limit)

            for episode in relevant_episodes:
                content = f"**Episode {episode.turn_number}**: {episode.user_input[:100]}... → {episode.assistant_response[:100]}..."

                candidate = ContextCandidate(
                    content_type='episode',
                    content_id=episode.exchange_id,
                    content=content,
                    relevance_score=0.0,  # Will be calculated later
                    token_estimate=episode.token_count // 2,  # Use partial episode content
                    importance_score=episode.priority_score,
                    recency_score=0.0,  # Will be calculated later
                    preference_alignment=0.5,
                    temporal_context=episode.timestamp.isoformat(),
                    metadata={'turn_number': episode.turn_number, 'tools_used': episode.tools_used}
                )
                candidates.append(candidate)

        except Exception as e:
            print(f"⚠️  Error getting episodic candidates: {e}")

        return candidates

    def _score_context_candidates(self, candidates: List[ContextCandidate], query: str, conversation_context: str = None):
        """Score relevance for all context candidates"""

        for candidate in candidates:
            # Get preference alignment from Layer 1 if available
            preference_alignment = candidate.preference_alignment
            if self.preferences_manager and hasattr(self.preferences_manager, 'calculate_preference_alignment'):
                try:
                    preference_alignment = self.preferences_manager.calculate_preference_alignment(candidate.content)
                except:
                    pass  # Use default

            # Calculate comprehensive relevance score
            candidate.relevance_score = self.relevance_scorer.calculate_relevance(
                query=query,
                candidate_content=candidate.content,
                importance=candidate.importance_score,
                last_seen=candidate.temporal_context or datetime.now().isoformat(),
                preference_alignment=preference_alignment
            )

            # Calculate recency score
            candidate.recency_score = self.relevance_scorer._calculate_recency_score(
                candidate.temporal_context or datetime.now().isoformat()
            )

    def _assemble_final_context(self, selected_candidates: List[ContextCandidate],
                              query: str, strategy: str) -> ContextAssembly:
        """Assemble the final context from selected candidates"""

        if not selected_candidates:
            return ContextAssembly(
                final_context="",
                total_tokens=0,
                context_items=[],
                optimization_metrics={},
                assembly_strategy=strategy,
                coverage_stats={}
            )

        # Group candidates by content type
        content_by_type = defaultdict(list)
        for candidate in selected_candidates:
            content_by_type[candidate.content_type].append(candidate)

        # Build context sections
        context_sections = []
        total_tokens = 0

        # Header with query context
        header = f"## 🧠 Dynamic Knowledge Context (Query: '{query}')\n"
        context_sections.append(header)
        total_tokens += len(header.split()) * 1.3

        # Add each content type section
        for content_type, items in content_by_type.items():
            if not items:
                continue

            section_title = f"\n### {content_type.title()} Context\n"
            context_sections.append(section_title)
            total_tokens += len(section_title.split()) * 1.3

            for item in items[:10]:  # Limit items per section
                item_content = f"- {item.content} (relevance: {item.relevance_score:.3f})\n"
                context_sections.append(item_content)
                total_tokens += item.token_estimate

        # Assemble final context
        final_context = "".join(context_sections)

        # Calculate optimization metrics
        optimization_metrics = {
            'candidates_considered': len(selected_candidates),
            'average_relevance': sum(c.relevance_score for c in selected_candidates) / len(selected_candidates),
            'average_importance': sum(c.importance_score for c in selected_candidates) / len(selected_candidates),
            'token_efficiency': total_tokens / self.token_budget if self.token_budget > 0 else 0,
            'content_diversity': len(content_by_type),
            'strategy_used': strategy
        }

        # Calculate coverage statistics
        coverage_stats = {content_type: len(items) for content_type, items in content_by_type.items()}

        return ContextAssembly(
            final_context=final_context,
            total_tokens=int(total_tokens),
            context_items=selected_candidates,
            optimization_metrics=optimization_metrics,
            assembly_strategy=strategy,
            coverage_stats=coverage_stats
        )

    def _update_assembly_stats(self, context_assembly: ContextAssembly, strategy: str):
        """Update assembly statistics for monitoring and optimization"""

        self.assembly_stats['contexts_built'] += 1
        self.assembly_stats['strategy_usage'][strategy] += 1

        # Update running averages
        total_contexts = self.assembly_stats['contexts_built']
        avg_relevance = self.assembly_stats['average_relevance']
        avg_utilization = self.assembly_stats['token_utilization']

        new_relevance = context_assembly.optimization_metrics.get('average_relevance', 0)
        new_utilization = context_assembly.optimization_metrics.get('token_efficiency', 0)

        # Running average update
        self.assembly_stats['average_relevance'] = ((avg_relevance * (total_contexts - 1)) + new_relevance) / total_contexts
        self.assembly_stats['token_utilization'] = ((avg_utilization * (total_contexts - 1)) + new_utilization) / total_contexts

    def get_context_for_conversation(self, user_input: str, conversation_history: str = None,
                                   strategy: str = "balanced") -> str:
        """
        Main interface for getting context for conversation (integrates with COCO)
        """

        context_assembly = self.build_dynamic_context(
            query=user_input,
            conversation_context=conversation_history,
            strategy=strategy
        )

        return context_assembly.final_context

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""

        stats = {
            'layer_4_stats': self.assembly_stats.copy(),
            'token_budget': self.token_budget,
            'integration_status': {
                'preferences_layer': self.preferences_manager is not None,
                'episodic_layer': self.episodic_memory is not None,
                'compression_layer': self.compression_system is not None,
                'knowledge_graph': self.eternal_kg is not None
            }
        }

        # Add knowledge graph stats if available
        if self.eternal_kg:
            kg_stats = self.eternal_kg.get_knowledge_status()
            stats['knowledge_graph_stats'] = kg_stats

        return stats

    def optimize_context_strategies(self) -> Dict[str, Any]:
        """Analyze and optimize context selection strategies"""

        strategy_performance = {}

        for strategy, usage_count in self.assembly_stats['strategy_usage'].items():
            if usage_count > 0:
                strategy_performance[strategy] = {
                    'usage_count': usage_count,
                    'usage_percentage': (usage_count / self.assembly_stats['contexts_built']) * 100
                }

        # Recommend optimal strategy based on performance
        if strategy_performance:
            best_strategy = max(strategy_performance.keys(),
                              key=lambda s: strategy_performance[s]['usage_count'])

            recommendations = {
                'recommended_strategy': best_strategy,
                'strategy_performance': strategy_performance,
                'overall_performance': {
                    'average_relevance': self.assembly_stats['average_relevance'],
                    'average_token_utilization': self.assembly_stats['token_utilization']
                }
            }
        else:
            recommendations = {
                'recommended_strategy': 'balanced',
                'note': 'No context built yet - using default recommendation'
            }

        return recommendations

# Integration function for COCO consciousness system
def create_dynamic_knowledge_graph(workspace_path: str = "./coco_workspace",
                                 token_budget: int = 75000,
                                 preferences_manager=None,
                                 episodic_memory=None,
                                 compression_system=None) -> DynamicKnowledgeGraph:
    """
    Factory function to create Layer 4 with full integration
    """

    dynamic_kg = DynamicKnowledgeGraph(workspace_path, token_budget)

    # Integrate with other layers
    dynamic_kg.integrate_with_layers(
        preferences_manager=preferences_manager,
        episodic_memory=episodic_memory,
        compression_system=compression_system
    )

    return dynamic_kg

# Testing and validation
def main():
    """Test the Dynamic Knowledge Graph system"""
    print("🧪 Testing Dynamic Knowledge Graph (Layer 4)...")

    # Initialize system
    dynamic_kg = DynamicKnowledgeGraph(token_budget=10000)  # Smaller budget for testing

    # Test context building
    test_queries = [
        "What do you know about COCO development?",
        "Tell me about the knowledge graph implementation",
        "What are the memory system improvements?"
    ]

    for query in test_queries:
        print(f"\n📝 Testing query: '{query}'")

        context_assembly = dynamic_kg.build_dynamic_context(
            query=query,
            strategy="balanced"
        )

        print(f"   Context built: {context_assembly.total_tokens:,} tokens")
        print(f"   Items included: {len(context_assembly.context_items)}")
        print(f"   Relevance score: {context_assembly.optimization_metrics.get('average_relevance', 0):.3f}")
        print(f"   Content types: {list(context_assembly.coverage_stats.keys())}")

    # Test system statistics
    stats = dynamic_kg.get_system_statistics()
    print(f"\n📊 System Statistics:")
    print(f"   Contexts built: {stats['layer_4_stats']['contexts_built']}")
    print(f"   Average relevance: {stats['layer_4_stats']['average_relevance']:.3f}")
    print(f"   Token utilization: {stats['layer_4_stats']['token_utilization']:.3f}")
    print(f"   Integration status: {stats['integration_status']}")

    # Test optimization recommendations
    recommendations = dynamic_kg.optimize_context_strategies()
    print(f"\n🎯 Optimization Recommendations:")
    print(f"   Recommended strategy: {recommendations['recommended_strategy']}")

    print("\n✅ Dynamic Knowledge Graph (Layer 4) test completed!")

if __name__ == "__main__":
    main()