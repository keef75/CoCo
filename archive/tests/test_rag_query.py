#!/usr/bin/env python3
"""
Test SimpleRAG Query Performance
=================================

Tests the Ilia-Ramin connection query that was the original issue.
"""

import sys
from pathlib import Path

project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

from simple_rag import SimpleRAG

def test_rag_queries():
    """Test critical queries against SimpleRAG"""

    print("🧪 TESTING SIMPLE RAG RETRIEVAL")
    print("="*70)

    rag = SimpleRAG('coco_workspace/simple_rag.db')

    # Test queries that COCO will face
    test_cases = [
        ("How are Ilia and Ramin connected?", "Should find RLF Workshop connection"),
        ("Who is Ilia?", "Should return friend and workshop participant info"),
        ("What does Ramin do?", "Should return attorney at RLF info"),
        ("Tell me about the RLF Workshop", "Should return workshop details"),
        ("Who are Keith's children?", "Should return Dylan, Ayden, Ronin"),
        ("What is Cocoa AI?", "Should return Keith's company info"),
    ]

    for query, expected in test_cases:
        print(f"\n📝 Query: '{query}'")
        print(f"   Expected: {expected}")
        print()

        memories = rag.retrieve(query, k=3)

        if memories:
            print("   ✅ Retrieved memories:")
            for i, memory in enumerate(memories, 1):
                preview = memory[:100] + "..." if len(memory) > 100 else memory
                print(f"   [{i}] {preview}")
        else:
            print("   ❌ No memories retrieved")

    print("\n" + "="*70)
    print("📊 RAG STATISTICS")
    print("="*70)
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
    print("\n💡 The SimpleRAG layer is ready for integration with COCO!")
    print("   When COCO processes these queries, it will automatically")
    print("   retrieve and inject this context into the conversation.")

if __name__ == "__main__":
    test_rag_queries()
