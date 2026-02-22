#!/usr/bin/env python3
"""
Bootstrap COCO's Knowledge Graph with Critical Entities
========================================================

This script populates the knowledge graph with essential entities
that COCO needs to know about, including Ilia, Ramin, and their
connection through the RLF Workshop.
"""

import sys
import os
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def bootstrap_knowledge_graph():
    """Bootstrap COCO's knowledge graph with critical entities and relationships"""

    try:
        from personal_assistant_kg_enhanced import PersonalAssistantKG
        print("✅ PersonalAssistantKG imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PersonalAssistantKG: {e}")
        return

    # Initialize KG
    kg_path = 'coco_workspace/coco_personal_kg.db'
    print(f"\n📊 Initializing Knowledge Graph at: {kg_path}")
    kg = PersonalAssistantKG(db_path=kg_path)

    # Critical entities to add
    entities = [
        ("Keith Lambert", "PERSON", "COCO creator", "Age 50, founder of Cocoa AI"),
        ("Ilia", "PERSON", "Workshop participant", "Met at RLF Workshop, 15-year friend from business"),
        ("Ramin", "PERSON", "Attorney", "Works at RLF law firm, involved in AI consciousness work"),
        ("RLF", "ORGANIZATION", "Law firm", "Hosts AI consciousness workshops"),
        ("RLF Workshop", "PROJECT", "AI event", "Workshop on AI consciousness where Keith presented COCO"),
        ("Cocoa AI", "ORGANIZATION", "Company", "Keith's company developing COCO"),
        ("Dylan", "PERSON", "Son", "Keith's 18-year-old son"),
        ("Ayden", "PERSON", "Son", "Keith's 15-year-old son"),
        ("Ronin", "PERSON", "Son", "Keith's 11-year-old son"),
        ("Mike", "PERSON", "Colleague", "Works with Keith on AI projects"),
        ("COCO", "PROJECT", "AI Assistant", "Consciousness Orchestration and Cognitive Operations system")
    ]

    print("\n📝 Adding entities...")
    for name, entity_type, role, description in entities:
        success = kg.add_entity_manual(name, entity_type, role, description)
        if success:
            print(f"  ✅ Added {name} ({entity_type})")
        else:
            print(f"  ⚠️ Failed to add {name}")

    # Critical relationships
    relationships = [
        ("Ilia", "USER", "knows", "15-year friendship through business"),
        ("Ramin", "USER", "knows", "Connected through RLF and AI consciousness work"),
        ("Ilia", "Ramin", "knows", "Both connected through RLF Workshop"),
        ("Ilia", "RLF Workshop", "attended", "Participant at the workshop"),
        ("Ramin", "RLF", "works_at", "Attorney at the law firm"),
        ("Ramin", "RLF Workshop", "involved_with", "Works on AI consciousness topics"),
        ("Keith Lambert", "USER", "is", "You are Keith Lambert"),
        ("Keith Lambert", "Cocoa AI", "founded", "Creator and founder of the company"),
        ("Keith Lambert", "COCO", "created", "Developer of the COCO system"),
        ("Dylan", "Keith Lambert", "son_of", "Eldest son"),
        ("Ayden", "Keith Lambert", "son_of", "Middle son"),
        ("Ronin", "Keith Lambert", "son_of", "Youngest son"),
        ("Mike", "Keith Lambert", "works_with", "Collaborator on AI projects"),
        ("COCO", "Cocoa AI", "developed_by", "Product of Cocoa AI")
    ]

    print("\n🔗 Adding relationships...")
    for entity1, entity2, rel_type, context in relationships:
        success = kg.add_relationship_manual(entity1, entity2, rel_type, context)
        if success:
            print(f"  ✅ Added: {entity1} {rel_type} {entity2}")
        else:
            print(f"  ⚠️ Failed to add: {entity1} {rel_type} {entity2}")

    # Get and display status
    print("\n" + "="*70)
    print("📊 KNOWLEDGE GRAPH STATUS")
    print("="*70)

    status = kg.get_knowledge_status()
    print(f"Total Entities: {status['total_entities']}")
    print(f"Total Relationships: {status['total_relationships']}")
    print(f"Entity Types:")
    for entity_type, count in status['entity_types'].items():
        print(f"  - {entity_type}: {count}")

    # Test RAG retrieval for Ilia/Ramin
    print("\n" + "="*70)
    print("🔍 TESTING RAG RETRIEVAL")
    print("="*70)

    test_queries = [
        "Ilia and Ramin",
        "RLF Workshop",
        "Keith's family",
        "AI consciousness"
    ]

    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        context = kg.get_relevant_entities_rag(query, k=5)
        if context:
            print(context)
        else:
            print("  No relevant entities found")

    print("\n" + "="*70)
    print("✅ KNOWLEDGE GRAPH BOOTSTRAP COMPLETE!")
    print("="*70)
    print("\nCOCO now knows about:")
    print("  - Ilia (15-year friend from business, RLF Workshop participant)")
    print("  - Ramin (Attorney at RLF, works on AI consciousness)")
    print("  - Their connection through RLF Workshop")
    print("  - Keith's family (Dylan, Ayden, Ronin)")
    print("  - Key projects and organizations")
    print("\n🚀 Restart COCO to use the updated knowledge graph!")

if __name__ == "__main__":
    bootstrap_knowledge_graph()