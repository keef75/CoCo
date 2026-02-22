#!/usr/bin/env python3
"""
Test Three-Layer Memory System Integration
===========================================

Verifies that all three memory layers are working together:
1. Episodic Buffer (immediate conversation recall)
2. Simple RAG (semantic cross-conversation memory)
3. Markdown Identity (persistent long-term memory)
"""

import sys
from pathlib import Path
from datetime import datetime
from collections import deque

project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def test_three_layer_integration():
    """Test the complete three-layer memory architecture"""

    print("🧪 TESTING THREE-LAYER MEMORY SYSTEM")
    print("="*70)

    # Test Layer 1: Episodic Buffer
    print("\n📝 LAYER 1: EPISODIC BUFFER (Immediate Recall)")
    print("-"*70)

    try:
        from cocoa import HierarchicalMemorySystem, Config

        config = Config()
        memory = HierarchicalMemorySystem(config)

        # Add some test exchanges
        test_exchanges = [
            ("Who is Ilia?", "Ilia is a 15-year friend who attended the RLF Workshop."),
            ("What about Ramin?", "Ramin is an attorney at RLF law firm."),
            ("How are they connected?", "They're connected through the RLF Workshop on AI consciousness."),
        ]

        for user_text, agent_text in test_exchanges:
            memory.insert_episode(user_text, agent_text)

        # Get working memory context
        working_context = memory.get_working_memory_context()

        print(f"✅ Episodic Buffer Active")
        print(f"   Buffer Size: {len(memory.working_memory)} exchanges")
        print(f"   Max Capacity: {memory.working_memory.maxlen}")
        print(f"   Context Length: {len(working_context)} chars")

        # Verify recent exchanges are in context
        if "Ilia" in working_context and "Ramin" in working_context:
            print(f"   ✅ Recent conversation present in context")
        else:
            print(f"   ⚠️ Recent conversation not found in context")

    except Exception as e:
        print(f"❌ Layer 1 Test Failed: {e}")
        import traceback
        traceback.print_exc()

    # Test Layer 2: Simple RAG
    print("\n📚 LAYER 2: SIMPLE RAG (Semantic Memory)")
    print("-"*70)

    try:
        if hasattr(memory, 'simple_rag') and memory.simple_rag:
            rag_stats = memory.simple_rag.get_stats()
            print(f"✅ Simple RAG Active")
            print(f"   Total Memories: {rag_stats['total_memories']}")
            print(f"   Recent (24h): {rag_stats['recent_memories']}")
            print(f"   Most Accessed: {rag_stats['most_accessed']}")

            # Test retrieval
            query = "How are Ilia and Ramin connected?"
            rag_context = memory.simple_rag.get_context(query, k=3)

            if rag_context:
                print(f"   ✅ RAG retrieval working")
                print(f"   Query: '{query}'")
                print(f"   Retrieved: {len(rag_context)} chars")

                # Check if RAG context is injected into working memory context
                full_context = memory.get_working_memory_context()
                if "Relevant Semantic Memory" in full_context:
                    print(f"   ✅ RAG context injected into working memory")
                else:
                    print(f"   ⚠️ RAG context not found in working memory")
            else:
                print(f"   ⚠️ RAG retrieval returned empty")
        else:
            print(f"⚠️ Simple RAG not initialized")

    except Exception as e:
        print(f"❌ Layer 2 Test Failed: {e}")
        import traceback
        traceback.print_exc()

    # Test Layer 3: Markdown Identity
    print("\n📄 LAYER 3: MARKDOWN IDENTITY (Long-term Persistence)")
    print("-"*70)

    try:
        # Check if markdown files exist
        workspace = Path(config.workspace)
        identity_file = workspace / "COCO.md"
        user_profile = workspace / "USER_PROFILE.md"
        prev_conv = workspace / "previous_conversation.md"

        files_found = []
        files_missing = []

        for file_path, name in [
            (identity_file, "COCO.md"),
            (user_profile, "USER_PROFILE.md"),
            (prev_conv, "previous_conversation.md")
        ]:
            if file_path.exists():
                size = file_path.stat().st_size
                files_found.append((name, size))
                print(f"   ✅ {name} exists ({size:,} bytes)")
            else:
                files_missing.append(name)
                print(f"   ⚠️ {name} missing")

        # Test identity context loading
        if hasattr(memory, 'get_identity_context_for_prompt'):
            identity_context = memory.get_identity_context_for_prompt()
            print(f"\n   Identity Context Length: {len(identity_context):,} chars")

            # Check for expected sections
            has_coco = "COCO IDENTITY" in identity_context or "COCO.md" in identity_context
            has_user = "USER PROFILE" in identity_context or "USER_PROFILE.md" in identity_context
            has_prev = "PREVIOUS CONVERSATION" in identity_context or "previous_conversation" in identity_context

            print(f"   {'✅' if has_coco else '⚠️'} COCO identity present")
            print(f"   {'✅' if has_user else '⚠️'} User profile present")
            print(f"   {'✅' if has_prev else '⚠️'} Previous conversation present")

            if has_coco and has_user:
                print(f"\n   ✅ Markdown Identity fully integrated")
            else:
                print(f"\n   ⚠️ Some markdown files not loading")
        else:
            print(f"   ⚠️ get_identity_context_for_prompt() method not found")

    except Exception as e:
        print(f"❌ Layer 3 Test Failed: {e}")
        import traceback
        traceback.print_exc()

    # Integration Test
    print("\n" + "="*70)
    print("🔗 INTEGRATION TEST: All Layers Working Together")
    print("="*70)

    try:
        # Get complete context as COCO would see it
        full_context = memory.get_working_memory_context()

        print(f"\nComplete Context Stats:")
        print(f"  Total Length: {len(full_context):,} chars")

        # Check for presence of each layer
        layers_present = []

        # Layer 1: Should have recent exchanges
        if "User:" in full_context and "Assistant:" in full_context:
            layers_present.append("Layer 1 (Episodic)")

        # Layer 2: Should have semantic memory marker
        if "Semantic Memory" in full_context or "📚" in full_context:
            layers_present.append("Layer 2 (RAG)")

        # Layer 3: Would be in separate identity context
        identity_ctx = memory.get_identity_context_for_prompt() if hasattr(memory, 'get_identity_context_for_prompt') else ""
        if len(identity_ctx) > 1000:
            layers_present.append("Layer 3 (Identity)")

        print(f"\n  Layers Active: {len(layers_present)}/3")
        for layer in layers_present:
            print(f"    ✅ {layer}")

        missing = 3 - len(layers_present)
        if missing > 0:
            print(f"\n  ⚠️ {missing} layer(s) may not be fully integrated")
        else:
            print(f"\n  ✅ ALL THREE LAYERS OPERATIONAL!")

        # Test the critical query
        print("\n" + "="*70)
        print("🎯 CRITICAL TEST: Ilia-Ramin Connection Query")
        print("="*70)

        # Simulate what would happen when user asks this
        query = "How are Ilia and Ramin connected?"

        print(f"\nQuery: '{query}'")
        print(f"\nContext COCO would receive:")

        # Layer 1: Recent conversation
        print(f"\n[Layer 1 - Episodic Buffer]")
        recent = [ex for ex in list(memory.working_memory)[-3:]]
        for ex in recent:
            print(f"  User: {ex['user'][:60]}")
            print(f"  Assistant: {ex['agent'][:60]}")

        # Layer 2: RAG retrieval
        if hasattr(memory, 'simple_rag') and memory.simple_rag:
            print(f"\n[Layer 2 - Semantic Memory]")
            rag_results = memory.simple_rag.retrieve(query, k=3)
            for i, result in enumerate(rag_results, 1):
                print(f"  [{i}] {result[:80]}...")

        # Layer 3: Identity files
        print(f"\n[Layer 3 - Persistent Identity]")
        if len(identity_ctx) > 0:
            print(f"  {len(identity_ctx):,} chars of identity context loaded")
            print(f"  (COCO.md + USER_PROFILE.md + previous_conversation.md)")

        print("\n" + "="*70)
        print("✅ THREE-LAYER MEMORY SYSTEM TEST COMPLETE")
        print("="*70)

        print("\n💡 Summary:")
        print(f"  1. Episodic Buffer: {len(memory.working_memory)} exchanges in memory")
        print(f"  2. Simple RAG: {rag_stats['total_memories']} semantic memories")
        print(f"  3. Markdown Identity: {len(files_found)} files loaded")
        print(f"\n  The three layers complement each other perfectly:")
        print(f"    - Episodic = Precise, immediate recall")
        print(f"    - RAG = Dynamic, semantic connections")
        print(f"    - Identity = Persistent, evolving self")

    except Exception as e:
        print(f"❌ Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_three_layer_integration()
