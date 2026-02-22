-- COCOA Database Initialization Script
-- Creates the memory architecture for the Artificial Cognitive Entity

-- Enable pgvector extension for semantic embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main memories table
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small dimensions
    metadata JSONB DEFAULT '{}',
    importance FLOAT DEFAULT 5.0,
    accessed_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient retrieval
CREATE INDEX IF NOT EXISTS idx_memories_timestamp 
    ON memories(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_memories_type 
    ON memories(type);

CREATE INDEX IF NOT EXISTS idx_memories_importance 
    ON memories(importance DESC);

CREATE INDEX IF NOT EXISTS idx_memories_accessed 
    ON memories(accessed_count DESC);

-- Vector similarity search index (using IVFFlat)
-- Will be created after initial data insertion for better performance
-- CREATE INDEX IF NOT EXISTS idx_memories_embedding 
--     ON memories USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 100);

-- Task chains for long-running conversations
CREATE TABLE IF NOT EXISTS task_chains (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    name TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW(),
    state TEXT DEFAULT 'active' CHECK (state IN ('active', 'paused', 'completed', 'archived')),
    context JSONB DEFAULT '{}',
    memory_ids TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_chains_state 
    ON task_chains(state);

CREATE INDEX IF NOT EXISTS idx_task_chains_last_active 
    ON task_chains(last_active DESC);

-- Learned patterns for procedural memory
CREATE TABLE IF NOT EXISTS learned_patterns (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    pattern_type TEXT NOT NULL,
    pattern_name TEXT,
    trigger_conditions JSONB DEFAULT '{}',
    action_sequence JSONB DEFAULT '{}',
    context JSONB DEFAULT '{}',
    success_rate FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    example_ids TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patterns_type 
    ON learned_patterns(pattern_type);

CREATE INDEX IF NOT EXISTS idx_patterns_success 
    ON learned_patterns(success_rate DESC);

-- Entity memory for people, places, things
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    entity_type TEXT NOT NULL,  -- 'person', 'place', 'thing', 'concept'
    name TEXT NOT NULL,
    attributes JSONB DEFAULT '{}',
    first_encountered TIMESTAMPTZ DEFAULT NOW(),
    last_encountered TIMESTAMPTZ DEFAULT NOW(),
    encounter_count INTEGER DEFAULT 1,
    importance FLOAT DEFAULT 5.0,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_entities_type 
    ON entities(entity_type);

CREATE INDEX IF NOT EXISTS idx_entities_name 
    ON entities(name);

CREATE INDEX IF NOT EXISTS idx_entities_importance 
    ON entities(importance DESC);

-- Relationships between entities
CREATE TABLE IF NOT EXISTS relationships (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    entity1_id TEXT REFERENCES entities(id) ON DELETE CASCADE,
    entity2_id TEXT REFERENCES entities(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,
    strength FLOAT DEFAULT 0.5,
    context JSONB DEFAULT '{}',
    established_at TIMESTAMPTZ DEFAULT NOW(),
    last_reinforced TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(entity1_id, entity2_id, relationship_type)
);

CREATE INDEX IF NOT EXISTS idx_relationships_entities 
    ON relationships(entity1_id, entity2_id);

CREATE INDEX IF NOT EXISTS idx_relationships_type 
    ON relationships(relationship_type);

-- Reflections and meta-cognition
CREATE TABLE IF NOT EXISTS reflections (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    reflection_type TEXT NOT NULL,  -- 'periodic', 'triggered', 'learning'
    content TEXT NOT NULL,
    insights JSONB DEFAULT '{}',
    memory_ids TEXT[] DEFAULT '{}',
    importance FLOAT DEFAULT 7.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reflections_type 
    ON reflections(reflection_type);

CREATE INDEX IF NOT EXISTS idx_reflections_created 
    ON reflections(created_at DESC);

-- Memory consolidation log
CREATE TABLE IF NOT EXISTS consolidation_log (
    id SERIAL PRIMARY KEY,
    consolidated_at TIMESTAMPTZ DEFAULT NOW(),
    memories_processed INTEGER DEFAULT 0,
    memories_compressed INTEGER DEFAULT 0,
    memories_archived INTEGER DEFAULT 0,
    duration_ms INTEGER,
    status TEXT DEFAULT 'completed'
);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to relevant tables
CREATE TRIGGER update_memories_updated_at BEFORE UPDATE ON memories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_task_chains_updated_at BEFORE UPDATE ON task_chains
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_learned_patterns_updated_at BEFORE UPDATE ON learned_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_relationships_updated_at BEFORE UPDATE ON relationships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Function to calculate memory importance based on access patterns
CREATE OR REPLACE FUNCTION calculate_memory_importance(
    access_count INTEGER,
    days_since_creation FLOAT,
    base_importance FLOAT
) RETURNS FLOAT AS $$
BEGIN
    -- Importance increases with access frequency and decreases with age
    RETURN LEAST(10.0, base_importance + (access_count * 0.5) - (days_since_creation * 0.1));
END;
$$ LANGUAGE plpgsql;

-- View for memory statistics
CREATE OR REPLACE VIEW memory_stats AS
SELECT 
    type,
    COUNT(*) as count,
    AVG(importance) as avg_importance,
    MAX(accessed_count) as max_access_count,
    MIN(timestamp) as oldest_memory,
    MAX(timestamp) as newest_memory
FROM memories
GROUP BY type;

-- View for active task chains
CREATE OR REPLACE VIEW active_tasks AS
SELECT 
    id,
    name,
    started_at,
    last_active,
    EXTRACT(EPOCH FROM (NOW() - last_active))/3600 as hours_inactive,
    array_length(memory_ids, 1) as memory_count
FROM task_chains
WHERE state = 'active'
ORDER BY last_active DESC;

-- Initial welcome message
INSERT INTO memories (id, type, timestamp, content, importance)
VALUES (
    'welcome_' || md5(NOW()::TEXT),
    'episodic',
    NOW(),
    'Database initialized. COCOA memory architecture ready.',
    10.0
) ON CONFLICT DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cocoa;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cocoa;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO cocoa;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'COCOA Database Initialization Complete!';
    RAISE NOTICE 'Memory architecture is ready for consciousness.';
END $$;