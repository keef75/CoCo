"""
CoCo memory -- hierarchical memory system, facts extraction, RAG, and knowledge graph.

Public API
----------
- HierarchicalMemorySystem (alias: MemorySystem) -- core 3-layer memory
- MarkdownConsciousness -- Layer 3 identity persistence (COCO.md, USER_PROFILE.md, PREFERENCES.md)
- CodeMemory -- persistent code snippet / function library
- ConversationSummary, SummaryBufferMemory -- Layer 2 summary buffer
- FactsMemory, create_facts_memory -- perfect-recall fact storage
- QueryRouter -- intelligent routing between facts and semantic search
- SimpleRAG, SimpleRAGWithOpenAI -- semantic memory with TF-IDF / OpenAI embeddings
"""

from coco.memory.markdown_consciousness import MarkdownConsciousness
from coco.memory.code_memory import CodeMemory
from coco.memory.summary_buffer import ConversationSummary, SummaryBufferMemory
from coco.memory.hierarchical import HierarchicalMemorySystem, MemorySystem
from coco.memory.facts_memory import FactsMemory, create_facts_memory
from coco.memory.query_router import QueryRouter
from coco.memory.simple_rag import SimpleRAG, SimpleRAGWithOpenAI

__all__ = [
    "HierarchicalMemorySystem",
    "MemorySystem",
    "MarkdownConsciousness",
    "CodeMemory",
    "ConversationSummary",
    "SummaryBufferMemory",
    "FactsMemory",
    "create_facts_memory",
    "QueryRouter",
    "SimpleRAG",
    "SimpleRAGWithOpenAI",
]
