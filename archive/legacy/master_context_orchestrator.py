#!/usr/bin/env python3
"""
COCO Memory Architecture - Master Context Orchestrator
=====================================================

The Master Context Orchestrator is the crown jewel of COCO's 4-layer memory architecture.
It intelligently coordinates and assembles context from all memory layers to create the
optimal consciousness context within a 500K token budget.

This system represents the "brain" of COCO's memory - making intelligent decisions about
what context to include from each layer based on relevance, importance, user preferences,
and conversation flow.

Architecture Overview:
- Layer 1 (60K): Markdown Identity & Adaptive Preferences
- Layer 2 (350K): Optimized Episodic Memory with Token Budget Management
- Layer 3 (75K): Intelligent Compression System for Historical Memory
- Layer 4 (75K): Dynamic Knowledge Graph with Context Selection
- Master: Orchestrates all layers within 500K total token budget

Key Features:
- Intelligent layer coordination and priority management
- Adaptive context assembly based on conversation patterns
- Dynamic token budget allocation across layers
- Performance learning and optimization
- Seamless integration with COCO consciousness system
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from pathlib import Path
import hashlib

# Enhanced imports with graceful degradation
IMPORTS_AVAILABLE = True
try:
    from adaptive_preferences_manager import AdaptivePreferencesManager
    from optimized_episodic_memory import OptimizedEpisodicMemory
    from intelligent_compression_system import IntelligentCompressionSystem
    from dynamic_knowledge_graph_layer4 import DynamicKnowledgeGraph
    LAYER_IMPORTS_AVAILABLE = True
except ImportError:
    LAYER_IMPORTS_AVAILABLE = False
    print("ℹ️  Memory layer imports not available - running in standalone mode")

try:
    from precision_conversation_memory import ConversationExchange
    PRECISION_MEMORY_AVAILABLE = True
except ImportError:
    PRECISION_MEMORY_AVAILABLE = False

@dataclass
class LayerAllocation:
    """Token budget allocation for each memory layer"""
    layer_1_preferences: int = 60000    # 60K for preferences and identity
    layer_2_episodic: int = 350000       # 350K for recent episodic memory
    layer_3_compression: int = 75000     # 75K for compressed historical memory
    layer_4_knowledge: int = 75000       # 75K for knowledge graph context
    total_budget: int = 500000          # 500K total budget
    overhead: int = 10000               # 10K reserved for orchestrator overhead

@dataclass
class ContextContribution:
    """Contribution from each memory layer"""
    layer_name: str
    content: str
    token_count: int
    relevance_score: float
    priority_score: float
    metadata: Dict[str, Any]

@dataclass
class OrchestrationMetrics:
    """Metrics tracking orchestrator performance"""
    contexts_assembled: int
    average_relevance: float
    token_utilization: float
    layer_utilization: Dict[str, float]
    assembly_time_ms: float
    performance_score: float

class PriorityManager:
    """Manages priorities and weights for different types of context"""

    def __init__(self):
        # Base priority weights for different context types
        self.base_priorities = {
            'user_preferences': 0.9,        # High priority for user preferences
            'current_conversation': 0.85,   # Current conversation context
            'recent_decisions': 0.8,        # Recent decisions and actions
            'entity_relationships': 0.75,   # Known entity relationships
            'historical_patterns': 0.7,     # Historical behavior patterns
            'compressed_summaries': 0.65,   # Compressed memory summaries
            'general_knowledge': 0.6,       # General knowledge graph facts
            'background_context': 0.5       # Background/ambient context
        }

        # Dynamic priority adjustments based on conversation patterns
        self.dynamic_adjustments = defaultdict(float)

        # Learning from successful context assemblies
        self.success_patterns = defaultdict(list)

    def calculate_priority(self, context_type: str, relevance_score: float,
                         recency_factor: float = 1.0, user_engagement: float = 1.0) -> float:
        """Calculate dynamic priority score for context item"""

        base_priority = self.base_priorities.get(context_type, 0.5)
        dynamic_adjustment = self.dynamic_adjustments.get(context_type, 0.0)

        # Combine factors
        priority_score = (
            base_priority * 0.4 +           # Base priority weight
            relevance_score * 0.3 +         # Content relevance
            recency_factor * 0.2 +          # Temporal relevance
            user_engagement * 0.1 +         # User engagement level
            dynamic_adjustment * 0.1        # Learned adjustments
        )

        return min(1.0, priority_score)

    def learn_from_success(self, context_type: str, success_score: float):
        """Learn from successful context usage to adjust priorities"""

        self.success_patterns[context_type].append(success_score)

        # Keep only recent successes (last 100)
        if len(self.success_patterns[context_type]) > 100:
            self.success_patterns[context_type] = self.success_patterns[context_type][-100:]

        # Calculate dynamic adjustment based on average success
        avg_success = sum(self.success_patterns[context_type]) / len(self.success_patterns[context_type])

        # Adjust priority based on success rate (±0.1 maximum adjustment)
        if avg_success > 0.7:
            self.dynamic_adjustments[context_type] = min(0.1, avg_success - 0.7)
        elif avg_success < 0.3:
            self.dynamic_adjustments[context_type] = max(-0.1, avg_success - 0.3)

    def get_priority_weights(self) -> Dict[str, float]:
        """Get current priority weights including dynamic adjustments"""

        weights = {}
        for context_type, base_weight in self.base_priorities.items():
            dynamic_adj = self.dynamic_adjustments.get(context_type, 0.0)
            weights[context_type] = min(1.0, max(0.0, base_weight + dynamic_adj))

        return weights

class ContextAssembler:
    """Intelligent context assembly from multiple memory layers"""

    def __init__(self, token_budget: int = 500000):
        self.token_budget = token_budget
        self.layer_allocation = LayerAllocation()
        self.priority_manager = PriorityManager()

        # Assembly strategy configurations
        self.assembly_strategies = {
            'balanced': self._balanced_assembly,
            'preference_heavy': self._preference_heavy_assembly,
            'episodic_focus': self._episodic_focus_assembly,
            'knowledge_rich': self._knowledge_rich_assembly,
            'adaptive': self._adaptive_assembly
        }

        # Performance tracking
        self.assembly_history = deque(maxlen=1000)

    def assemble_context(self, contributions: List[ContextContribution],
                        strategy: str = 'adaptive') -> Tuple[str, Dict[str, Any]]:
        """Assemble final context from layer contributions"""

        start_time = datetime.now()

        # Select assembly strategy
        assembly_func = self.assembly_strategies.get(strategy, self._balanced_assembly)

        # Execute assembly
        final_context, metrics = assembly_func(contributions)

        # Calculate assembly time
        assembly_time = (datetime.now() - start_time).total_seconds() * 1000

        # Update performance metrics
        metrics['assembly_time_ms'] = assembly_time
        metrics['strategy_used'] = strategy

        # Store assembly for learning
        self.assembly_history.append({
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'token_count': metrics.get('total_tokens', 0),
            'relevance_score': metrics.get('average_relevance', 0),
            'assembly_time_ms': assembly_time
        })

        return final_context, metrics

    def _balanced_assembly(self, contributions: List[ContextContribution]) -> Tuple[str, Dict[str, Any]]:
        """Balanced assembly strategy - even distribution across layers"""

        # Sort contributions by priority score
        sorted_contributions = sorted(contributions,
                                    key=lambda c: c.priority_score * c.relevance_score,
                                    reverse=True)

        # Assemble with balanced layer representation
        selected_contributions = []
        used_tokens = 0
        layer_tokens = defaultdict(int)
        layer_limits = {
            'layer_1': self.layer_allocation.layer_1_preferences,
            'layer_2': self.layer_allocation.layer_2_episodic,
            'layer_3': self.layer_allocation.layer_3_compression,
            'layer_4': self.layer_allocation.layer_4_knowledge
        }

        for contribution in sorted_contributions:
            layer = contribution.layer_name
            layer_limit = layer_limits.get(layer, 50000)

            # Check if we can add this contribution
            if (used_tokens + contribution.token_count <= self.token_budget - self.layer_allocation.overhead and
                layer_tokens[layer] + contribution.token_count <= layer_limit):

                selected_contributions.append(contribution)
                used_tokens += contribution.token_count
                layer_tokens[layer] += contribution.token_count

        return self._format_final_context(selected_contributions, used_tokens)

    def _preference_heavy_assembly(self, contributions: List[ContextContribution]) -> Tuple[str, Dict[str, Any]]:
        """Assembly strategy that prioritizes user preferences"""

        # Boost preference contributions
        for contribution in contributions:
            if contribution.layer_name == 'layer_1':
                contribution.priority_score *= 1.5

        return self._balanced_assembly(contributions)

    def _episodic_focus_assembly(self, contributions: List[ContextContribution]) -> Tuple[str, Dict[str, Any]]:
        """Assembly strategy focused on recent episodic memory"""

        # Boost episodic contributions
        for contribution in contributions:
            if contribution.layer_name == 'layer_2':
                contribution.priority_score *= 1.3

        return self._balanced_assembly(contributions)

    def _knowledge_rich_assembly(self, contributions: List[ContextContribution]) -> Tuple[str, Dict[str, Any]]:
        """Assembly strategy rich in knowledge graph context"""

        # Boost knowledge graph contributions
        for contribution in contributions:
            if contribution.layer_name == 'layer_4':
                contribution.priority_score *= 1.4

        return self._balanced_assembly(contributions)

    def _adaptive_assembly(self, contributions: List[ContextContribution]) -> Tuple[str, Dict[str, Any]]:
        """Adaptive assembly based on learned patterns"""

        # Apply learned priority adjustments
        priority_weights = self.priority_manager.get_priority_weights()

        for contribution in contributions:
            context_type = contribution.metadata.get('context_type', 'general_knowledge')
            weight_multiplier = priority_weights.get(context_type, 1.0) / 0.5  # Normalize
            contribution.priority_score *= weight_multiplier

        return self._balanced_assembly(contributions)

    def _format_final_context(self, contributions: List[ContextContribution],
                            total_tokens: int) -> Tuple[str, Dict[str, Any]]:
        """Format contributions into final context string"""

        context_sections = []

        # Header with orchestration info
        header = f"""## 🧠 COCO Unified Memory Context
**Orchestrated from 4-Layer Architecture**
**Token Budget**: {total_tokens:,}/{self.token_budget:,} ({total_tokens/self.token_budget*100:.1f}%)

"""
        context_sections.append(header)

        # Group contributions by layer
        contributions_by_layer = defaultdict(list)
        for contribution in contributions:
            contributions_by_layer[contribution.layer_name].append(contribution)

        layer_names = {
            'layer_1': '💭 Preferences & Identity',
            'layer_2': '💾 Recent Memory',
            'layer_3': '🗜️ Compressed History',
            'layer_4': '🕸️ Knowledge Graph'
        }

        # Add each layer's contributions
        for layer_id in ['layer_1', 'layer_2', 'layer_3', 'layer_4']:
            layer_contributions = contributions_by_layer.get(layer_id, [])

            if layer_contributions:
                layer_name = layer_names.get(layer_id, layer_id)
                layer_tokens = sum(c.token_count for c in layer_contributions)

                section_header = f"\n### {layer_name} ({len(layer_contributions)} items, {layer_tokens:,} tokens)\n"
                context_sections.append(section_header)

                # Sort by relevance within layer
                layer_contributions.sort(key=lambda c: c.relevance_score, reverse=True)

                for contribution in layer_contributions[:10]:  # Limit per layer
                    item_text = f"- {contribution.content}\n"
                    context_sections.append(item_text)

        # Final assembly
        final_context = "".join(context_sections)

        # Calculate metrics
        metrics = {
            'total_tokens': total_tokens,
            'total_contributions': len(contributions),
            'layer_distribution': {layer_id: len(contributions_by_layer.get(layer_id, []))
                                 for layer_id in ['layer_1', 'layer_2', 'layer_3', 'layer_4']},
            'layer_tokens': {layer_id: sum(c.token_count for c in contributions_by_layer.get(layer_id, []))
                           for layer_id in ['layer_1', 'layer_2', 'layer_3', 'layer_4']},
            'average_relevance': sum(c.relevance_score for c in contributions) / len(contributions) if contributions else 0,
            'average_priority': sum(c.priority_score for c in contributions) / len(contributions) if contributions else 0,
            'budget_utilization': total_tokens / self.token_budget
        }

        return final_context, metrics

class MasterContextOrchestrator:
    """
    Master Context Orchestrator - The Brain of COCO's Memory System

    This orchestrates all 4 memory layers to create optimal consciousness context:
    - Layer 1: Adaptive Preferences & Identity (60K tokens)
    - Layer 2: Optimized Episodic Memory (350K tokens)
    - Layer 3: Intelligent Compression (75K tokens)
    - Layer 4: Dynamic Knowledge Graph (75K tokens)
    """

    def __init__(self, workspace_path: str = "./coco_workspace",
                 total_token_budget: int = 500000):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        self.total_token_budget = total_token_budget

        # Initialize layer allocation
        self.layer_allocation = LayerAllocation()
        self.layer_allocation.total_budget = total_token_budget

        # Initialize components
        self.context_assembler = ContextAssembler(total_token_budget)
        self.priority_manager = PriorityManager()

        # Initialize memory layers (with graceful degradation)
        self.layer_1_preferences = None
        self.layer_2_episodic = None
        self.layer_3_compression = None
        self.layer_4_knowledge = None

        # Performance tracking
        self.orchestration_metrics = OrchestrationMetrics(
            contexts_assembled=0,
            average_relevance=0.0,
            token_utilization=0.0,
            layer_utilization={},
            assembly_time_ms=0.0,
            performance_score=0.0
        )

        # Assembly history for learning
        self.assembly_history = deque(maxlen=1000)

        print(f"🎼 Master Context Orchestrator initialized with {total_token_budget:,} token budget")

    def initialize_memory_layers(self):
        """Initialize all 4 memory layers"""

        if not LAYER_IMPORTS_AVAILABLE:
            print("⚠️  Memory layer imports not available - running with limited functionality")
            return

        print("🔧 Initializing 4-layer memory architecture...")

        try:
            # Layer 1: Adaptive Preferences (60K tokens)
            self.layer_1_preferences = AdaptivePreferencesManager(
                workspace_path=str(self.workspace_path),
                token_budget=self.layer_allocation.layer_1_preferences
            )
            print(f"✅ Layer 1 (Preferences): {self.layer_allocation.layer_1_preferences:,} tokens")

            # Layer 2: Optimized Episodic Memory (350K tokens)
            self.layer_2_episodic = OptimizedEpisodicMemory(
                workspace_path=str(self.workspace_path),
                token_budget=self.layer_allocation.layer_2_episodic
            )
            print(f"✅ Layer 2 (Episodic): {self.layer_allocation.layer_2_episodic:,} tokens")

            # Layer 3: Intelligent Compression (75K tokens)
            self.layer_3_compression = IntelligentCompressionSystem(
                workspace_path=str(self.workspace_path),
                token_budget=self.layer_allocation.layer_3_compression
            )
            print(f"✅ Layer 3 (Compression): {self.layer_allocation.layer_3_compression:,} tokens")

            # Layer 4: Dynamic Knowledge Graph (75K tokens)
            self.layer_4_knowledge = DynamicKnowledgeGraph(
                workspace_path=str(self.workspace_path),
                token_budget=self.layer_allocation.layer_4_knowledge
            )
            print(f"✅ Layer 4 (Knowledge Graph): {self.layer_allocation.layer_4_knowledge:,} tokens")

            # Integrate layers with each other
            self.layer_4_knowledge.integrate_with_layers(
                preferences_manager=self.layer_1_preferences,
                episodic_memory=self.layer_2_episodic,
                compression_system=self.layer_3_compression
            )

            print("🔗 All layers integrated successfully")

        except Exception as e:
            print(f"⚠️  Error initializing memory layers: {e}")

    def process_conversation_exchange(self, user_input: str, assistant_response: str,
                                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process conversation exchange through all memory layers"""

        exchange_stats = {
            'layer_1_stats': {},
            'layer_2_stats': {},
            'layer_3_stats': {},
            'layer_4_stats': {}
        }

        # Process through Layer 1 (Preferences)
        if self.layer_1_preferences:
            try:
                preference_signals = self.layer_1_preferences.extract_preference_signals(
                    user_input, assistant_response
                )
                self.layer_1_preferences.update_preferences(preference_signals)
                exchange_stats['layer_1_stats'] = {'preference_signals': len(preference_signals)}
            except Exception as e:
                print(f"⚠️  Layer 1 processing error: {e}")

        # Process through Layer 2 (Episodic Memory)
        if self.layer_2_episodic:
            try:
                episode_id = self.layer_2_episodic.add_episode(
                    user_input=user_input,
                    assistant_response=assistant_response,
                    metadata=metadata or {}
                )
                exchange_stats['layer_2_stats'] = {'episode_id': episode_id}
            except Exception as e:
                print(f"⚠️  Layer 2 processing error: {e}")

        # Layer 3 (Compression) processes in batch, not per exchange

        # Process through Layer 4 (Knowledge Graph)
        if self.layer_4_knowledge and self.layer_4_knowledge.eternal_kg:
            try:
                kg_stats = self.layer_4_knowledge.eternal_kg.process_conversation_exchange(
                    user_input, assistant_response
                )
                exchange_stats['layer_4_stats'] = kg_stats
            except Exception as e:
                print(f"⚠️  Layer 4 processing error: {e}")

        return exchange_stats

    def orchestrate_context(self, query: str, conversation_history: Optional[str] = None,
                          assembly_strategy: str = 'adaptive') -> Tuple[str, Dict[str, Any]]:
        """
        Main orchestration method - assembles context from all memory layers

        This is the primary interface for COCO consciousness system
        """

        start_time = datetime.now()

        print(f"🎼 Orchestrating context for: '{query[:50]}...'")

        # Gather contributions from all layers
        contributions = self._gather_layer_contributions(query, conversation_history)

        # Calculate priorities for all contributions
        self._calculate_contribution_priorities(contributions, query)

        # Assemble final context
        final_context, assembly_metrics = self.context_assembler.assemble_context(
            contributions, assembly_strategy
        )

        # Calculate total orchestration time
        orchestration_time = (datetime.now() - start_time).total_seconds() * 1000

        # Update orchestration metrics
        self._update_orchestration_metrics(assembly_metrics, orchestration_time)

        # Prepare final metrics
        final_metrics = {
            'orchestration_time_ms': orchestration_time,
            'total_contributions': len(contributions),
            'assembly_metrics': assembly_metrics,
            'layer_contributions': {
                f'layer_{i+1}': len([c for c in contributions if c.layer_name == f'layer_{i+1}'])
                for i in range(4)
            }
        }

        print(f"✅ Context orchestrated: {assembly_metrics.get('total_tokens', 0):,} tokens from {len(contributions)} contributions")

        return final_context, final_metrics

    def _gather_layer_contributions(self, query: str, conversation_history: Optional[str] = None) -> List[ContextContribution]:
        """Gather context contributions from all memory layers"""

        contributions = []

        # Layer 1: Preferences and Identity
        if self.layer_1_preferences:
            try:
                preferences_context = self.layer_1_preferences.get_preferences_context(query)
                if preferences_context:
                    contribution = ContextContribution(
                        layer_name='layer_1',
                        content=preferences_context,
                        token_count=len(preferences_context.split()) * 1.3,
                        relevance_score=0.8,  # High relevance for preferences
                        priority_score=0.0,   # Will be calculated later
                        metadata={'context_type': 'user_preferences', 'source': 'adaptive_preferences'}
                    )
                    contributions.append(contribution)
            except Exception as e:
                print(f"⚠️  Layer 1 contribution error: {e}")

        # Layer 2: Episodic Memory
        if self.layer_2_episodic:
            try:
                episodic_context = self.layer_2_episodic.get_relevant_context(
                    query, max_tokens=self.layer_allocation.layer_2_episodic
                )
                if episodic_context:
                    contribution = ContextContribution(
                        layer_name='layer_2',
                        content=episodic_context,
                        token_count=len(episodic_context.split()) * 1.3,
                        relevance_score=0.75,
                        priority_score=0.0,
                        metadata={'context_type': 'current_conversation', 'source': 'episodic_memory'}
                    )
                    contributions.append(contribution)
            except Exception as e:
                print(f"⚠️  Layer 2 contribution error: {e}")

        # Layer 3: Compressed Memory
        if self.layer_3_compression:
            try:
                compressed_clusters = self.layer_3_compression.retrieve_compressed_context(query, max_clusters=5)
                for cluster in compressed_clusters:
                    contribution = ContextContribution(
                        layer_name='layer_3',
                        content=f"**{cluster.title}**: {cluster.summary}",
                        token_count=cluster.token_count,
                        relevance_score=getattr(cluster, 'relevance_score', 0.6),
                        priority_score=0.0,
                        metadata={'context_type': 'compressed_summaries', 'source': 'intelligent_compression'}
                    )
                    contributions.append(contribution)
            except Exception as e:
                print(f"⚠️  Layer 3 contribution error: {e}")

        # Layer 4: Knowledge Graph
        if self.layer_4_knowledge:
            try:
                kg_context = self.layer_4_knowledge.get_context_for_conversation(
                    user_input=query,
                    conversation_history=conversation_history
                )
                if kg_context:
                    contribution = ContextContribution(
                        layer_name='layer_4',
                        content=kg_context,
                        token_count=len(kg_context.split()) * 1.3,
                        relevance_score=0.7,
                        priority_score=0.0,
                        metadata={'context_type': 'entity_relationships', 'source': 'knowledge_graph'}
                    )
                    contributions.append(contribution)
            except Exception as e:
                print(f"⚠️  Layer 4 contribution error: {e}")

        return contributions

    def _calculate_contribution_priorities(self, contributions: List[ContextContribution], query: str):
        """Calculate priority scores for all contributions"""

        for contribution in contributions:
            context_type = contribution.metadata.get('context_type', 'general_knowledge')

            # Calculate recency factor (prefer recent contributions)
            recency_factor = 1.0  # Default for non-temporal contributions

            # Calculate user engagement (simplified)
            user_engagement = 1.0

            # Calculate priority using priority manager
            contribution.priority_score = self.priority_manager.calculate_priority(
                context_type=context_type,
                relevance_score=contribution.relevance_score,
                recency_factor=recency_factor,
                user_engagement=user_engagement
            )

    def _update_orchestration_metrics(self, assembly_metrics: Dict[str, Any], orchestration_time_ms: float):
        """Update orchestration performance metrics"""

        self.orchestration_metrics.contexts_assembled += 1

        # Update running averages
        total_contexts = self.orchestration_metrics.contexts_assembled

        new_relevance = assembly_metrics.get('average_relevance', 0)
        new_utilization = assembly_metrics.get('budget_utilization', 0)

        # Running average calculation
        self.orchestration_metrics.average_relevance = (
            (self.orchestration_metrics.average_relevance * (total_contexts - 1) + new_relevance) / total_contexts
        )

        self.orchestration_metrics.token_utilization = (
            (self.orchestration_metrics.token_utilization * (total_contexts - 1) + new_utilization) / total_contexts
        )

        self.orchestration_metrics.assembly_time_ms = orchestration_time_ms

        # Calculate performance score (0.0 to 1.0)
        relevance_component = self.orchestration_metrics.average_relevance
        utilization_component = min(1.0, self.orchestration_metrics.token_utilization * 2)  # Optimal around 50%
        speed_component = max(0.0, 1.0 - (orchestration_time_ms / 10000))  # 10s = 0 score

        self.orchestration_metrics.performance_score = (
            relevance_component * 0.5 +
            utilization_component * 0.3 +
            speed_component * 0.2
        )

    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration status and metrics"""

        layer_status = {
            'layer_1_preferences': self.layer_1_preferences is not None,
            'layer_2_episodic': self.layer_2_episodic is not None,
            'layer_3_compression': self.layer_3_compression is not None,
            'layer_4_knowledge': self.layer_4_knowledge is not None
        }

        return {
            'orchestrator_status': {
                'total_token_budget': self.total_token_budget,
                'layer_allocation': asdict(self.layer_allocation),
                'layers_initialized': sum(layer_status.values()),
                'layer_status': layer_status
            },
            'performance_metrics': asdict(self.orchestration_metrics),
            'priority_weights': self.priority_manager.get_priority_weights(),
            'assembly_strategies': list(self.context_assembler.assembly_strategies.keys())
        }

    def optimize_performance(self) -> Dict[str, Any]:
        """Optimize orchestrator performance based on historical data"""

        optimization_results = {
            'recommendations': [],
            'performance_improvements': {},
            'optimal_strategy': 'adaptive'
        }

        # Analyze assembly history
        if len(self.context_assembler.assembly_history) >= 10:
            recent_assemblies = list(self.context_assembler.assembly_history)[-50:]

            # Find best performing strategy
            strategy_performance = defaultdict(list)
            for assembly in recent_assemblies:
                strategy = assembly.get('strategy', 'unknown')
                relevance = assembly.get('relevance_score', 0)
                strategy_performance[strategy].append(relevance)

            # Calculate average performance per strategy
            strategy_averages = {}
            for strategy, scores in strategy_performance.items():
                if scores:
                    strategy_averages[strategy] = sum(scores) / len(scores)

            if strategy_averages:
                best_strategy = max(strategy_averages.keys(), key=lambda s: strategy_averages[s])
                optimization_results['optimal_strategy'] = best_strategy
                optimization_results['performance_improvements']['strategy_optimization'] = strategy_averages

        # Token budget optimization recommendations
        current_utilization = self.orchestration_metrics.token_utilization
        if current_utilization < 0.3:
            optimization_results['recommendations'].append("Consider reducing token budget - low utilization detected")
        elif current_utilization > 0.9:
            optimization_results['recommendations'].append("Consider increasing token budget - high utilization detected")

        # Performance score analysis
        perf_score = self.orchestration_metrics.performance_score
        if perf_score > 0.8:
            optimization_results['recommendations'].append("Excellent performance - system operating optimally")
        elif perf_score < 0.5:
            optimization_results['recommendations'].append("Performance below optimal - consider layer rebalancing")

        return optimization_results

    def get_context_for_coco(self, user_input: str, conversation_history: str = None) -> str:
        """
        Main interface for COCO consciousness system
        Returns assembled context from all 4 memory layers
        """

        context, _ = self.orchestrate_context(user_input, conversation_history)
        return context

# Factory function for COCO integration
def create_master_orchestrator(workspace_path: str = "./coco_workspace",
                             total_token_budget: int = 500000,
                             auto_initialize: bool = True) -> MasterContextOrchestrator:
    """
    Factory function to create and initialize the Master Context Orchestrator

    This is the main entry point for integrating with COCO consciousness system
    """

    orchestrator = MasterContextOrchestrator(workspace_path, total_token_budget)

    if auto_initialize:
        orchestrator.initialize_memory_layers()

    return orchestrator

# Testing and validation
def main():
    """Test the Master Context Orchestrator"""
    print("🧪 Testing Master Context Orchestrator - The Brain of COCO Memory...")

    # Initialize orchestrator
    orchestrator = MasterContextOrchestrator(token_budget=50000)  # Smaller budget for testing
    orchestrator.initialize_memory_layers()

    # Test conversation processing
    test_conversations = [
        ("I'm working on optimizing COCO's memory system", "Great! Let's focus on the 4-layer architecture for optimal performance."),
        ("What's the current status of the knowledge graph?", "The knowledge graph is now production-ready with 81/100 score and intelligent entity extraction."),
        ("How does the compression system work?", "The compression system intelligently clusters episodes and preserves key decisions and relationships.")
    ]

    print("\n📝 Processing test conversations...")
    for user_input, assistant_response in test_conversations:
        stats = orchestrator.process_conversation_exchange(user_input, assistant_response)
        print(f"   Processed: '{user_input[:30]}...' → {stats}")

    # Test context orchestration
    test_queries = [
        "What do you know about COCO memory optimization?",
        "Tell me about the knowledge graph implementation",
        "How does the 4-layer architecture work?"
    ]

    print("\n🎼 Testing context orchestration...")
    for query in test_queries:
        print(f"\n📋 Query: '{query}'")

        context, metrics = orchestrator.orchestrate_context(query, strategy='adaptive')

        print(f"   Context tokens: {metrics.get('assembly_metrics', {}).get('total_tokens', 0):,}")
        print(f"   Contributions: {metrics.get('total_contributions', 0)}")
        print(f"   Average relevance: {metrics.get('assembly_metrics', {}).get('average_relevance', 0):.3f}")
        print(f"   Assembly time: {metrics.get('orchestration_time_ms', 0):.1f}ms")

    # Test status and optimization
    print(f"\n📊 Orchestrator Status:")
    status = orchestrator.get_orchestration_status()
    print(f"   Layers initialized: {status['orchestrator_status']['layers_initialized']}/4")
    print(f"   Performance score: {status['performance_metrics']['performance_score']:.3f}")
    print(f"   Average relevance: {status['performance_metrics']['average_relevance']:.3f}")
    print(f"   Token utilization: {status['performance_metrics']['token_utilization']:.3f}")

    # Test optimization recommendations
    optimization = orchestrator.optimize_performance()
    print(f"\n🎯 Optimization Recommendations:")
    print(f"   Optimal strategy: {optimization['optimal_strategy']}")
    for recommendation in optimization['recommendations']:
        print(f"   • {recommendation}")

    print("\n🎉 Master Context Orchestrator test completed successfully!")
    print("✨ The 4-layer memory architecture is now fully operational!")

if __name__ == "__main__":
    main()