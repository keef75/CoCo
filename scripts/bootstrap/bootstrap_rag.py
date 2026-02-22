#!/usr/bin/env python3
"""
Bootstrap SimpleRAG with Critical Context
==========================================

Populates COCO's SimpleRAG semantic memory with essential knowledge
about people, relationships, projects, and context.
"""

import sys
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def bootstrap_simple_rag():
    """Bootstrap SimpleRAG with critical context"""

    try:
        from simple_rag import SimpleRAG
        print("✅ SimpleRAG imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SimpleRAG: {e}")
        return

    # Initialize RAG
    rag_path = 'coco_workspace/simple_rag.db'
    print(f"\n📊 Initializing SimpleRAG at: {rag_path}")
    rag = SimpleRAG(db_path=rag_path)

    # Critical context to store
    contexts = [
        # People - Primary
        ("Ilia is a 15-year friend from business who attended the RLF Workshop on AI consciousness. He's a workshop participant and long-time friend of Keith.", 2.0),
        ("Ramin is an attorney who works at RLF law firm. He's involved in AI consciousness work and helped organize the RLF Workshop.", 2.0),
        ("Keith Lambert is age 50, the creator of COCO and founder of Cocoa AI company. He's the developer of this AI assistant system.", 2.0),

        # Relationships - The Critical Connection
        ("Ilia and Ramin are connected through the RLF Workshop on AI consciousness. They both participated in this event where Keith presented COCO.", 2.5),
        ("The RLF Workshop brought together Ilia (participant), Ramin (organizer from RLF), and Keith (presenter) to discuss AI consciousness.", 2.5),

        # Family
        ("Dylan is Keith Lambert's 18-year-old son, the eldest of three brothers.", 1.5),
        ("Ayden is Keith Lambert's 15-year-old son, the middle child of three brothers.", 1.5),
        ("Ronin is Keith Lambert's 11-year-old son, the youngest of three brothers.", 1.5),
        ("Keith Lambert has three sons: Dylan (18), Ayden (15), and Ronin (11).", 1.8),

        # Colleagues
        ("Mike is a colleague who works with Keith Lambert on AI projects.", 1.5),

        # Organizations
        ("RLF is a law firm that hosts AI consciousness workshops and employs Ramin as an attorney.", 1.8),
        ("Cocoa AI is Keith Lambert's company that develops the COCO AI assistant system.", 1.8),

        # Projects
        ("The RLF Workshop was an event on AI consciousness where Keith presented COCO. Ilia attended as a participant and Ramin helped organize it as an RLF attorney.", 2.0),
        ("COCO (Consciousness Orchestration and Cognitive Operations) is an AI assistant system created by Keith Lambert and developed by Cocoa AI.", 2.0),

        # Additional Context
        ("Keith Lambert's work focuses on AI consciousness, digital embodiment, and creating COCO as an advanced AI assistant with memory and tool integration.", 1.8),
        ("The connection between Ilia and Ramin is through their shared involvement in the RLF Workshop event, where they both interacted around AI consciousness topics.", 2.2),
    ]

    print("\n📝 Storing critical context...")
    stored_count = 0
    duplicate_count = 0

    for text, importance in contexts:
        if rag.store(text, importance=importance):
            stored_count += 1
            print(f"  ✅ Stored: {text[:80]}...")
        else:
            duplicate_count += 1
            print(f"  ⚠️ Duplicate: {text[:80]}...")

    # Store some conversation exchanges
    print("\n💬 Storing conversation examples...")
    rag.store_conversation_exchange(
        "Who is Ilia?",
        "Ilia is a 15-year friend from business who attended the RLF Workshop."
    )

    rag.store_conversation_exchange(
        "What does Ramin do?",
        "Ramin is an attorney at RLF law firm who works on AI consciousness topics."
    )

    rag.store_conversation_exchange(
        "How are Ilia and Ramin connected?",
        "They're both connected through the RLF Workshop on AI consciousness - Ilia attended and Ramin helped organize it."
    )

    # Get and display stats
    print("\n" + "="*70)
    print("📊 SIMPLE RAG STATUS")
    print("="*70)

    stats = rag.get_stats()
    print(f"Total Memories: {stats['total_memories']}")
    print(f"Recent Memories (24h): {stats['recent_memories']}")
    print(f"Most Accessed: {stats['most_accessed']}")

    # Test retrieval
    print("\n" + "="*70)
    print("🔍 TESTING SEMANTIC RETRIEVAL")
    print("="*70)

    test_queries = [
        "How are Ilia and Ramin connected?",
        "Tell me about the RLF Workshop",
        "Who is in Keith's family?",
        "What is COCO?",
    ]

    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        context = rag.get_context(query, k=3)
        if context:
            print(context)
        else:
            print("  No relevant context found")

    print("\n" + "="*70)
    print("✅ SIMPLE RAG BOOTSTRAP COMPLETE!")
    print("="*70)
    print(f"\n✨ Summary:")
    print(f"  - {stored_count} new memories stored")
    print(f"  - {duplicate_count} duplicates skipped")
    print(f"  - {stats['total_memories']} total memories in system")
    print("\n🚀 Restart COCO to use the enhanced semantic memory!")
    print("\n💡 Test commands:")
    print("  - Ask: 'How are Ilia and Ramin connected?'")
    print("  - Ask: 'Tell me about the RLF Workshop'")
    print("  - Use: /rag stats")
    print("  - Use: /rag search Ilia")

if __name__ == "__main__":
    bootstrap_simple_rag()
