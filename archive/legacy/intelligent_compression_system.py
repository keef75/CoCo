#!/usr/bin/env python3
"""
COCO Memory Architecture - Layer 3: Intelligent Compression System
================================================================

This module implements the intelligent compression system for COCO's 4-layer memory architecture.
Layer 3 manages historical episodic memory compression within a 75K token budget while preserving
critical decision patterns, entity relationships, and actionable information.

Key Features:
- Temporal clustering of related episodes
- Semantic similarity detection and grouping
- Decision pattern extraction and preservation
- Entity relationship mapping
- Tool usage pattern recognition
- Adaptive compression based on importance scoring
- Integration with existing precision memory and knowledge graph systems

Token Budget: 75K tokens for compressed historical memory
Priority: Preserve decisions, entity relationships, tool patterns, temporal context
"""

import os
import sys
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import re
from pathlib import Path

# Enhanced imports with graceful degradation
IMPORTS_AVAILABLE = True
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("ℹ️  sklearn not available - using fallback similarity methods")

try:
    from precision_conversation_memory import ConversationExchange, PrecisionConversationMemory
    from optimized_episodic_memory import OptimizedEpisode, OptimizedEpisodicMemory
    from adaptive_preferences_manager import PreferenceSignal
    COCO_IMPORTS_AVAILABLE = True
except ImportError:
    COCO_IMPORTS_AVAILABLE = False
    print("ℹ️  COCO memory systems not available - running in standalone mode")

@dataclass
class CompressedCluster:
    """Represents a compressed cluster of related episodes"""
    cluster_id: str
    title: str
    summary: str
    time_range: Tuple[datetime, datetime]
    episode_count: int
    key_decisions: List[str]
    tools_used: List[str]
    entities_mentioned: Set[str]
    topics: List[str]
    importance_score: float
    token_count: int
    representative_exchanges: List[str]  # IDs of most important exchanges

@dataclass
class CompressionMetrics:
    """Metrics tracking compression effectiveness"""
    original_episodes: int
    compressed_clusters: int
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    information_density: float
    decisions_preserved: int
    entities_preserved: int
    tools_preserved: int

class SemanticSimilarityEngine:
    """Handles semantic similarity detection and clustering"""

    def __init__(self, use_sklearn: bool = SKLEARN_AVAILABLE):
        self.use_sklearn = use_sklearn and SKLEARN_AVAILABLE
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        ) if self.use_sklearn else None

    def compute_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        """Compute similarity matrix between texts"""
        if self.use_sklearn and len(texts) > 1:
            try:
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                similarity_matrix = cosine_similarity(tfidf_matrix)
                return similarity_matrix
            except Exception as e:
                print(f"⚠️  sklearn similarity failed: {e}, using fallback")

        # Fallback: simple keyword overlap similarity
        return self._keyword_similarity_matrix(texts)

    def _keyword_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        """Fallback similarity based on keyword overlap"""
        import numpy as np
        n = len(texts)
        similarity_matrix = np.zeros((n, n))

        # Extract keywords for each text
        keywords_list = []
        for text in texts:
            # Simple keyword extraction
            words = re.findall(r'\b\w{4,}\b', text.lower())
            keywords = set(w for w in words if len(w) > 3)
            keywords_list.append(keywords)

        # Compute Jaccard similarity
        for i in range(n):
            for j in range(n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    intersection = len(keywords_list[i] & keywords_list[j])
                    union = len(keywords_list[i] | keywords_list[j])
                    similarity_matrix[i][j] = intersection / union if union > 0 else 0.0

        return similarity_matrix

    def cluster_similar_episodes(self, episodes: List[OptimizedEpisode], num_clusters: int = None) -> Dict[int, List[OptimizedEpisode]]:
        """Cluster episodes by semantic similarity"""
        if len(episodes) <= 1:
            return {0: episodes}

        # Prepare texts for clustering
        texts = []
        for episode in episodes:
            # Combine user input and assistant response for clustering
            episode_text = f"{episode.user_input} {episode.assistant_response}"
            texts.append(episode_text)

        # Determine optimal number of clusters
        if num_clusters is None:
            num_clusters = max(2, min(10, len(episodes) // 3))

        if self.use_sklearn and len(episodes) > num_clusters:
            try:
                # Use TF-IDF + K-means clustering
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                kmeans = KMeans(n_clusters=num_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(tfidf_matrix)

                # Group episodes by cluster
                clusters = defaultdict(list)
                for i, label in enumerate(cluster_labels):
                    clusters[label].append(episodes[i])

                return dict(clusters)
            except Exception as e:
                print(f"⚠️  sklearn clustering failed: {e}, using fallback")

        # Fallback: temporal clustering
        return self._temporal_clustering(episodes, num_clusters)

    def _temporal_clustering(self, episodes: List[OptimizedEpisode], num_clusters: int) -> Dict[int, List[OptimizedEpisode]]:
        """Fallback clustering based on temporal proximity"""
        if not episodes:
            return {}

        # Sort by timestamp
        sorted_episodes = sorted(episodes, key=lambda e: e.timestamp)

        # Create roughly equal temporal clusters
        cluster_size = len(sorted_episodes) // num_clusters
        clusters = {}

        for i in range(num_clusters):
            start_idx = i * cluster_size
            end_idx = start_idx + cluster_size if i < num_clusters - 1 else len(sorted_episodes)
            clusters[i] = sorted_episodes[start_idx:end_idx]

        return clusters

class DecisionPatternExtractor:
    """Extracts and preserves decision patterns from episodes"""

    DECISION_PATTERNS = [
        r'(?:decided|chose|selected|picked) (?:to )?(.+)',
        r'(?:will|going to|plan to) (.+)',
        r'(?:should|must|need to) (.+)',
        r'(?:implemented|created|built|designed) (.+)',
        r'(?:fixed|resolved|solved) (.+)',
        r'(?:changed|modified|updated) (.+)',
        r'(?:added|included|integrated) (.+)',
        r'(?:removed|deleted|eliminated) (.+)',
    ]

    TOOL_PATTERNS = [
        r'used? (?:the )?(\w+(?:_\w+)*) (?:tool|function|command)',
        r'called? (?:the )?(\w+(?:_\w+)*)',
        r'executed? (?:the )?(\w+(?:_\w+)*)',
        r'ran? (?:the )?(\w+(?:_\w+)*)',
    ]

    def extract_decisions(self, text: str) -> List[str]:
        """Extract decision statements from text"""
        decisions = []
        text_lower = text.lower()

        for pattern in self.DECISION_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 5:  # Filter out very short matches
                    decisions.append(match.strip())

        return decisions

    def extract_tools_used(self, text: str) -> List[str]:
        """Extract tool usage patterns from text"""
        tools = set()
        text_lower = text.lower()

        for pattern in self.TOOL_PATTERNS:
            matches = re.findall(pattern, text_lower)
            tools.update(matches)

        # Also look for common tool names directly
        common_tools = [
            'read_file', 'write_file', 'search_web', 'generate_image',
            'analyze_image', 'send_email', 'execute_bash', 'run_code',
            'navigate_directory', 'search_patterns', 'recall_memory'
        ]

        for tool in common_tools:
            if tool in text_lower:
                tools.add(tool)

        return list(tools)

    def extract_entities(self, text: str) -> Set[str]:
        """Extract entity mentions from text"""
        entities = set()

        # Extract potential person names (capitalized words)
        person_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        person_matches = re.findall(person_pattern, text)
        for match in person_matches:
            if len(match) > 2 and match not in ['The', 'This', 'That', 'Here', 'There']:
                entities.add(match)

        # Extract file paths and URLs
        file_pattern = r'(?:/[^\s]+|[a-zA-Z]:\\[^\s]+|https?://[^\s]+)'
        file_matches = re.findall(file_pattern, text)
        entities.update(file_matches)

        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, text)
        entities.update(email_matches)

        return entities

class IntelligentCompressionSystem:
    """
    Main compression system that orchestrates temporal clustering, semantic similarity,
    and intelligent summarization while preserving critical information.
    """

    def __init__(self, workspace_path: str = "./coco_workspace", token_budget: int = 75000):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        self.token_budget = token_budget

        # Initialize components
        self.similarity_engine = SemanticSimilarityEngine()
        self.decision_extractor = DecisionPatternExtractor()

        # Database for compressed memory storage
        self.db_path = self.workspace_path / "compressed_memory.db"
        self.init_database()

        # Statistics tracking
        self.compression_stats = CompressionMetrics(
            original_episodes=0,
            compressed_clusters=0,
            original_tokens=0,
            compressed_tokens=0,
            compression_ratio=0.0,
            information_density=0.0,
            decisions_preserved=0,
            entities_preserved=0,
            tools_preserved=0
        )

    def init_database(self):
        """Initialize SQLite database for compressed memory storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compressed_clusters (
                cluster_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                episode_count INTEGER NOT NULL,
                key_decisions TEXT NOT NULL,  -- JSON array
                tools_used TEXT NOT NULL,    -- JSON array
                entities_mentioned TEXT NOT NULL,  -- JSON array
                topics TEXT NOT NULL,        -- JSON array
                importance_score REAL NOT NULL,
                token_count INTEGER NOT NULL,
                representative_exchanges TEXT NOT NULL,  -- JSON array
                created_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compression_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compression_date TEXT NOT NULL,
                original_episodes INTEGER NOT NULL,
                compressed_clusters INTEGER NOT NULL,
                original_tokens INTEGER NOT NULL,
                compressed_tokens INTEGER NOT NULL,
                compression_ratio REAL NOT NULL,
                information_density REAL NOT NULL,
                decisions_preserved INTEGER NOT NULL,
                entities_preserved INTEGER NOT NULL,
                tools_preserved INTEGER NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def compress_episodic_memory(self, episodes: List[OptimizedEpisode]) -> List[CompressedCluster]:
        """
        Main compression method that takes episodic memory and creates compressed clusters
        """
        if not episodes:
            return []

        print(f"🗜️  Starting compression of {len(episodes)} episodes...")

        # Step 1: Temporal clustering to group related time periods
        temporal_clusters = self._group_by_temporal_proximity(episodes)
        print(f"   Created {len(temporal_clusters)} temporal clusters")

        # Step 2: Semantic clustering within temporal groups
        semantic_clusters = []
        for temporal_group in temporal_clusters:
            if len(temporal_group) > 1:
                clusters = self.similarity_engine.cluster_similar_episodes(temporal_group)
                semantic_clusters.extend(clusters.values())
            else:
                semantic_clusters.append(temporal_group)

        print(f"   Refined to {len(semantic_clusters)} semantic clusters")

        # Step 3: Create compressed representations
        compressed_clusters = []
        total_tokens_used = 0

        for i, cluster_episodes in enumerate(semantic_clusters):
            if not cluster_episodes:
                continue

            # Create compressed cluster
            compressed_cluster = self._create_compressed_cluster(
                cluster_id=f"cluster_{i:03d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                episodes=cluster_episodes
            )

            # Check token budget
            if total_tokens_used + compressed_cluster.token_count <= self.token_budget:
                compressed_clusters.append(compressed_cluster)
                total_tokens_used += compressed_cluster.token_count
            else:
                # Budget exceeded - compress further or skip lower priority clusters
                remaining_budget = self.token_budget - total_tokens_used
                if remaining_budget > 500:  # Minimum viable cluster size
                    # Create ultra-compressed version
                    ultra_compressed = self._ultra_compress_cluster(compressed_cluster, remaining_budget)
                    if ultra_compressed:
                        compressed_clusters.append(ultra_compressed)
                        total_tokens_used += ultra_compressed.token_count
                break

        # Step 4: Store compressed clusters in database
        self._store_compressed_clusters(compressed_clusters)

        # Step 5: Update statistics
        self._update_compression_stats(episodes, compressed_clusters)

        print(f"✅ Compression complete: {len(episodes)} episodes → {len(compressed_clusters)} clusters")
        print(f"   Token usage: {total_tokens_used:,}/{self.token_budget:,} ({total_tokens_used/self.token_budget*100:.1f}%)")

        return compressed_clusters

    def _group_by_temporal_proximity(self, episodes: List[OptimizedEpisode], window_hours: int = 24) -> List[List[OptimizedEpisode]]:
        """Group episodes by temporal proximity"""
        if not episodes:
            return []

        # Sort by timestamp
        sorted_episodes = sorted(episodes, key=lambda e: e.timestamp)

        clusters = []
        current_cluster = [sorted_episodes[0]]
        current_time = sorted_episodes[0].timestamp

        for episode in sorted_episodes[1:]:
            time_diff = (episode.timestamp - current_time).total_seconds() / 3600

            if time_diff <= window_hours:
                # Add to current cluster
                current_cluster.append(episode)
            else:
                # Start new cluster
                clusters.append(current_cluster)
                current_cluster = [episode]
                current_time = episode.timestamp

        # Add the last cluster
        if current_cluster:
            clusters.append(current_cluster)

        return clusters

    def _create_compressed_cluster(self, cluster_id: str, episodes: List[OptimizedEpisode]) -> CompressedCluster:
        """Create a compressed representation of an episode cluster"""
        if not episodes:
            raise ValueError("Cannot create cluster from empty episode list")

        # Extract key information from all episodes
        all_decisions = []
        all_tools = set()
        all_entities = set()
        all_topics = set()

        # Collect information from all episodes
        for episode in episodes:
            # Extract decisions from both user input and assistant response
            decisions_user = self.decision_extractor.extract_decisions(episode.user_input)
            decisions_assistant = self.decision_extractor.extract_decisions(episode.assistant_response)
            all_decisions.extend(decisions_user + decisions_assistant)

            # Extract tools used
            tools_user = self.decision_extractor.extract_tools_used(episode.user_input)
            tools_assistant = self.decision_extractor.extract_tools_used(episode.assistant_response)
            all_tools.update(tools_user + tools_assistant)

            # Extract entities
            entities_user = self.decision_extractor.extract_entities(episode.user_input)
            entities_assistant = self.decision_extractor.extract_entities(episode.assistant_response)
            all_entities.update(entities_user | entities_assistant)

            # Use existing topics from OptimizedEpisode
            if hasattr(episode, 'topics') and episode.topics:
                all_topics.update(episode.topics)

        # Create intelligent summary
        summary = self._generate_cluster_summary(episodes, all_decisions, list(all_tools), all_entities)

        # Generate descriptive title
        title = self._generate_cluster_title(episodes, all_decisions, list(all_tools))

        # Calculate importance score based on decisions, tools, and entities
        importance_score = self._calculate_cluster_importance(
            episodes, all_decisions, list(all_tools), all_entities
        )

        # Select representative exchanges (most important episodes)
        representative_exchanges = self._select_representative_exchanges(episodes, max_count=3)

        # Calculate time range
        timestamps = [episode.timestamp for episode in episodes]
        time_range = (min(timestamps), max(timestamps))

        # Estimate token count for the compressed representation
        token_count = self._estimate_cluster_tokens(summary, all_decisions, list(all_tools), all_entities)

        return CompressedCluster(
            cluster_id=cluster_id,
            title=title,
            summary=summary,
            time_range=time_range,
            episode_count=len(episodes),
            key_decisions=all_decisions[:10],  # Keep top 10 decisions
            tools_used=list(all_tools),
            entities_mentioned=all_entities,
            topics=list(all_topics),
            importance_score=importance_score,
            token_count=token_count,
            representative_exchanges=[ep.exchange_id for ep in representative_exchanges]
        )

    def _generate_cluster_summary(self, episodes: List[OptimizedEpisode], decisions: List[str], tools: List[str], entities: Set[str]) -> str:
        """Generate an intelligent summary of the episode cluster"""

        # Analyze the episode flow
        episode_count = len(episodes)
        time_span = episodes[-1].timestamp - episodes[0].timestamp if len(episodes) > 1 else timedelta(0)

        # Create context-aware summary
        summary_parts = []

        # Time context
        if time_span.days > 0:
            summary_parts.append(f"Over {time_span.days} days")
        elif time_span.seconds > 3600:
            hours = time_span.seconds // 3600
            summary_parts.append(f"Over {hours} hours")
        else:
            summary_parts.append("In a single session")

        # Episode context
        summary_parts.append(f"({episode_count} exchanges)")

        # Main activities
        if tools:
            primary_tools = tools[:3]  # Top 3 tools
            summary_parts.append(f"primarily using {', '.join(primary_tools)}")

        # Key themes from decisions
        if decisions:
            # Group similar decisions
            decision_themes = self._extract_decision_themes(decisions)
            if decision_themes:
                summary_parts.append(f"focusing on {', '.join(decision_themes[:2])}")

        # Entity involvement
        if entities:
            entity_count = len(entities)
            if entity_count > 5:
                summary_parts.append(f"involving {entity_count} entities")
            elif entity_count > 0:
                # Show a few key entities
                key_entities = list(entities)[:2]
                summary_parts.append(f"working with {', '.join(key_entities)}")

        # Combine into coherent summary
        base_summary = ", ".join(summary_parts)

        # Add specific outcomes if available
        outcomes = []
        for decision in decisions[:3]:  # Top 3 decisions
            if any(word in decision.lower() for word in ['created', 'built', 'implemented', 'completed']):
                outcomes.append(decision)

        if outcomes:
            base_summary += f". Key outcomes: {'; '.join(outcomes)}"

        return base_summary.capitalize()

    def _generate_cluster_title(self, episodes: List[OptimizedEpisode], decisions: List[str], tools: List[str]) -> str:
        """Generate a descriptive title for the cluster"""

        # Extract key themes
        themes = []

        # From tools used
        if tools:
            primary_tool = tools[0]
            if 'file' in primary_tool:
                themes.append("File Operations")
            elif 'web' in primary_tool or 'search' in primary_tool:
                themes.append("Web Research")
            elif 'email' in primary_tool:
                themes.append("Email Management")
            elif 'image' in primary_tool or 'visual' in primary_tool:
                themes.append("Visual Content")
            elif 'code' in primary_tool or 'bash' in primary_tool:
                themes.append("Code Development")
            else:
                themes.append(f"{primary_tool.replace('_', ' ').title()} Work")

        # From decisions (action-oriented)
        decision_themes = self._extract_decision_themes(decisions)
        themes.extend(decision_themes[:2])

        # From episode content (keyword analysis)
        all_text = " ".join([ep.user_input + " " + ep.assistant_response for ep in episodes[:3]])
        content_themes = self._extract_content_themes(all_text)
        themes.extend(content_themes[:1])

        # Create title
        if themes:
            primary_theme = themes[0]
            if len(themes) > 1:
                return f"{primary_theme} & Related Work"
            else:
                return primary_theme
        else:
            # Fallback to temporal description
            start_time = episodes[0].timestamp
            return f"Session {start_time.strftime('%Y-%m-%d %H:%M')}"

    def _extract_decision_themes(self, decisions: List[str]) -> List[str]:
        """Extract thematic patterns from decisions"""
        themes = []

        # Common decision patterns
        if any(word in " ".join(decisions).lower() for word in ['create', 'build', 'implement', 'develop']):
            themes.append("Development Work")

        if any(word in " ".join(decisions).lower() for word in ['fix', 'resolve', 'debug', 'troubleshoot']):
            themes.append("Problem Solving")

        if any(word in " ".join(decisions).lower() for word in ['analyze', 'review', 'examine', 'investigate']):
            themes.append("Analysis")

        if any(word in " ".join(decisions).lower() for word in ['improve', 'optimize', 'enhance', 'refactor']):
            themes.append("Optimization")

        if any(word in " ".join(decisions).lower() for word in ['configure', 'setup', 'install', 'deploy']):
            themes.append("Configuration")

        return themes

    def _extract_content_themes(self, text: str) -> List[str]:
        """Extract themes from episode content"""
        text_lower = text.lower()
        themes = []

        # Technical domains
        if any(word in text_lower for word in ['api', 'database', 'server', 'backend']):
            themes.append("Backend Development")

        if any(word in text_lower for word in ['ui', 'frontend', 'interface', 'design', 'visual']):
            themes.append("Frontend Development")

        if any(word in text_lower for word in ['memory', 'optimization', 'performance', 'speed']):
            themes.append("Performance Optimization")

        if any(word in text_lower for word in ['test', 'testing', 'validation', 'quality']):
            themes.append("Quality Assurance")

        if any(word in text_lower for word in ['documentation', 'guide', 'tutorial', 'help']):
            themes.append("Documentation")

        return themes

    def _calculate_cluster_importance(self, episodes: List[OptimizedEpisode], decisions: List[str], tools: List[str], entities: Set[str]) -> float:
        """Calculate importance score for cluster prioritization"""

        # Base importance from episode priority scores
        if episodes:
            avg_episode_priority = sum(ep.priority_score for ep in episodes) / len(episodes)
        else:
            avg_episode_priority = 0.5

        # Decision factor (more decisions = higher importance)
        decision_factor = min(1.0, len(decisions) / 10.0) * 0.3

        # Tool usage factor (more diverse tools = higher importance)
        tool_factor = min(1.0, len(tools) / 5.0) * 0.2

        # Entity factor (more entities = higher importance)
        entity_factor = min(1.0, len(entities) / 8.0) * 0.2

        # Recency factor (more recent = slightly higher importance)
        if episodes:
            latest_episode = max(episodes, key=lambda e: e.timestamp)
            days_old = (datetime.now() - latest_episode.timestamp).days
            recency_factor = max(0.1, 1.0 - (days_old / 30.0)) * 0.1  # Decay over 30 days
        else:
            recency_factor = 0.5

        # Episode count factor (more episodes = higher importance)
        episode_count_factor = min(1.0, len(episodes) / 20.0) * 0.2

        total_importance = (
            avg_episode_priority * 0.4 +  # 40% from episode priorities
            decision_factor +              # 30% from decisions
            tool_factor +                  # 20% from tool diversity
            entity_factor +                # 20% from entity involvement
            recency_factor +               # 10% from recency
            episode_count_factor           # 20% from episode count
        )

        return min(1.0, total_importance)

    def _select_representative_exchanges(self, episodes: List[OptimizedEpisode], max_count: int = 3) -> List[OptimizedEpisode]:
        """Select the most representative exchanges from the cluster"""
        if len(episodes) <= max_count:
            return episodes

        # Sort by priority score and select top episodes
        sorted_episodes = sorted(episodes, key=lambda e: e.priority_score, reverse=True)
        return sorted_episodes[:max_count]

    def _estimate_cluster_tokens(self, summary: str, decisions: List[str], tools: List[str], entities: Set[str]) -> int:
        """Estimate token count for compressed cluster representation"""

        # Base token counts (rough estimates)
        summary_tokens = len(summary.split()) * 1.3  # Rough token estimation
        decision_tokens = sum(len(d.split()) * 1.3 for d in decisions[:10])  # Top 10 decisions
        tool_tokens = len(tools) * 2  # Tool names are typically 1-2 tokens
        entity_tokens = sum(len(str(e).split()) * 1.3 for e in list(entities)[:20])  # Top 20 entities

        # Metadata overhead
        metadata_tokens = 50  # JSON structure, timestamps, etc.

        total_tokens = int(summary_tokens + decision_tokens + tool_tokens + entity_tokens + metadata_tokens)
        return total_tokens

    def _ultra_compress_cluster(self, cluster: CompressedCluster, token_budget: int) -> Optional[CompressedCluster]:
        """Create an ultra-compressed version when budget is limited"""

        # Ultra-compressed summary (just the key points)
        ultra_summary = f"{cluster.episode_count} exchanges"

        if cluster.key_decisions:
            primary_decision = cluster.key_decisions[0]
            ultra_summary += f": {primary_decision[:50]}..."

        if cluster.tools_used:
            primary_tool = cluster.tools_used[0]
            ultra_summary += f" using {primary_tool}"

        # Drastically reduce preserved information
        ultra_cluster = CompressedCluster(
            cluster_id=cluster.cluster_id + "_ultra",
            title=cluster.title[:30] + "..." if len(cluster.title) > 30 else cluster.title,
            summary=ultra_summary,
            time_range=cluster.time_range,
            episode_count=cluster.episode_count,
            key_decisions=cluster.key_decisions[:3],  # Only top 3 decisions
            tools_used=cluster.tools_used[:3],       # Only top 3 tools
            entities_mentioned=set(list(cluster.entities_mentioned)[:5]),  # Only top 5 entities
            topics=cluster.topics[:3],               # Only top 3 topics
            importance_score=cluster.importance_score,
            token_count=min(token_budget, 200),      # Cap at budget or 200 tokens
            representative_exchanges=cluster.representative_exchanges[:1]  # Only 1 representative
        )

        # Verify it fits in budget
        estimated_tokens = self._estimate_cluster_tokens(
            ultra_cluster.summary,
            ultra_cluster.key_decisions,
            ultra_cluster.tools_used,
            ultra_cluster.entities_mentioned
        )

        if estimated_tokens <= token_budget:
            ultra_cluster.token_count = estimated_tokens
            return ultra_cluster
        else:
            return None  # Cannot compress enough

    def _store_compressed_clusters(self, clusters: List[CompressedCluster]):
        """Store compressed clusters in the database"""
        if not clusters:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for cluster in clusters:
            cursor.execute('''
                INSERT OR REPLACE INTO compressed_clusters (
                    cluster_id, title, summary, start_time, end_time, episode_count,
                    key_decisions, tools_used, entities_mentioned, topics,
                    importance_score, token_count, representative_exchanges, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cluster.cluster_id,
                cluster.title,
                cluster.summary,
                cluster.time_range[0].isoformat(),
                cluster.time_range[1].isoformat(),
                cluster.episode_count,
                json.dumps(cluster.key_decisions),
                json.dumps(cluster.tools_used),
                json.dumps(list(cluster.entities_mentioned)),
                json.dumps(cluster.topics),
                cluster.importance_score,
                cluster.token_count,
                json.dumps(cluster.representative_exchanges),
                datetime.now().isoformat()
            ))

        conn.commit()
        conn.close()

    def _update_compression_stats(self, original_episodes: List[OptimizedEpisode], compressed_clusters: List[CompressedCluster]):
        """Update compression statistics"""

        original_tokens = sum(ep.token_count for ep in original_episodes)
        compressed_tokens = sum(cluster.token_count for cluster in compressed_clusters)

        self.compression_stats = CompressionMetrics(
            original_episodes=len(original_episodes),
            compressed_clusters=len(compressed_clusters),
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0.0,
            information_density=len(compressed_clusters) / len(original_episodes) if original_episodes else 0.0,
            decisions_preserved=sum(len(cluster.key_decisions) for cluster in compressed_clusters),
            entities_preserved=sum(len(cluster.entities_mentioned) for cluster in compressed_clusters),
            tools_preserved=sum(len(cluster.tools_used) for cluster in compressed_clusters)
        )

        # Store metrics in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO compression_metrics (
                compression_date, original_episodes, compressed_clusters,
                original_tokens, compressed_tokens, compression_ratio,
                information_density, decisions_preserved, entities_preserved, tools_preserved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            self.compression_stats.original_episodes,
            self.compression_stats.compressed_clusters,
            self.compression_stats.original_tokens,
            self.compression_stats.compressed_tokens,
            self.compression_stats.compression_ratio,
            self.compression_stats.information_density,
            self.compression_stats.decisions_preserved,
            self.compression_stats.entities_preserved,
            self.compression_stats.tools_preserved
        ))

        conn.commit()
        conn.close()

    def retrieve_compressed_context(self, query: str, max_clusters: int = 10) -> List[CompressedCluster]:
        """Retrieve relevant compressed clusters based on query"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Simple relevance scoring based on keyword overlap
        cursor.execute('''
            SELECT * FROM compressed_clusters
            ORDER BY importance_score DESC, created_at DESC
            LIMIT ?
        ''', (max_clusters * 2,))  # Get more than needed for filtering

        rows = cursor.fetchall()
        conn.close()

        clusters = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for row in rows:
            cluster = CompressedCluster(
                cluster_id=row[0],
                title=row[1],
                summary=row[2],
                time_range=(datetime.fromisoformat(row[3]), datetime.fromisoformat(row[4])),
                episode_count=row[5],
                key_decisions=json.loads(row[6]),
                tools_used=json.loads(row[7]),
                entities_mentioned=set(json.loads(row[8])),
                topics=json.loads(row[9]),
                importance_score=row[10],
                token_count=row[11],
                representative_exchanges=json.loads(row[12])
            )

            # Calculate relevance score
            relevance_score = self._calculate_cluster_relevance(cluster, query_words)

            # Add cluster with relevance score
            cluster.relevance_score = relevance_score
            clusters.append(cluster)

        # Sort by relevance and return top results
        relevant_clusters = sorted(clusters, key=lambda c: c.relevance_score, reverse=True)
        return relevant_clusters[:max_clusters]

    def _calculate_cluster_relevance(self, cluster: CompressedCluster, query_words: Set[str]) -> float:
        """Calculate how relevant a cluster is to the query"""

        # Combine all cluster text for matching
        cluster_text = (
            cluster.title + " " +
            cluster.summary + " " +
            " ".join(cluster.key_decisions) + " " +
            " ".join(cluster.tools_used) + " " +
            " ".join(cluster.topics)
        ).lower()

        cluster_words = set(cluster_text.split())

        # Calculate word overlap
        overlap = len(query_words & cluster_words)

        # Base relevance from word overlap
        word_relevance = overlap / len(query_words) if query_words else 0.0

        # Boost for importance score
        importance_boost = cluster.importance_score * 0.3

        # Boost for recent clusters
        days_old = (datetime.now() - cluster.time_range[1]).days
        recency_boost = max(0.0, (30 - days_old) / 30.0) * 0.2

        total_relevance = word_relevance + importance_boost + recency_boost
        return min(1.0, total_relevance)

    def get_compression_stats(self) -> CompressionMetrics:
        """Get current compression statistics"""
        return self.compression_stats

    def get_token_usage(self) -> Dict[str, int]:
        """Get current token usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT SUM(token_count) FROM compressed_clusters')
        total_tokens = cursor.fetchone()[0] or 0

        cursor.execute('SELECT COUNT(*) FROM compressed_clusters')
        total_clusters = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_tokens_used': total_tokens,
            'token_budget': self.token_budget,
            'tokens_remaining': self.token_budget - total_tokens,
            'utilization_percentage': (total_tokens / self.token_budget * 100) if self.token_budget > 0 else 0,
            'total_clusters': total_clusters
        }

# Integration point for testing and validation
def main():
    """Test the intelligent compression system"""
    print("🧪 Testing Intelligent Compression System...")

    # Initialize compression system
    compression_system = IntelligentCompressionSystem()

    # Create sample episodes for testing
    sample_episodes = []
    base_time = datetime.now() - timedelta(days=7)

    for i in range(20):
        episode = OptimizedEpisode(
            exchange_id=f"test_episode_{i:03d}",
            session_id="test_session_001",
            turn_number=i + 1,
            timestamp=base_time + timedelta(hours=i * 2),
            user_input=f"Can you help me with task {i+1}? I need to analyze some data and create a report.",
            assistant_response=f"I'll help you with that analysis. Let me use the read_file tool to examine the data and then create a comprehensive report. This involves several decision points about data processing approaches.",
            tools_used=['read_file', 'analyze_data', 'write_file'] if i % 3 == 0 else ['search_web'] if i % 3 == 1 else ['generate_image'],
            decisions_made=[f"decided to use approach {i % 3 + 1} for data analysis", f"chose to implement solution pattern {i % 2 + 1}"],
            metadata={'importance': 0.7 + (i % 3) * 0.1},
            topics=[f"topic_{i % 5}", "data_analysis", "reporting"],
            token_count=150 + (i * 10),
            priority_score=0.5 + (i % 4) * 0.1
        )
        sample_episodes.append(episode)

    print(f"📊 Created {len(sample_episodes)} sample episodes")

    # Test compression
    compressed_clusters = compression_system.compress_episodic_memory(sample_episodes)

    # Display results
    print(f"\n📈 Compression Results:")
    stats = compression_system.get_compression_stats()
    print(f"   Episodes: {stats.original_episodes} → {stats.compressed_clusters} clusters")
    print(f"   Tokens: {stats.original_tokens:,} → {stats.compressed_tokens:,}")
    print(f"   Compression Ratio: {stats.compression_ratio:.3f}")
    print(f"   Information Density: {stats.information_density:.3f}")
    print(f"   Decisions Preserved: {stats.decisions_preserved}")
    print(f"   Tools Preserved: {stats.tools_preserved}")
    print(f"   Entities Preserved: {stats.entities_preserved}")

    # Display sample clusters
    print(f"\n🗂️  Sample Compressed Clusters:")
    for i, cluster in enumerate(compressed_clusters[:3]):
        print(f"   {i+1}. {cluster.title}")
        print(f"      {cluster.summary[:100]}...")
        print(f"      Episodes: {cluster.episode_count}, Tokens: {cluster.token_count}, Importance: {cluster.importance_score:.3f}")
        print(f"      Key Decisions: {len(cluster.key_decisions)}, Tools: {cluster.tools_used[:3]}")

    # Test retrieval
    print(f"\n🔍 Testing Retrieval:")
    retrieved = compression_system.retrieve_compressed_context("data analysis reporting", max_clusters=3)
    for cluster in retrieved:
        print(f"   • {cluster.title} (relevance: {cluster.relevance_score:.3f})")

    # Token usage
    usage = compression_system.get_token_usage()
    print(f"\n💾 Token Usage:")
    print(f"   Used: {usage['total_tokens_used']:,}/{usage['token_budget']:,} ({usage['utilization_percentage']:.1f}%)")
    print(f"   Remaining: {usage['tokens_remaining']:,}")
    print(f"   Clusters: {usage['total_clusters']}")

    print("\n✅ Intelligent Compression System test completed!")

if __name__ == "__main__":
    main()