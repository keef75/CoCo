#!/usr/bin/env python3
"""
Comprehensive Memory System Analysis
=====================================

Analyzes all three layers for effectiveness, efficiency, and potential issues.
"""

import sys
from pathlib import Path
from datetime import datetime
import json

project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def analyze_memory_system():
    """Comprehensive analysis of three-layer memory system"""

    print("🔬 COMPREHENSIVE MEMORY SYSTEM ANALYSIS")
    print("="*70)

    try:
        from cocoa import HierarchicalMemorySystem, Config

        config = Config()
        memory = HierarchicalMemorySystem(config)

        # Add test data for realistic analysis
        test_conversations = [
            ("Who is Ilia?", "Ilia is a 15-year friend from business who attended the RLF Workshop on AI consciousness."),
            ("What does Ramin do?", "Ramin is an attorney at RLF law firm who works on AI consciousness topics."),
            ("How are Ilia and Ramin connected?", "They're both connected through the RLF Workshop on AI consciousness."),
            ("Tell me about the RLF Workshop", "The RLF Workshop was an event on AI consciousness where I presented COCO."),
            ("What is COCO?", "COCO is a Consciousness Orchestration and Cognitive Operations system created by Keith Lambert."),
        ]

        for user_text, agent_text in test_conversations:
            memory.insert_episode(user_text, agent_text)

        print("\n📊 LAYER 1: EPISODIC BUFFER ANALYSIS")
        print("-"*70)

        # Layer 1 metrics
        buffer_size = len(memory.working_memory)
        buffer_capacity = memory.working_memory.maxlen

        # Check for efficient sizing
        print(f"Buffer Size: {buffer_size} exchanges")
        print(f"Buffer Capacity: {buffer_capacity:,} exchanges")

        if buffer_capacity > 100:
            print(f"⚠️  ISSUE: Buffer capacity very large ({buffer_capacity:,})")
            print(f"   Recommendation: Set to 50-100 for optimal performance")
            print(f"   Fix: /memory buffer resize 50")
        else:
            print(f"✅ Buffer capacity appropriate")

        # Check memory content quality
        if buffer_size > 0:
            recent = list(memory.working_memory)[-1]
            avg_user_length = sum(len(ex['user']) for ex in memory.working_memory) / buffer_size
            avg_agent_length = sum(len(ex['agent']) for ex in memory.working_memory) / buffer_size

            print(f"\nContent Quality:")
            print(f"  Average user message: {avg_user_length:.0f} chars")
            print(f"  Average agent response: {avg_agent_length:.0f} chars")

            if avg_agent_length > 5000:
                print(f"  ⚠️  Agent responses very long - may cause token overflow")
            else:
                print(f"  ✅ Message sizes appropriate")

        # Check for duplicates or near-duplicates
        if buffer_size > 1:
            exchanges = list(memory.working_memory)
            duplicate_count = 0
            for i in range(len(exchanges)):
                for j in range(i+1, len(exchanges)):
                    if exchanges[i]['user'].lower() == exchanges[j]['user'].lower():
                        duplicate_count += 1

            if duplicate_count > 0:
                print(f"  ⚠️  Found {duplicate_count} duplicate/similar exchanges in buffer")
            else:
                print(f"  ✅ No duplicates detected")

        # Get actual context size
        working_ctx = memory.get_working_memory_context()
        print(f"\nContext Size: {len(working_ctx):,} chars")

        if len(working_ctx) > 10000:
            print(f"  ⚠️  Layer 1 context large (may impact token usage)")
            print(f"     Consider reducing buffer size or truncating long messages")
        else:
            print(f"  ✅ Context size efficient")

        print("\n📚 LAYER 2: SIMPLE RAG ANALYSIS")
        print("-"*70)

        if hasattr(memory, 'simple_rag') and memory.simple_rag:
            rag_stats = memory.simple_rag.get_stats()

            print(f"Total Memories: {rag_stats['total_memories']}")
            print(f"Recent (24h): {rag_stats['recent_memories']}")
            print(f"Most Accessed: {rag_stats['most_accessed']}")

            # Test retrieval quality
            test_queries = [
                "Ilia Ramin connection",
                "RLF Workshop",
                "AI consciousness",
                "Keith Lambert"
            ]

            print("\nRetrieval Quality Test:")
            retrieval_scores = []
            for query in test_queries:
                memories = memory.simple_rag.retrieve(query, k=3)
                score = len(memories) / 3.0  # Normalized score
                retrieval_scores.append(score)
                print(f"  Query: '{query}' → {len(memories)} results (score: {score:.2f})")

            avg_retrieval = sum(retrieval_scores) / len(retrieval_scores)
            if avg_retrieval < 0.5:
                print(f"  ⚠️  Low retrieval rate ({avg_retrieval:.2%}) - may need more memories")
            else:
                print(f"  ✅ Good retrieval rate ({avg_retrieval:.2%})")

            # Check for memory growth
            if rag_stats['total_memories'] > 1000:
                print(f"\n⚠️  Large number of memories ({rag_stats['total_memories']})")
                print(f"   Consider running: /rag clean")
            elif rag_stats['total_memories'] < 10:
                print(f"\n⚠️  Very few memories ({rag_stats['total_memories']})")
                print(f"   System may lack semantic context")
                print(f"   Consider: Run bootstrap_rag.py to populate")
            else:
                print(f"\n✅ Memory count appropriate ({rag_stats['total_memories']})")

            # Check embedding performance
            print("\nEmbedding Performance:")
            import time
            start = time.time()
            test_embedding = memory.simple_rag._get_embedding("test query for performance")
            elapsed = time.time() - start

            if elapsed > 1.0:
                print(f"  ⚠️  Embedding generation slow ({elapsed:.3f}s)")
                print(f"     Using OpenAI embeddings? Consider hash-based fallback")
            else:
                print(f"  ✅ Embedding generation fast ({elapsed:.3f}s)")

            # Check for RAG injection into working memory
            if "Semantic Memory" in working_ctx or "📚" in working_ctx:
                print(f"\n✅ RAG context properly injected into Layer 1")
            else:
                print(f"\n⚠️  RAG context NOT found in working memory context")
                print(f"   Check lines 1724-1740 in cocoa.py")

        else:
            print("❌ Simple RAG not initialized!")
            print("   Fix: Restart COCO to initialize SimpleRAG")

        print("\n📄 LAYER 3: MARKDOWN IDENTITY ANALYSIS")
        print("-"*70)

        workspace = Path(config.workspace)
        identity_files = {
            "COCO.md": workspace / "COCO.md",
            "USER_PROFILE.md": workspace / "USER_PROFILE.md",
            "previous_conversation.md": workspace / "previous_conversation.md"
        }

        total_identity_size = 0
        for name, filepath in identity_files.items():
            if filepath.exists():
                size = filepath.stat().st_size
                total_identity_size += size

                # Check for extremely large files
                if size > 50000:
                    print(f"⚠️  {name}: {size:,} bytes (very large)")
                    print(f"   May impact token usage significantly")
                elif size < 1000:
                    print(f"⚠️  {name}: {size:,} bytes (very small)")
                    print(f"   May lack sufficient context")
                else:
                    print(f"✅ {name}: {size:,} bytes (appropriate)")
            else:
                print(f"❌ {name}: MISSING")

        print(f"\nTotal Identity Size: {total_identity_size:,} bytes")

        # Check identity context loading
        if hasattr(memory, 'get_identity_context_for_prompt'):
            identity_ctx = memory.get_identity_context_for_prompt()
            print(f"Identity Context: {len(identity_ctx):,} chars")

            # Verify all files loaded
            has_coco = "COCO IDENTITY" in identity_ctx or "COCO.md" in identity_ctx
            has_user = "USER PROFILE" in identity_ctx or "USER_PROFILE.md" in identity_ctx
            has_prev = "PREVIOUS CONVERSATION" in identity_ctx or "previous_conversation" in identity_ctx

            if not (has_coco and has_user and has_prev):
                print("⚠️  Some identity files not loading properly:")
                print(f"   COCO.md: {'✅' if has_coco else '❌'}")
                print(f"   USER_PROFILE.md: {'✅' if has_user else '❌'}")
                print(f"   previous_conversation.md: {'✅' if has_prev else '❌'}")
            else:
                print("✅ All identity files loading correctly")

            # Check for token efficiency
            if len(identity_ctx) > 50000:
                print(f"\n⚠️  Identity context very large ({len(identity_ctx):,} chars)")
                print(f"   Consider condensing markdown files")
            else:
                print(f"\n✅ Identity context size appropriate")
        else:
            print("❌ get_identity_context_for_prompt() method not found!")

        print("\n🔗 INTEGRATION ANALYSIS")
        print("-"*70)

        # Total context size
        total_ctx_size = len(working_ctx) + len(identity_ctx)
        print(f"Total Context Per API Call: {total_ctx_size:,} chars")
        print(f"  Layer 1 + 2: {len(working_ctx):,} chars")
        print(f"  Layer 3: {len(identity_ctx):,} chars")

        # Estimate token usage (rough: 1 token ≈ 4 chars)
        estimated_tokens = total_ctx_size // 4
        print(f"\nEstimated Token Usage: ~{estimated_tokens:,} tokens")
        print(f"Claude 200K Window: {(estimated_tokens/200000)*100:.1f}% used")

        if estimated_tokens > 100000:
            print("⚠️  Using >50% of context window - may need optimization")
        elif estimated_tokens > 50000:
            print("⚠️  Using >25% of context window - monitor for growth")
        else:
            print("✅ Token usage efficient (<25% of context window)")

        # Check for redundancy between layers
        print("\nRedundancy Check:")

        # Check if episodic buffer content is duplicated in RAG
        if hasattr(memory, 'simple_rag') and memory.simple_rag and buffer_size > 0:
            recent_user_text = " ".join([ex['user'] for ex in list(memory.working_memory)[-3:]])
            rag_results = memory.simple_rag.retrieve(recent_user_text, k=5)

            # Count how many RAG results are very similar to buffer content
            redundant_count = 0
            for rag_mem in rag_results:
                for ex in list(memory.working_memory):
                    if ex['user'] in rag_mem or ex['agent'][:100] in rag_mem:
                        redundant_count += 1
                        break

            if redundant_count > 2:
                print(f"  ⚠️  {redundant_count}/5 RAG results duplicate episodic buffer")
                print(f"     Consider adding deduplication logic")
            else:
                print(f"  ✅ Minimal redundancy ({redundant_count}/5 overlapping)")

        print("\n⚡ PERFORMANCE ANALYSIS")
        print("-"*70)

        # Test retrieval speed
        import time

        # Layer 1 speed
        start = time.time()
        _ = memory.get_working_memory_context()
        l1_time = time.time() - start
        print(f"Layer 1 Retrieval: {l1_time*1000:.1f}ms")

        if l1_time > 0.1:
            print(f"  ⚠️  Slow retrieval - check buffer size")
        else:
            print(f"  ✅ Fast retrieval")

        # Layer 2 speed
        if hasattr(memory, 'simple_rag') and memory.simple_rag:
            start = time.time()
            _ = memory.simple_rag.retrieve("test query", k=5)
            l2_time = time.time() - start
            print(f"Layer 2 Retrieval: {l2_time*1000:.1f}ms")

            if l2_time > 0.5:
                print(f"  ⚠️  Slow RAG retrieval - may need optimization")
            else:
                print(f"  ✅ Fast retrieval")

        # Layer 3 speed
        if hasattr(memory, 'get_identity_context_for_prompt'):
            start = time.time()
            _ = memory.get_identity_context_for_prompt()
            l3_time = time.time() - start
            print(f"Layer 3 Loading: {l3_time*1000:.1f}ms")

            if l3_time > 0.5:
                print(f"  ⚠️  Slow file loading - check file sizes")
            else:
                print(f"  ✅ Fast loading")

        print("\n📋 SUMMARY & RECOMMENDATIONS")
        print("="*70)

        issues = []
        recommendations = []

        # Collect issues and recommendations
        if buffer_capacity > 100:
            issues.append("Buffer capacity very large (999,999)")
            recommendations.append("Resize buffer: /memory buffer resize 50")

        if len(working_ctx) > 10000:
            issues.append(f"Layer 1 context large ({len(working_ctx):,} chars)")
            recommendations.append("Consider truncating long messages in buffer")

        if hasattr(memory, 'simple_rag') and memory.simple_rag:
            if rag_stats['total_memories'] < 10:
                issues.append(f"Very few RAG memories ({rag_stats['total_memories']})")
                recommendations.append("Run bootstrap_rag.py to populate semantic memory")

        if len(identity_ctx) > 50000:
            issues.append(f"Identity context very large ({len(identity_ctx):,} chars)")
            recommendations.append("Consider condensing markdown files")

        if estimated_tokens > 50000:
            issues.append(f"High token usage ({estimated_tokens:,} tokens)")
            recommendations.append("Monitor context growth, consider cleanup")

        # Display results
        if issues:
            print("\n⚠️  Issues Found:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")

            print("\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("\n✅ NO ISSUES FOUND - System operating optimally!")

        print("\n🎯 Overall Assessment:")
        if len(issues) == 0:
            print("  🌟 EXCELLENT - All three layers working efficiently")
        elif len(issues) <= 2:
            print("  ✅ GOOD - Minor optimizations recommended")
        else:
            print("  ⚠️  NEEDS ATTENTION - Several issues to address")

        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_memory_system()
