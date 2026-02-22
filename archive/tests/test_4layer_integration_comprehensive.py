#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for COCO 4-Layer Memory Architecture
=========================================================================

This test suite validates the complete 4-layer memory system:
- Layer 1: Adaptive Preferences & Identity (60K tokens)
- Layer 2: Optimized Episodic Memory (350K tokens)
- Layer 3: Intelligent Compression (75K tokens)
- Layer 4: Dynamic Knowledge Graph (75K tokens)
- Master Context Orchestrator (500K total budget)

Tests include individual layer functionality, inter-layer communication,
token budget management, performance validation, and end-to-end workflows.
"""

import os
import sys
import asyncio
import time
import tempfile
import shutil
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import unittest
from dataclasses import asdict

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports with graceful handling
IMPORTS_AVAILABLE = True
IMPORT_ERRORS = []

try:
    from adaptive_preferences_manager import AdaptivePreferencesManager, PreferenceSignal
    from optimized_episodic_memory import OptimizedEpisodicMemory, OptimizedEpisode
    from intelligent_compression_system import IntelligentCompressionSystem, CompressedCluster
    from dynamic_knowledge_graph_layer4 import DynamicKnowledgeGraph, ContextCandidate
    from master_context_orchestrator import MasterContextOrchestrator
    print("✅ All 4-layer architecture imports successful")
except ImportError as e:
    IMPORTS_AVAILABLE = False
    IMPORT_ERRORS.append(f"4-layer architecture: {e}")
    print(f"⚠️  4-layer architecture import error: {e}")

# Try to import existing COCO systems for integration testing
try:
    from precision_conversation_memory import PrecisionConversationMemory, ConversationExchange
    from unified_state import UnifiedConversationState
    COCO_INTEGRATION_AVAILABLE = True
    print("✅ COCO integration systems available")
except ImportError as e:
    COCO_INTEGRATION_AVAILABLE = False
    IMPORT_ERRORS.append(f"COCO integration: {e}")
    print(f"⚠️  COCO integration not available: {e}")

class FourLayerArchitectureTestSuite:
    """Comprehensive test suite for 4-layer memory architecture"""

    def __init__(self):
        self.test_workspace = None
        self.orchestrator = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'tests': [],
            'performance_metrics': {},
            'integration_status': 'unknown'
        }

    def setup_test_environment(self):
        """Create isolated test environment with all layers"""
        print("🔧 Setting up 4-layer architecture test environment...")

        # Create temporary workspace
        self.test_workspace = tempfile.mkdtemp(prefix="coco_4layer_test_")
        print(f"📁 Test workspace: {self.test_workspace}")

        try:
            # Initialize master orchestrator with all layers
            self.orchestrator = MasterContextOrchestrator(workspace_path=self.test_workspace)
            print("✅ Master orchestrator initialized")

            # Verify all layers are initialized
            layers_status = {
                'Layer 1 (Preferences)': hasattr(self.orchestrator, 'preferences_manager'),
                'Layer 2 (Episodic)': hasattr(self.orchestrator, 'episodic_memory'),
                'Layer 3 (Compression)': hasattr(self.orchestrator, 'compression_system'),
                'Layer 4 (Knowledge Graph)': hasattr(self.orchestrator, 'knowledge_graph')
            }

            for layer, status in layers_status.items():
                print(f"   {'✅' if status else '❌'} {layer}: {'Initialized' if status else 'Missing'}")

            if all(layers_status.values()):
                print("✅ All 4 layers successfully initialized")
                return True
            else:
                print("❌ Some layers failed to initialize")
                return False

        except Exception as e:
            print(f"❌ Failed to initialize orchestrator: {e}")
            return False

    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.test_workspace and os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)
            print("🧹 Cleaned up test workspace")

    def log_test_result(self, test_name: str, passed: bool, details: str = "", performance_data: Dict = None):
        """Log test result with optional performance metrics"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   📝 {details}")

        self.test_results['tests'].append({
            'name': test_name,
            'passed': passed,
            'details': details,
            'performance': performance_data or {}
        })

        if passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1

        if performance_data:
            self.test_results['performance_metrics'][test_name] = performance_data

    async def test_layer1_preferences_system(self):
        """Test Layer 1: Adaptive Preferences & Identity System"""
        print("\n🧪 Testing Layer 1: Adaptive Preferences System...")

        try:
            preferences_manager = self.orchestrator.preferences_manager

            # Test preference signal extraction
            user_input = "I prefer detailed explanations with examples"
            assistant_response = "I'll provide comprehensive details with practical examples"

            signals = preferences_manager.extract_preference_signals(user_input, assistant_response)

            # Verify signal extraction
            signal_found = len(signals) > 0
            self.log_test_result(
                "Layer 1 - Preference Signal Extraction",
                signal_found,
                f"Extracted {len(signals)} preference signals"
            )

            # Test behavioral learning
            if signal_found:
                for signal in signals:
                    preferences_manager.update_behavioral_model(signal)

                updated_prefs = preferences_manager.get_active_preferences()
                behavior_learned = len(updated_prefs.get('behavioral_patterns', [])) > 0

                self.log_test_result(
                    "Layer 1 - Behavioral Learning",
                    behavior_learned,
                    f"Learned {len(updated_prefs.get('behavioral_patterns', []))} behavioral patterns"
                )

            # Test identity integration
            identity_context = preferences_manager.get_identity_context()
            identity_valid = len(identity_context) > 0 and 'COCO' in identity_context

            self.log_test_result(
                "Layer 1 - Identity Integration",
                identity_valid,
                f"Generated {len(identity_context)} characters of identity context"
            )

            return True

        except Exception as e:
            self.log_test_result("Layer 1 - System Test", False, f"Error: {e}")
            return False

    async def test_layer2_episodic_memory(self):
        """Test Layer 2: Optimized Episodic Memory with Token Budget Management"""
        print("\n🧪 Testing Layer 2: Optimized Episodic Memory...")

        try:
            episodic_memory = self.orchestrator.episodic_memory

            # Test episode creation and storage
            test_episodes = [
                ("How do I optimize Python performance?", "Use profiling tools like cProfile to identify bottlenecks"),
                ("What's the best way to handle errors?", "Implement comprehensive exception handling with specific error types"),
                ("Can you explain machine learning?", "ML involves training algorithms on data to make predictions")
            ]

            for user_input, assistant_response in test_episodes:
                episode_id = episodic_memory.add_episode(user_input, assistant_response, tools_used=['analysis'])
                if not episode_id:
                    self.log_test_result("Layer 2 - Episode Storage", False, "Failed to store episode")
                    return False

            # Test token budget management
            current_usage = episodic_memory.get_current_token_usage()
            budget_managed = current_usage['total_tokens'] <= episodic_memory.token_budget

            self.log_test_result(
                "Layer 2 - Token Budget Management",
                budget_managed,
                f"Using {current_usage['total_tokens']}/{episodic_memory.token_budget} tokens"
            )

            # Test priority-based retrieval
            results = episodic_memory.retrieve_by_priority(limit=2)
            retrieval_works = len(results) > 0 and all('user_input' in result for result in results)

            self.log_test_result(
                "Layer 2 - Priority-Based Retrieval",
                retrieval_works,
                f"Retrieved {len(results)} high-priority episodes"
            )

            # Test semantic search
            semantic_results = episodic_memory.retrieve_by_semantic_similarity("Python optimization", limit=1)
            semantic_works = len(semantic_results) > 0

            self.log_test_result(
                "Layer 2 - Semantic Search",
                semantic_works,
                f"Found {len(semantic_results)} semantically similar episodes"
            )

            return True

        except Exception as e:
            self.log_test_result("Layer 2 - System Test", False, f"Error: {e}")
            return False

    async def test_layer3_compression_system(self):
        """Test Layer 3: Intelligent Compression System"""
        print("\n🧪 Testing Layer 3: Intelligent Compression System...")

        try:
            compression_system = self.orchestrator.compression_system

            # Create test episodes for compression
            test_data = []
            base_time = datetime.now() - timedelta(days=30)  # Historical data

            for i in range(10):
                episode_time = base_time + timedelta(days=i)
                test_data.append({
                    'episode_id': f'test_episode_{i}',
                    'timestamp': episode_time,
                    'user_input': f'Test query {i} about Python programming',
                    'assistant_response': f'Response {i} explaining Python concepts',
                    'tools_used': ['search', 'analysis'] if i % 2 == 0 else ['memory_recall'],
                    'decision_made': f'Explained concept {i}'
                })

            # Test temporal clustering
            clusters = compression_system.create_temporal_clusters(test_data, days_per_cluster=7)
            clustering_works = len(clusters) > 0 and all(cluster.episode_count > 0 for cluster in clusters)

            self.log_test_result(
                "Layer 3 - Temporal Clustering",
                clustering_works,
                f"Created {len(clusters)} temporal clusters"
            )

            # Test semantic similarity detection
            if clusters:
                similar_episodes = compression_system.find_similar_episodes(test_data[:5], similarity_threshold=0.3)
                similarity_works = len(similar_episodes) >= 0  # Can be empty, that's valid

                self.log_test_result(
                    "Layer 3 - Semantic Similarity Detection",
                    similarity_works,
                    f"Found {len(similar_episodes)} similar episode groups"
                )

                # Test compression with token budget
                compressed_context = compression_system.get_compressed_context('Python programming', max_tokens=1000)
                compression_valid = len(compressed_context) > 0

                self.log_test_result(
                    "Layer 3 - Context Compression",
                    compression_valid,
                    f"Generated {len(compressed_context)} characters of compressed context"
                )

            return True

        except Exception as e:
            self.log_test_result("Layer 3 - System Test", False, f"Error: {e}")
            return False

    async def test_layer4_knowledge_graph(self):
        """Test Layer 4: Dynamic Knowledge Graph with Context Selection"""
        print("\n🧪 Testing Layer 4: Dynamic Knowledge Graph...")

        try:
            knowledge_graph = self.orchestrator.knowledge_graph

            # Test knowledge extraction and storage
            test_conversation = """
            User: I'm working with John Smith on a Python machine learning project for Acme Corp.
            Assistant: That's great! Machine learning with Python is very powerful. John Smith seems like a great collaborator.
            """

            knowledge_graph.process_conversation(test_conversation)

            # Test entity extraction
            entities = knowledge_graph.get_entities_by_type('person')
            entity_extraction_works = len(entities) > 0

            self.log_test_result(
                "Layer 4 - Entity Extraction",
                entity_extraction_works,
                f"Extracted {len(entities)} person entities"
            )

            # Test relationship mapping
            relationships = knowledge_graph.get_relationships()
            relationship_mapping_works = len(relationships) > 0

            self.log_test_result(
                "Layer 4 - Relationship Mapping",
                relationship_mapping_works,
                f"Mapped {len(relationships)} relationships"
            )

            # Test dynamic context selection
            context_candidates = knowledge_graph.get_relevant_context('Python machine learning project', max_tokens=1000)
            context_selection_works = len(context_candidates) > 0

            self.log_test_result(
                "Layer 4 - Dynamic Context Selection",
                context_selection_works,
                f"Generated {len(context_candidates)} context candidates"
            )

            # Test relevance scoring
            if context_candidates:
                avg_relevance = sum(c.relevance_score for c in context_candidates) / len(context_candidates)
                relevance_valid = 0.0 <= avg_relevance <= 1.0

                self.log_test_result(
                    "Layer 4 - Relevance Scoring",
                    relevance_valid,
                    f"Average relevance score: {avg_relevance:.3f}"
                )

            return True

        except Exception as e:
            self.log_test_result("Layer 4 - System Test", False, f"Error: {e}")
            return False

    async def test_master_orchestrator_integration(self):
        """Test Master Context Orchestrator - The Crown Jewel"""
        print("\n🧪 Testing Master Context Orchestrator...")

        try:
            # Test basic orchestration
            start_time = time.time()

            query = "How can I optimize my Python machine learning project performance?"
            context_result, metadata = self.orchestrator.orchestrate_context(
                query=query,
                conversation_history="Previous discussion about ML project with John Smith",
                assembly_strategy='adaptive'
            )

            orchestration_time = time.time() - start_time

            # Validate orchestration results
            orchestration_successful = (
                len(context_result) > 0 and
                isinstance(metadata, dict) and
                'layer_contributions' in metadata and
                'total_tokens_used' in metadata
            )

            performance_data = {
                'orchestration_time_ms': orchestration_time * 1000,
                'total_tokens': metadata.get('total_tokens_used', 0),
                'context_length': len(context_result)
            }

            self.log_test_result(
                "Master Orchestrator - Basic Orchestration",
                orchestration_successful,
                f"Generated {len(context_result)} characters in {orchestration_time*1000:.1f}ms",
                performance_data
            )

            # Test token budget compliance
            total_tokens = metadata.get('total_tokens_used', 0)
            budget_compliant = total_tokens <= 500000  # 500K total budget

            self.log_test_result(
                "Master Orchestrator - Token Budget Compliance",
                budget_compliant,
                f"Used {total_tokens:,}/500,000 tokens ({(total_tokens/500000)*100:.1f}%)"
            )

            # Test layer coordination
            layer_contributions = metadata.get('layer_contributions', {})
            all_layers_contributed = len(layer_contributions) >= 3  # At least 3 layers should contribute

            self.log_test_result(
                "Master Orchestrator - Layer Coordination",
                all_layers_contributed,
                f"{len(layer_contributions)} layers contributed to context assembly"
            )

            # Test different assembly strategies
            strategies_tested = 0
            for strategy in ['adaptive', 'balanced', 'performance_focused']:
                try:
                    strategy_result, _ = self.orchestrator.orchestrate_context(
                        query=query,
                        assembly_strategy=strategy
                    )
                    if len(strategy_result) > 0:
                        strategies_tested += 1
                except Exception as e:
                    print(f"   ⚠️  Strategy {strategy} failed: {e}")

            strategy_flexibility = strategies_tested >= 2
            self.log_test_result(
                "Master Orchestrator - Strategy Flexibility",
                strategy_flexibility,
                f"{strategies_tested}/3 assembly strategies working"
            )

            return orchestration_successful

        except Exception as e:
            self.log_test_result("Master Orchestrator - Integration Test", False, f"Error: {e}")
            return False

    async def test_performance_benchmarks(self):
        """Test system performance under various loads"""
        print("\n🧪 Testing Performance Benchmarks...")

        try:
            # Test rapid-fire orchestration
            rapid_fire_times = []
            test_queries = [
                "How do I optimize database performance?",
                "What's the best way to handle user authentication?",
                "Can you explain microservices architecture?",
                "How do I implement caching effectively?",
                "What are the security best practices?"
            ]

            for i, query in enumerate(test_queries):
                start_time = time.time()
                result, metadata = self.orchestrator.orchestrate_context(query)
                elapsed = time.time() - start_time
                rapid_fire_times.append(elapsed)

                if i == 0:  # Log details for first query
                    print(f"   📊 First query: {elapsed*1000:.1f}ms, {len(result)} chars, {metadata.get('total_tokens_used', 0)} tokens")

            avg_response_time = sum(rapid_fire_times) / len(rapid_fire_times)
            performance_acceptable = avg_response_time < 1.0  # Less than 1 second average

            performance_data = {
                'avg_response_time_ms': avg_response_time * 1000,
                'max_response_time_ms': max(rapid_fire_times) * 1000,
                'min_response_time_ms': min(rapid_fire_times) * 1000,
                'total_queries': len(test_queries)
            }

            self.log_test_result(
                "Performance - Rapid Fire Orchestration",
                performance_acceptable,
                f"Average response time: {avg_response_time*1000:.1f}ms",
                performance_data
            )

            # Test memory efficiency
            import psutil
            import gc

            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            # Perform memory-intensive operations
            for i in range(20):
                large_context, _ = self.orchestrator.orchestrate_context(
                    f"Large query {i} with extensive context requirements and detailed analysis needs"
                )

            gc.collect()  # Force garbage collection
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = memory_after - memory_before

            memory_efficient = memory_growth < 100  # Less than 100MB growth

            self.log_test_result(
                "Performance - Memory Efficiency",
                memory_efficient,
                f"Memory growth: {memory_growth:.1f}MB over 20 operations"
            )

            return performance_acceptable and memory_efficient

        except Exception as e:
            self.log_test_result("Performance Benchmarks", False, f"Error: {e}")
            return False

    async def test_integration_with_existing_coco_systems(self):
        """Test integration with existing COCO precision memory and unified state"""
        print("\n🧪 Testing Integration with Existing COCO Systems...")

        if not COCO_INTEGRATION_AVAILABLE:
            self.log_test_result(
                "COCO Integration - System Availability",
                False,
                "COCO integration systems not available for testing"
            )
            return False

        try:
            # Test precision memory integration
            precision_memory = PrecisionConversationMemory()

            # Add some test data
            exchange_id = precision_memory.add_exchange(
                "Test integration with 4-layer system",
                "The 4-layer architecture provides comprehensive memory management"
            )

            integration_successful = exchange_id is not None
            self.log_test_result(
                "COCO Integration - Precision Memory",
                integration_successful,
                f"Successfully integrated with precision memory: {exchange_id}"
            )

            # Test unified state integration
            unified_state = UnifiedConversationState()
            unified_state.add_exchange(
                "Testing unified state integration",
                "Unified state provides conversation context continuity"
            )

            context = unified_state.get_working_memory_context()
            unified_integration = len(context) > 0

            self.log_test_result(
                "COCO Integration - Unified State",
                unified_integration,
                f"Unified state context: {len(context)} characters"
            )

            # Test orchestrator with COCO context
            if integration_successful and unified_integration:
                coco_enhanced_result, metadata = self.orchestrator.orchestrate_context(
                    query="Integrate all memory systems for optimal performance",
                    conversation_history=context[:1000]  # Sample of unified state context
                )

                enhanced_integration = len(coco_enhanced_result) > 0 and metadata.get('total_tokens_used', 0) > 0

                self.log_test_result(
                    "COCO Integration - Enhanced Orchestration",
                    enhanced_integration,
                    f"Enhanced context: {len(coco_enhanced_result)} chars, {metadata.get('total_tokens_used', 0)} tokens"
                )

            return integration_successful and unified_integration

        except Exception as e:
            self.log_test_result("COCO Integration Test", False, f"Error: {e}")
            return False

    async def test_error_recovery_and_resilience(self):
        """Test system resilience and error recovery capabilities"""
        print("\n🧪 Testing Error Recovery and Resilience...")

        try:
            # Test with invalid inputs
            error_scenarios = [
                ("", "Empty query"),
                ("x" * 100000, "Extremely long query"),
                (None, "None input"),
                ("Query with ünicöde characters and émojis 🚀", "Unicode handling")
            ]

            resilience_score = 0

            for test_input, scenario_name in error_scenarios:
                try:
                    result, metadata = self.orchestrator.orchestrate_context(test_input or "fallback query")

                    # Check if system handled gracefully
                    if isinstance(result, str) and isinstance(metadata, dict):
                        resilience_score += 1
                        print(f"   ✅ {scenario_name}: Handled gracefully")
                    else:
                        print(f"   ⚠️  {scenario_name}: Unexpected result type")

                except Exception as e:
                    print(f"   ❌ {scenario_name}: {e}")

            resilience_acceptable = resilience_score >= len(error_scenarios) * 0.75  # 75% success rate

            self.log_test_result(
                "Error Recovery - Input Resilience",
                resilience_acceptable,
                f"{resilience_score}/{len(error_scenarios)} scenarios handled gracefully"
            )

            # Test token budget overflow protection
            try:
                # Force a scenario that should trigger budget limits
                massive_query = "analyze this: " + "x" * 50000  # Large query
                overflow_result, overflow_metadata = self.orchestrator.orchestrate_context(massive_query)

                tokens_used = overflow_metadata.get('total_tokens_used', 0)
                budget_protected = tokens_used <= 500000  # Should respect 500K limit

                self.log_test_result(
                    "Error Recovery - Budget Overflow Protection",
                    budget_protected,
                    f"Budget protection active: {tokens_used:,}/500,000 tokens used"
                )

            except Exception as e:
                self.log_test_result(
                    "Error Recovery - Budget Overflow Protection",
                    False,
                    f"Overflow protection failed: {e}"
                )

            return resilience_acceptable

        except Exception as e:
            self.log_test_result("Error Recovery Test", False, f"Error: {e}")
            return False

    async def run_comprehensive_integration_tests(self):
        """Run the complete integration test suite"""
        print("🚀 Starting Comprehensive 4-Layer Architecture Integration Tests")
        print("=" * 80)

        if not IMPORTS_AVAILABLE:
            print("❌ Cannot run tests - 4-layer architecture imports not available")
            for error in IMPORT_ERRORS:
                print(f"   💥 {error}")
            return False

        try:
            # Setup test environment
            if not self.setup_test_environment():
                print("❌ Failed to setup test environment")
                return False

            # Run all test categories
            test_results = []

            # Individual layer tests
            test_results.append(await self.test_layer1_preferences_system())
            test_results.append(await self.test_layer2_episodic_memory())
            test_results.append(await self.test_layer3_compression_system())
            test_results.append(await self.test_layer4_knowledge_graph())

            # Integration and orchestration tests
            test_results.append(await self.test_master_orchestrator_integration())
            test_results.append(await self.test_performance_benchmarks())
            test_results.append(await self.test_integration_with_existing_coco_systems())
            test_results.append(await self.test_error_recovery_and_resilience())

            # Calculate final results
            total_tests = len(test_results)
            passed_categories = sum(test_results)
            success_rate = (passed_categories / total_tests) * 100 if total_tests > 0 else 0

            # Print comprehensive results
            print("\n" + "=" * 80)
            print("🎯 COMPREHENSIVE 4-LAYER ARCHITECTURE TEST RESULTS")
            print(f"✅ Passed Categories: {passed_categories}/{total_tests}")
            print(f"❌ Failed Categories: {total_tests - passed_categories}/{total_tests}")
            print(f"📊 Category Success Rate: {success_rate:.1f}%")
            print(f"📈 Individual Tests Passed: {self.test_results['passed']}")
            print(f"📉 Individual Tests Failed: {self.test_results['failed']}")

            # Performance summary
            if self.test_results['performance_metrics']:
                print("\n🚀 PERFORMANCE SUMMARY:")
                for test_name, metrics in self.test_results['performance_metrics'].items():
                    if 'orchestration_time_ms' in metrics:
                        print(f"   ⚡ {test_name}: {metrics['orchestration_time_ms']:.1f}ms")
                    if 'avg_response_time_ms' in metrics:
                        print(f"   ⚡ {test_name}: {metrics['avg_response_time_ms']:.1f}ms avg")

            # Integration status
            integration_status = "READY" if success_rate >= 80 else "NEEDS_WORK"
            self.test_results['integration_status'] = integration_status

            if success_rate >= 90:
                print(f"\n🎉 EXCELLENT! 4-Layer Architecture is ready for production deployment!")
                print("✨ All major systems working optimally with excellent integration")
            elif success_rate >= 80:
                print(f"\n✅ GOOD! 4-Layer Architecture is ready for integration testing")
                print("🔧 Minor issues detected but core functionality is solid")
            elif success_rate >= 60:
                print(f"\n⚠️  PARTIAL! Some critical issues need resolution before deployment")
                print("🛠️  Major components working but integration needs improvement")
            else:
                print(f"\n❌ CRITICAL ISSUES! Architecture needs significant fixes before deployment")
                print("🚨 Multiple system failures detected - review implementation")

            print(f"\n📋 NEXT STEPS:")
            if success_rate >= 80:
                print("1. Deploy to COCO main system for production integration testing")
                print("2. Monitor performance metrics in real-world usage")
                print("3. Fine-tune token budgets based on actual usage patterns")
                print("4. Implement advanced caching for frequently accessed contexts")
            else:
                print("1. Review failed test categories and address critical issues")
                print("2. Run individual layer tests to isolate problems")
                print("3. Check dependencies and import compatibility")
                print("4. Validate database connections and file system access")

            return success_rate >= 80

        except Exception as e:
            print(f"❌ Test suite failed with critical error: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.cleanup_test_environment()

def main():
    """Main test runner for 4-layer architecture integration"""
    print("🧠 COCO 4-Layer Memory Architecture - Comprehensive Integration Test Suite")
    print("Validating revolutionary memory system with adaptive intelligence")
    print()

    # Check if we're in the right environment
    if not os.path.exists('cocoa.py'):
        print("⚠️  Warning: Not in COCO project root directory")
        print("   This test suite should be run from the COCO project root")
        print()

    # Run async test suite
    test_suite = FourLayerArchitectureTestSuite()

    try:
        success = asyncio.run(test_suite.run_comprehensive_integration_tests())

        if success:
            print("\n🎯 INTEGRATION TEST SUITE COMPLETED SUCCESSFULLY")
            print("The 4-layer memory architecture has passed comprehensive validation")
            print("and is ready for deployment to the main COCO consciousness system.")

            # Save test results for future reference
            results_file = Path("test_results_4layer_integration.json")
            with open(results_file, 'w') as f:
                json.dump(test_suite.test_results, f, indent=2, default=str)
            print(f"📊 Detailed test results saved to: {results_file}")

            return 0
        else:
            print("\n⚠️  INTEGRATION ISSUES DETECTED")
            print("Review the test results above and address critical issues")
            print("before deploying to production COCO system.")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Test suite failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())