"""
CoCo Constants - Centralized constants extracted from cocoa.py.

All magic numbers, model identifiers, thresholds, and static configuration
values live here so they can be imported by any module without pulling in
heavy runtime dependencies.  API keys and user-configurable settings
remain in ``Config`` / ``.env``.
"""

# ---------------------------------------------------------------------------
# Model Identifiers
# ---------------------------------------------------------------------------

# Primary conversation model (Claude Sonnet 4.5 - latest, no beta features)
PRIMARY_MODEL = "claude-sonnet-4-5-20250929"

# Summarisation model used for buffer compression
SUMMARIZATION_MODEL = "claude-sonnet-4-5"

# Embedding model (OpenAI) used by Simple RAG
EMBEDDING_MODEL = "text-embedding-3-small"

# Fast extraction model used by Knowledge Graph
KG_EXTRACTION_MODEL = "claude-3-haiku"

# ---------------------------------------------------------------------------
# Context Window
# ---------------------------------------------------------------------------

# Absolute context-window limit (tokens)
CONTEXT_WINDOW_LIMIT = 200_000

# Estimated tokens consumed by tool definitions
TOOLS_TOKEN_ESTIMATE = 5_000

# Safety buffer reserved when computing available document budget
CONTEXT_SAFETY_BUFFER = 20_000

# ---------------------------------------------------------------------------
# Context Pressure Thresholds (percentages of CONTEXT_WINDOW_LIMIT)
# ---------------------------------------------------------------------------
# Used by dynamic memory allocation, summary compression, document budget,
# and facts injection to adapt behaviour to real-time context pressure.

PRESSURE_LOW = 50          # Green zone: full capacity
PRESSURE_MEDIUM = 60       # Yellow zone: resource optimization
PRESSURE_HIGH = 70         # Orange zone: warning alerts
PRESSURE_CRITICAL = 80     # Red zone: force efficiency modes
PRESSURE_EMERGENCY = 85    # Critical zone: essential operations only

# Warning / critical absolute token counts
CONTEXT_WARNING_TOKENS = 140_000    # 70% of 200K
CONTEXT_CRITICAL_TOKENS = 160_000   # 80% of 200K

# ---------------------------------------------------------------------------
# Working Memory (Dynamic Buffer Sizes)
# ---------------------------------------------------------------------------
# Buffer sizes are NOT fixed -- they adapt based on context pressure.
# See ``HierarchicalMemorySystem.record_episode()`` for the allocation logic.

BUFFER_SIZE_EMERGENCY = 10     # >= 85% pressure
BUFFER_SIZE_CRITICAL = 15      # >= 80% pressure
BUFFER_SIZE_HIGH = 20          # >= 70% pressure
BUFFER_SIZE_MEDIUM_HIGH = 25   # >= 60% pressure
BUFFER_SIZE_MEDIUM = 30        # >= 50% pressure
BUFFER_SIZE_LOW = 35           # <  50% pressure (maximum memory)

# Emergency compression keeps the last N exchanges intact
EMERGENCY_COMPRESSION_KEEP = 20

# ---------------------------------------------------------------------------
# Summary Context Token Budgets (Pressure-Based)
# ---------------------------------------------------------------------------
# Graduated compression for ``get_summary_context()``.

SUMMARY_TOKENS_EMERGENCY = 1_000     # >= 85% pressure
SUMMARY_TOKENS_CRITICAL = 1_500      # >= 80% pressure
SUMMARY_TOKENS_HIGH = 2_000          # >= 70% pressure
SUMMARY_TOKENS_MEDIUM_HIGH = 3_000   # >= 60% pressure
SUMMARY_TOKENS_MEDIUM = 4_000        # >= 50% pressure
SUMMARY_TOKENS_LOW = 5_000           # <  50% pressure (full summaries)

# Cap on how many recent summaries are included
MAX_SUMMARIES_IN_CONTEXT = 3

# ---------------------------------------------------------------------------
# Document Context Token Budgets (Pressure-Based)
# ---------------------------------------------------------------------------
# Graduated document budgets from ``_calculate_available_document_budget()``.

DOC_BUDGET_EMERGENCY = 3_000     # >= 85% pressure
DOC_BUDGET_CRITICAL = 5_000      # >= 80% pressure
DOC_BUDGET_HIGH = 8_000          # >= 70% pressure
DOC_BUDGET_MEDIUM_HIGH = 12_000  # >= 60% pressure
DOC_BUDGET_MEDIUM = 15_000       # >= 50% pressure
DOC_BUDGET_LOW = 20_000          # <  50% pressure (full documents)

# Documents smaller than this threshold are included in full
SMALL_DOCUMENT_TOKEN_THRESHOLD = 10_000

# Number of top-k relevant chunks to include per large document
DOCUMENT_RELEVANT_CHUNKS_K = 3

# ---------------------------------------------------------------------------
# Facts Memory
# ---------------------------------------------------------------------------

# Confidence threshold for automatic facts injection into context
FACTS_AUTO_INJECT_CONFIDENCE = 0.6

# Importance threshold for creating identity nodes from episodes
IDENTITY_NODE_IMPORTANCE_THRESHOLD = 0.6

# Graduated facts injection limits (by context pressure)
FACTS_LIMIT_EMERGENCY = 1    # >= 85% pressure
FACTS_LIMIT_CRITICAL = 2     # >= 80% pressure
FACTS_LIMIT_HIGH = 3         # >= 70% pressure
FACTS_LIMIT_MEDIUM_HIGH = 4  # >= 60% pressure
FACTS_LIMIT_NORMAL = 5       # <  60% pressure

# The 18 recognised fact types (mirrors facts_memory.py FACT_TYPES)
FACT_TYPES = (
    # Personal Assistant Types (High Priority)
    "appointment",
    "contact",
    "preference",
    "task",
    "note",
    "location",
    "recommendation",
    "routine",
    "health",
    "financial",
    # Communication & Tools
    "communication",
    "tool_use",
    # Technical Support Types (Lower Priority)
    "command",
    "code",
    "file",
    "url",
    "error",
    "config",
)

# ---------------------------------------------------------------------------
# Memory Config Defaults
# ---------------------------------------------------------------------------

DEFAULT_BUFFER_SIZE = 100            # Default episodic window (env-overridable)
BUFFER_TRUNCATE_AT = 120             # Begin summarisation at this buffer size
SUMMARY_WINDOW_SIZE = 25             # Exchanges per summary
SUMMARY_OVERLAP = 5                  # Overlap between summary windows
MAX_SUMMARIES_IN_MEMORY = 50         # Recent summaries kept accessible
DEFAULT_SUMMARY_BUFFER_SIZE = 20     # Summary buffer injection count
GIST_CREATION_THRESHOLD = 25         # Summaries before gist creation
GIST_IMPORTANCE_THRESHOLD = 0.5      # Minimum importance for gist
SESSION_SUMMARY_LENGTH = 500         # Words in session summary

# Proactive summarisation triggers
PROACTIVE_SUMMARIZE_INTERVAL = 10    # Every N exchanges
PROACTIVE_SUMMARIZE_MIN_BUFFER = 20  # Minimum buffer size to trigger

# ---------------------------------------------------------------------------
# Working Memory Context Defaults
# ---------------------------------------------------------------------------

DEFAULT_WORKING_MEMORY_MAX_TOKENS = 150_000

# ---------------------------------------------------------------------------
# Twitter Integration
# ---------------------------------------------------------------------------

DEFAULT_MAX_TWEET_LENGTH = 280       # Standard Twitter limit
PREMIUM_MAX_TWEET_LENGTH = 25_000    # Premium / Blue long-form
DEFAULT_TWITTER_VOICE_FORMALITY = 6.0
DEFAULT_TWITTER_VOICE_DEPTH = 8.0
DEFAULT_TWITTER_VOICE_ACCESSIBILITY = 7.0

# ---------------------------------------------------------------------------
# Tavily Search Defaults
# ---------------------------------------------------------------------------

DEFAULT_TAVILY_SEARCH_DEPTH = "basic"
DEFAULT_TAVILY_MAX_RESULTS = 5
DEFAULT_TAVILY_TIMEOUT = 60

# ---------------------------------------------------------------------------
# Tool Timeouts
# ---------------------------------------------------------------------------

DEFAULT_BASH_TIMEOUT = 60            # Seconds

# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------

DEFAULT_WORKSPACE = "./coco_workspace"
MEMORY_DB_FILENAME = "coco_memory.db"
KNOWLEDGE_GRAPH_DB_FILENAME = "coco_knowledge.db"
