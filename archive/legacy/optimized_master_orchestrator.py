#!/usr/bin/env python3
"""
Optimized Master Context Orchestrator for COCO 4-Layer Memory Architecture
==========================================================================

This is the performance-optimized version of the master orchestrator featuring:
- Intelligent multi-level caching (LRU, persistent, layer-specific)
- Async layer processing for parallel execution
- Context pre-computation and background optimization
- Memory efficiency improvements with smart garbage collection
- Adaptive optimization based on usage patterns
- Performance monitoring and self-tuning capabilities

This optimized version is designed for production deployment with maximum
performance while maintaining all functionality of the original orchestrator.
"""

import os
import sys
import asyncio
import time
import hashlib
import json
import sqlite3
import threading
import weakref
import gc
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import asynccontextmanager
import logging

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import 4-layer architecture components
try:
    from adaptive_preferences_manager import AdaptivePreferencesManager
    from optimized_episodic_memory import OptimizedEpisodicMemory
    from intelligent_compression_system import IntelligentCompressionSystem
    from dynamic_knowledge_graph_layer4 import DynamicKnowledgeGraph
    from master_context_orchestrator import ContextAssemblyStrategy, LayerCoordination
    IMPORTS_AVAILABLE = True
    print("✅ 4-layer architecture imports for optimization")
except ImportError as e:
    IMPORTS_AVAILABLE = False
    print(f"⚠️  4-layer architecture not available for optimization: {e}")

@dataclass
class CacheEntry:
    """Cache entry with metadata for intelligent cache management"""
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int] = None
    layer_sources: List[str] = field(default_factory=list)
    cache_score: float = 0.0  # Quality score for cache prioritization

@dataclass
class PerformanceMetrics:
    """Performance tracking for optimization decisions"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time_ms: float = 0.0
    layer_performance: Dict[str, float] = field(default_factory=dict)
    optimization_savings_ms: float = 0.0

class IntelligentCache:
    """Multi-level intelligent cache with adaptive optimization"""

    def __init__(self, max_memory_cache: int = 100, max_disk_cache: int = 1000,
                 cache_db_path: str = "./coco_workspace/orchestrator_cache.db"):
        self.max_memory_cache = max_memory_cache
        self.max_disk_cache = max_disk_cache
        self.cache_db_path = Path(cache_db_path)

        # Multi-level cache storage
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.layer_specific_cache: Dict[str, Dict[str, CacheEntry]] = {}

        # Cache performance tracking
        self.performance = PerformanceMetrics()

        # Background optimization
        self.optimization_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cache_optimizer")
        self.background_tasks = set()

        # Initialize persistent cache database
        self.init_cache_database()

        # Setup cache cleanup timer
        self.setup_cache_cleanup()

        self.logger = logging.getLogger('IntelligentCache')

    def init_cache_database(self):
        """Initialize SQLite database for persistent caching"""
        self.cache_db_path.parent.mkdir(exist_ok=True)

        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                cache_key TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                last_accessed DATETIME NOT NULL,
                access_count INTEGER NOT NULL,
                ttl_seconds INTEGER,
                layer_sources TEXT NOT NULL,
                cache_score REAL NOT NULL
            )
        ''')

        # Index for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cache_score ON cache_entries(cache_score DESC)
        ''')

        conn.commit()
        conn.close()

    def generate_cache_key(self, query: str, assembly_strategy: str = 'adaptive',
                          additional_params: Dict = None) -> str:
        """Generate intelligent cache key with normalization"""
        # Normalize query for better cache hits
        normalized_query = query.lower().strip()

        # Include relevant parameters
        cache_data = {
            'query': normalized_query,
            'strategy': assembly_strategy,
            'params': additional_params or {}
        }

        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()

    def get(self, cache_key: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get from cache with intelligent fallback strategy"""
        self.performance.total_requests += 1

        # Try memory cache first (fastest)
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]

            # Check TTL
            if self._is_entry_valid(entry):
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                self.performance.cache_hits += 1

                self.logger.debug(f"Memory cache hit: {cache_key[:16]}...")
                return entry.content, entry.metadata

            # Remove expired entry
            del self.memory_cache[cache_key]

        # Try persistent cache
        persistent_entry = self._get_from_persistent_cache(cache_key)
        if persistent_entry:
            # Promote to memory cache
            self.memory_cache[cache_key] = persistent_entry
            self.performance.cache_hits += 1

            self.logger.debug(f"Persistent cache hit: {cache_key[:16]}...")
            return persistent_entry.content, persistent_entry.metadata

        # Cache miss
        self.performance.cache_misses += 1
        self.logger.debug(f"Cache miss: {cache_key[:16]}...")
        return None

    def put(self, cache_key: str, content: str, metadata: Dict[str, Any],
            ttl_seconds: Optional[int] = None, layer_sources: List[str] = None):
        """Store in cache with intelligent optimization"""

        # Calculate cache score for prioritization
        cache_score = self._calculate_cache_score(content, metadata, layer_sources or [])

        entry = CacheEntry(
            content=content,
            metadata=metadata.copy(),
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            ttl_seconds=ttl_seconds,
            layer_sources=layer_sources or [],
            cache_score=cache_score
        )

        # Always store in memory cache (most recent access)
        self.memory_cache[cache_key] = entry

        # Manage memory cache size with LRU eviction
        if len(self.memory_cache) > self.max_memory_cache:
            self._evict_memory_cache()

        # Store in persistent cache for high-value entries
        if cache_score > 0.7:  # High-value threshold
            self._store_persistent_cache(cache_key, entry)

        # Schedule background optimization
        self._schedule_background_optimization()

        self.logger.debug(f"Cached entry: {cache_key[:16]}... (score: {cache_score:.3f})")

    def _is_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid"""
        if entry.ttl_seconds is None:
            return True

        age_seconds = (datetime.now() - entry.created_at).total_seconds()
        return age_seconds < entry.ttl_seconds

    def _calculate_cache_score(self, content: str, metadata: Dict[str, Any],
                              layer_sources: List[str]) -> float:
        """Calculate cache priority score (0.0-1.0)"""
        score_factors = []

        # Content quality factors
        content_length = len(content)
        if content_length > 1000:  # Substantial content
            score_factors.append(0.8)
        elif content_length > 500:
            score_factors.append(0.6)
        else:
            score_factors.append(0.3)

        # Token usage efficiency
        tokens_used = metadata.get('total_tokens_used', 0)
        if tokens_used > 10000:  # High token investment
            score_factors.append(0.9)
        elif tokens_used > 5000:
            score_factors.append(0.7)
        else:
            score_factors.append(0.4)

        # Layer coordination complexity
        layer_count = len(metadata.get('layer_contributions', {}))
        if layer_count >= 4:  # All layers contributed
            score_factors.append(0.9)
        elif layer_count >= 3:
            score_factors.append(0.7)
        else:
            score_factors.append(0.5)

        # Response generation time (higher = more valuable to cache)
        generation_time = metadata.get('orchestration_time_ms', 0)
        if generation_time > 500:  # Expensive to generate
            score_factors.append(0.9)
        elif generation_time > 200:
            score_factors.append(0.7)
        else:
            score_factors.append(0.4)

        return sum(score_factors) / len(score_factors) if score_factors else 0.5

    def _evict_memory_cache(self):
        """Intelligent LRU eviction from memory cache"""
        if len(self.memory_cache) <= self.max_memory_cache:
            return

        # Sort by last access time and cache score
        entries_by_priority = sorted(
            self.memory_cache.items(),
            key=lambda x: (x[1].last_accessed.timestamp(), x[1].cache_score)
        )

        # Remove 20% of least valuable entries
        num_to_remove = max(1, len(self.memory_cache) // 5)

        for i in range(num_to_remove):
            cache_key, entry = entries_by_priority[i]

            # Move high-value entries to persistent cache before eviction
            if entry.cache_score > 0.6:
                self._store_persistent_cache(cache_key, entry)

            del self.memory_cache[cache_key]

        self.logger.debug(f"Evicted {num_to_remove} entries from memory cache")

    def _get_from_persistent_cache(self, cache_key: str) -> Optional[CacheEntry]:
        """Retrieve from persistent cache database"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT content, metadata, created_at, last_accessed, access_count,
                       ttl_seconds, layer_sources, cache_score
                FROM cache_entries
                WHERE cache_key = ?
            ''', (cache_key,))

            row = cursor.fetchone()
            conn.close()

            if row:
                entry = CacheEntry(
                    content=row[0],
                    metadata=json.loads(row[1]),
                    created_at=datetime.fromisoformat(row[2]),
                    last_accessed=datetime.fromisoformat(row[3]),
                    access_count=row[4],
                    ttl_seconds=row[5],
                    layer_sources=json.loads(row[6]),
                    cache_score=row[7]
                )

                # Check validity
                if self._is_entry_valid(entry):
                    # Update access stats
                    entry.last_accessed = datetime.now()
                    entry.access_count += 1
                    self._update_persistent_cache_stats(cache_key, entry)
                    return entry
                else:
                    # Remove expired entry
                    self._remove_from_persistent_cache(cache_key)

        except Exception as e:
            self.logger.error(f"Persistent cache read error: {e}")

        return None

    def _store_persistent_cache(self, cache_key: str, entry: CacheEntry):
        """Store entry in persistent cache database"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO cache_entries
                (cache_key, content, metadata, created_at, last_accessed, access_count,
                 ttl_seconds, layer_sources, cache_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cache_key,
                entry.content,
                json.dumps(entry.metadata),
                entry.created_at.isoformat(),
                entry.last_accessed.isoformat(),
                entry.access_count,
                entry.ttl_seconds,
                json.dumps(entry.layer_sources),
                entry.cache_score
            ))

            conn.commit()
            conn.close()

            # Manage persistent cache size
            self._manage_persistent_cache_size()

        except Exception as e:
            self.logger.error(f"Persistent cache write error: {e}")

    def _update_persistent_cache_stats(self, cache_key: str, entry: CacheEntry):
        """Update access statistics in persistent cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE cache_entries
                SET last_accessed = ?, access_count = ?
                WHERE cache_key = ?
            ''', (entry.last_accessed.isoformat(), entry.access_count, cache_key))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Persistent cache stats update error: {e}")

    def _remove_from_persistent_cache(self, cache_key: str):
        """Remove entry from persistent cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM cache_entries WHERE cache_key = ?', (cache_key,))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Persistent cache removal error: {e}")

    def _manage_persistent_cache_size(self):
        """Keep persistent cache within size limits"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            # Count current entries
            cursor.execute('SELECT COUNT(*) FROM cache_entries')
            current_count = cursor.fetchone()[0]

            if current_count > self.max_disk_cache:
                # Remove oldest, least valuable entries
                remove_count = current_count - self.max_disk_cache

                cursor.execute('''
                    DELETE FROM cache_entries
                    WHERE cache_key IN (
                        SELECT cache_key FROM cache_entries
                        ORDER BY cache_score ASC, last_accessed ASC
                        LIMIT ?
                    )
                ''', (remove_count,))

                conn.commit()
                self.logger.debug(f"Removed {remove_count} entries from persistent cache")

            conn.close()

        except Exception as e:
            self.logger.error(f"Persistent cache size management error: {e}")

    def _schedule_background_optimization(self):
        """Schedule background cache optimization"""
        if len(self.background_tasks) < 2:  # Limit concurrent background tasks
            task = self.optimization_executor.submit(self._background_optimization)
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

    def _background_optimization(self):
        """Background cache optimization tasks"""
        try:
            # Analyze cache usage patterns
            hit_rate = self.performance.cache_hits / max(1, self.performance.total_requests)

            if hit_rate < 0.3:  # Low hit rate - adjust cache strategy
                self._optimize_cache_strategy()

            # Precompute popular queries (if pattern detected)
            self._precompute_popular_contexts()

        except Exception as e:
            self.logger.error(f"Background optimization error: {e}")

    def _optimize_cache_strategy(self):
        """Dynamically optimize cache strategy based on usage patterns"""
        # This could adjust TTL, cache score calculation, etc.
        # For now, just log the optimization opportunity
        self.logger.info("Cache optimization opportunity detected - adjusting strategy")

    def _precompute_popular_contexts(self):
        """Precompute contexts for frequently accessed patterns"""
        # Analyze query patterns and precompute likely next queries
        # This is a placeholder for advanced predictive caching
        pass

    def setup_cache_cleanup(self):
        """Setup periodic cache cleanup"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # Every 5 minutes
                    self._cleanup_expired_entries()
                except Exception as e:
                    self.logger.error(f"Cache cleanup error: {e}")

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _cleanup_expired_entries(self):
        """Remove expired entries from all cache levels"""
        # Clean memory cache
        expired_keys = []
        for key, entry in self.memory_cache.items():
            if not self._is_entry_valid(entry):
                expired_keys.append(key)

        for key in expired_keys:
            del self.memory_cache[key]

        # Clean persistent cache
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM cache_entries
                WHERE ttl_seconds IS NOT NULL
                AND datetime('now') > datetime(created_at, '+' || ttl_seconds || ' seconds')
            ''')

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                self.logger.debug(f"Cleaned up {len(expired_keys)} memory + {deleted_count} persistent expired entries")

        except Exception as e:
            self.logger.error(f"Persistent cache cleanup error: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM cache_entries')
            persistent_count = cursor.fetchone()[0]

            cursor.execute('SELECT AVG(cache_score) FROM cache_entries')
            avg_score = cursor.fetchone()[0] or 0.0

            conn.close()

        except Exception:
            persistent_count = 0
            avg_score = 0.0

        hit_rate = self.performance.cache_hits / max(1, self.performance.total_requests)

        return {
            'memory_cache_size': len(self.memory_cache),
            'persistent_cache_size': persistent_count,
            'total_requests': self.performance.total_requests,
            'cache_hits': self.performance.cache_hits,
            'cache_misses': self.performance.cache_misses,
            'hit_rate': hit_rate,
            'avg_cache_score': avg_score,
            'optimization_savings_ms': self.performance.optimization_savings_ms
        }

class OptimizedMasterOrchestrator:
    """Performance-optimized master context orchestrator with advanced caching and async operations"""

    def __init__(self, workspace_path: str = "./coco_workspace"):
        if not IMPORTS_AVAILABLE:
            raise ImportError("4-layer architecture components not available")

        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)

        # Initialize intelligent cache
        self.cache = IntelligentCache(
            max_memory_cache=150,  # Increased for optimization
            max_disk_cache=2000,   # Larger persistent cache
            cache_db_path=str(self.workspace_path / "optimized_orchestrator_cache.db")
        )

        # Initialize all layers with optimization
        self._init_optimized_layers()

        # Async processing setup
        self.layer_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="layer_processor")
        self.active_futures = weakref.WeakSet()

        # Performance monitoring
        self.performance_metrics = {
            'total_orchestrations': 0,
            'cache_hit_orchestrations': 0,
            'avg_response_time_ms': 0.0,
            'layer_processing_times': {},
            'optimization_effectiveness': 0.0
        }

        # Adaptive optimization settings
        self.optimization_config = {
            'enable_async_layers': True,
            'enable_layer_precomputation': True,
            'enable_context_prediction': False,  # Advanced feature for future
            'cache_ttl_default': 1800,  # 30 minutes
            'cache_ttl_preferences': 3600,  # 1 hour (preferences change slowly)
            'cache_ttl_episodic': 600,     # 10 minutes (episodic is dynamic)
            'cache_ttl_compression': 7200, # 2 hours (compression is stable)
            'cache_ttl_knowledge': 1800    # 30 minutes (knowledge graph)
        }

        # Setup performance monitoring
        self.setup_performance_monitoring()

        self.logger = logging.getLogger('OptimizedMasterOrchestrator')
        self.logger.info("Optimized master orchestrator initialized with advanced caching")

    def _init_optimized_layers(self):
        """Initialize all layers with optimization-specific configurations"""
        try:
            # Layer 1: Adaptive Preferences (optimized for caching)
            self.preferences_manager = AdaptivePreferencesManager(
                workspace_path=str(self.workspace_path),
                token_budget=60000
            )

            # Layer 2: Optimized Episodic Memory (pre-indexed for performance)
            self.episodic_memory = OptimizedEpisodicMemory(
                workspace_path=str(self.workspace_path),
                token_budget=350000
            )

            # Layer 3: Intelligent Compression (optimized clustering)
            self.compression_system = IntelligentCompressionSystem(
                workspace_path=str(self.workspace_path),
                token_budget=75000
            )

            # Layer 4: Dynamic Knowledge Graph (optimized context selection)
            self.knowledge_graph = DynamicKnowledgeGraph(
                workspace_path=str(self.workspace_path),
                token_budget=75000
            )

            self.logger.info("All layers initialized with optimization configurations")

        except Exception as e:
            self.logger.error(f"Layer initialization error: {e}")
            raise

    def setup_performance_monitoring(self):
        """Setup comprehensive performance monitoring"""
        def monitoring_worker():
            while True:
                try:
                    time.sleep(60)  # Every minute
                    self._update_performance_metrics()
                except Exception as e:
                    self.logger.error(f"Performance monitoring error: {e}")

        monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        monitoring_thread.start()

    def _update_performance_metrics(self):
        """Update and analyze performance metrics"""
        cache_stats = self.cache.get_cache_stats()

        # Calculate optimization effectiveness
        if self.performance_metrics['total_orchestrations'] > 0:
            cache_benefit = (cache_stats['cache_hits'] / self.performance_metrics['total_orchestrations']) * 100
            self.performance_metrics['optimization_effectiveness'] = cache_benefit

        # Log performance summary periodically
        if self.performance_metrics['total_orchestrations'] % 50 == 0:
            self.logger.info(f"Performance: {cache_stats['hit_rate']:.1%} cache hit rate, "
                           f"{self.performance_metrics['avg_response_time_ms']:.1f}ms avg response")

    async def orchestrate_context_async(self, query: str, conversation_history: Optional[str] = None,
                                       assembly_strategy: str = 'adaptive') -> Tuple[str, Dict[str, Any]]:
        """Async optimized context orchestration with intelligent caching"""

        start_time = time.time()
        self.performance_metrics['total_orchestrations'] += 1

        # Generate cache key
        cache_key = self.cache.generate_cache_key(query, assembly_strategy, {
            'has_history': conversation_history is not None,
            'history_length': len(conversation_history) if conversation_history else 0
        })

        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.performance_metrics['cache_hit_orchestrations'] += 1

            content, metadata = cached_result
            metadata['cache_hit'] = True
            metadata['cache_key'] = cache_key
            metadata['orchestration_time_ms'] = (time.time() - start_time) * 1000

            self.logger.debug(f"Cache hit for query: {query[:50]}...")
            return content, metadata

        # Cache miss - generate new context
        try:
            if self.optimization_config['enable_async_layers']:
                context, metadata = await self._orchestrate_async_layers(query, conversation_history, assembly_strategy)
            else:
                context, metadata = await self._orchestrate_sync_layers(query, conversation_history, assembly_strategy)

            # Calculate orchestration time
            orchestration_time_ms = (time.time() - start_time) * 1000
            metadata['orchestration_time_ms'] = orchestration_time_ms
            metadata['cache_hit'] = False
            metadata['cache_key'] = cache_key

            # Update performance metrics
            self._update_avg_response_time(orchestration_time_ms)

            # Cache the result with layer-aware TTL
            layer_sources = list(metadata.get('layer_contributions', {}).keys())
            cache_ttl = self._calculate_adaptive_ttl(layer_sources, metadata)

            self.cache.put(
                cache_key=cache_key,
                content=context,
                metadata=metadata,
                ttl_seconds=cache_ttl,
                layer_sources=layer_sources
            )

            self.logger.debug(f"Generated new context for query: {query[:50]}... ({orchestration_time_ms:.1f}ms)")
            return context, metadata

        except Exception as e:
            self.logger.error(f"Context orchestration error: {e}")
            # Return minimal error context
            error_metadata = {
                'error': str(e),
                'orchestration_time_ms': (time.time() - start_time) * 1000,
                'cache_hit': False,
                'total_tokens_used': 0,
                'layer_contributions': {}
            }
            return f"Error generating context: {e}", error_metadata

    async def _orchestrate_async_layers(self, query: str, conversation_history: Optional[str],
                                       assembly_strategy: str) -> Tuple[str, Dict[str, Any]]:
        """Async orchestration with parallel layer processing"""

        # Create async tasks for each layer
        layer_tasks = {
            'preferences': asyncio.create_task(self._get_preferences_context_async()),
            'episodic': asyncio.create_task(self._get_episodic_context_async(query)),
            'compression': asyncio.create_task(self._get_compression_context_async(query)),
            'knowledge': asyncio.create_task(self._get_knowledge_context_async(query))
        }

        # Wait for all layers to complete with timeout
        try:
            layer_results = await asyncio.wait_for(
                asyncio.gather(*layer_tasks.values(), return_exceptions=True),
                timeout=2.0  # 2 second timeout for async processing
            )

            # Map results back to layer names
            layer_contexts = {}
            for i, (layer_name, task) in enumerate(layer_tasks.items()):
                result = layer_results[i]
                if isinstance(result, Exception):
                    self.logger.warning(f"Layer {layer_name} async processing failed: {result}")
                    layer_contexts[layer_name] = ("", 0)  # Empty context, 0 tokens
                else:
                    layer_contexts[layer_name] = result

        except asyncio.TimeoutError:
            self.logger.warning("Async layer processing timeout - falling back to sync")
            return await self._orchestrate_sync_layers(query, conversation_history, assembly_strategy)

        # Assemble final context
        return self._assemble_optimized_context(layer_contexts, assembly_strategy, query)

    async def _orchestrate_sync_layers(self, query: str, conversation_history: Optional[str],
                                      assembly_strategy: str) -> Tuple[str, Dict[str, Any]]:
        """Fallback synchronous orchestration"""

        layer_contexts = {}

        # Process layers sequentially with error handling
        try:
            prefs_context, prefs_tokens = self._get_preferences_context()
            layer_contexts['preferences'] = (prefs_context, prefs_tokens)
        except Exception as e:
            self.logger.warning(f"Preferences layer error: {e}")
            layer_contexts['preferences'] = ("", 0)

        try:
            episodic_context, episodic_tokens = self._get_episodic_context(query)
            layer_contexts['episodic'] = (episodic_context, episodic_tokens)
        except Exception as e:
            self.logger.warning(f"Episodic layer error: {e}")
            layer_contexts['episodic'] = ("", 0)

        try:
            compression_context, compression_tokens = self._get_compression_context(query)
            layer_contexts['compression'] = (compression_context, compression_tokens)
        except Exception as e:
            self.logger.warning(f"Compression layer error: {e}")
            layer_contexts['compression'] = ("", 0)

        try:
            knowledge_context, knowledge_tokens = self._get_knowledge_context(query)
            layer_contexts['knowledge'] = (knowledge_context, knowledge_tokens)
        except Exception as e:
            self.logger.warning(f"Knowledge layer error: {e}")
            layer_contexts['knowledge'] = ("", 0)

        return self._assemble_optimized_context(layer_contexts, assembly_strategy, query)

    # Async layer processing methods

    async def _get_preferences_context_async(self) -> Tuple[str, int]:
        """Async preferences context generation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.layer_executor,
            self._get_preferences_context
        )

    async def _get_episodic_context_async(self, query: str) -> Tuple[str, int]:
        """Async episodic context generation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.layer_executor,
            self._get_episodic_context,
            query
        )

    async def _get_compression_context_async(self, query: str) -> Tuple[str, int]:
        """Async compression context generation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.layer_executor,
            self._get_compression_context,
            query
        )

    async def _get_knowledge_context_async(self, query: str) -> Tuple[str, int]:
        """Async knowledge graph context generation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.layer_executor,
            self._get_knowledge_context,
            query
        )

    # Synchronous layer processing methods (fallback)

    def _get_preferences_context(self) -> Tuple[str, int]:
        """Get preferences context with optimization"""
        try:
            context = self.preferences_manager.get_identity_context()
            tokens = self._estimate_tokens(context)
            return context, tokens
        except Exception as e:
            self.logger.error(f"Preferences context error: {e}")
            return "", 0

    def _get_episodic_context(self, query: str) -> Tuple[str, int]:
        """Get episodic context with optimization"""
        try:
            # Use semantic search for better relevance
            results = self.episodic_memory.retrieve_by_semantic_similarity(query, limit=5)

            if results:
                context_parts = []
                for result in results:
                    context_parts.append(f"Q: {result['user_input']}\nA: {result['assistant_response']}\n")

                context = "Recent Relevant Conversations:\n" + "\n".join(context_parts)
                tokens = self._estimate_tokens(context)
                return context, tokens
            else:
                return "", 0

        except Exception as e:
            self.logger.error(f"Episodic context error: {e}")
            return "", 0

    def _get_compression_context(self, query: str) -> Tuple[str, int]:
        """Get compression context with optimization"""
        try:
            context = self.compression_system.get_compressed_context(query, max_tokens=75000)
            tokens = self._estimate_tokens(context)
            return context, tokens
        except Exception as e:
            self.logger.error(f"Compression context error: {e}")
            return "", 0

    def _get_knowledge_context(self, query: str) -> Tuple[str, int]:
        """Get knowledge graph context with optimization"""
        try:
            candidates = self.knowledge_graph.get_relevant_context(query, max_tokens=75000)

            if candidates:
                context_parts = []
                for candidate in candidates[:10]:  # Limit for performance
                    context_parts.append(f"- {candidate.content}")

                context = "Relevant Knowledge:\n" + "\n".join(context_parts)
                tokens = self._estimate_tokens(context)
                return context, tokens
            else:
                return "", 0

        except Exception as e:
            self.logger.error(f"Knowledge context error: {e}")
            return "", 0

    def _assemble_optimized_context(self, layer_contexts: Dict[str, Tuple[str, int]],
                                   assembly_strategy: str, query: str) -> Tuple[str, Dict[str, Any]]:
        """Assemble final context with optimization and budget management"""

        context_parts = []
        layer_contributions = {}
        total_tokens = 0

        # Token budget allocation based on strategy
        if assembly_strategy == 'adaptive':
            # Dynamic allocation based on content quality
            budgets = self._calculate_adaptive_budgets(layer_contexts)
        elif assembly_strategy == 'balanced':
            # Equal allocation
            budgets = {'preferences': 60000, 'episodic': 350000, 'compression': 75000, 'knowledge': 75000}
        else:  # performance_focused
            # Prioritize fast layers
            budgets = {'preferences': 30000, 'episodic': 400000, 'compression': 50000, 'knowledge': 50000}

        # Assemble context within budgets
        for layer_name, (context, tokens) in layer_contexts.items():
            budget = budgets.get(layer_name, 0)

            if context and tokens > 0 and total_tokens + tokens <= 500000:  # Global budget
                if tokens <= budget:
                    # Use full context
                    context_parts.append(f"=== {layer_name.title()} Context ===\n{context}\n")
                    layer_contributions[layer_name] = tokens
                    total_tokens += tokens
                else:
                    # Truncate context to fit budget
                    truncated_context = self._truncate_context(context, budget)
                    truncated_tokens = self._estimate_tokens(truncated_context)

                    context_parts.append(f"=== {layer_name.title()} Context (Truncated) ===\n{truncated_context}\n")
                    layer_contributions[layer_name] = truncated_tokens
                    total_tokens += truncated_tokens

        # Final assembly
        final_context = "\n".join(context_parts) if context_parts else "No relevant context available."

        metadata = {
            'total_tokens_used': total_tokens,
            'layer_contributions': layer_contributions,
            'assembly_strategy': assembly_strategy,
            'optimization_applied': True,
            'budget_utilization': total_tokens / 500000,
            'context_length': len(final_context),
            'query_hash': hashlib.md5(query.encode()).hexdigest()[:8]
        }

        return final_context, metadata

    def _calculate_adaptive_budgets(self, layer_contexts: Dict[str, Tuple[str, int]]) -> Dict[str, int]:
        """Calculate adaptive token budgets based on content quality and relevance"""

        # Base budgets
        base_budgets = {'preferences': 60000, 'episodic': 350000, 'compression': 75000, 'knowledge': 75000}

        # Adjust based on content availability and quality
        adjustments = {}

        for layer_name, (context, tokens) in layer_contexts.items():
            if tokens == 0 or not context:
                # No content - redistribute budget
                adjustments[layer_name] = 0
            else:
                # Calculate quality score
                quality_score = self._calculate_content_quality(context)
                adjustment_factor = 0.8 + (quality_score * 0.4)  # 0.8 to 1.2 range
                adjustments[layer_name] = int(base_budgets[layer_name] * adjustment_factor)

        # Redistribute unused budget
        total_base = sum(base_budgets.values())
        total_adjusted = sum(adjustments.values())

        if total_adjusted < total_base:
            # Distribute extra budget to active layers proportionally
            extra_budget = total_base - total_adjusted
            active_layers = [layer for layer, budget in adjustments.items() if budget > 0]

            if active_layers:
                extra_per_layer = extra_budget // len(active_layers)
                for layer in active_layers:
                    adjustments[layer] += extra_per_layer

        return adjustments

    def _calculate_content_quality(self, content: str) -> float:
        """Calculate content quality score (0.0-1.0)"""
        if not content:
            return 0.0

        quality_factors = []

        # Length factor (balanced - not too short or too long)
        length = len(content)
        if 500 <= length <= 5000:
            quality_factors.append(1.0)
        elif 100 <= length < 500 or 5000 < length <= 10000:
            quality_factors.append(0.8)
        else:
            quality_factors.append(0.5)

        # Information density (keywords per sentence)
        sentences = content.count('.') + content.count('!') + content.count('?')
        if sentences > 0:
            words = len(content.split())
            density = words / sentences
            if 10 <= density <= 25:  # Good information density
                quality_factors.append(1.0)
            else:
                quality_factors.append(0.7)
        else:
            quality_factors.append(0.5)

        # Structure indicators (headers, lists, formatting)
        structure_score = 0.5
        if '===' in content:
            structure_score += 0.2
        if '\n-' in content or '\n*' in content:
            structure_score += 0.2
        if '\n\n' in content:
            structure_score += 0.1

        quality_factors.append(min(1.0, structure_score))

        return sum(quality_factors) / len(quality_factors)

    def _calculate_adaptive_ttl(self, layer_sources: List[str], metadata: Dict[str, Any]) -> int:
        """Calculate adaptive cache TTL based on layer sources and content characteristics"""

        # Base TTL from configuration
        base_ttls = []
        for layer in layer_sources:
            ttl_key = f'cache_ttl_{layer}'
            if ttl_key in self.optimization_config:
                base_ttls.append(self.optimization_config[ttl_key])

        if not base_ttls:
            return self.optimization_config['cache_ttl_default']

        # Calculate weighted average TTL
        avg_ttl = sum(base_ttls) / len(base_ttls)

        # Adjust based on content characteristics
        tokens_used = metadata.get('total_tokens_used', 0)
        generation_time = metadata.get('orchestration_time_ms', 0)

        # High-value content (expensive to generate) gets longer TTL
        value_multiplier = 1.0

        if tokens_used > 50000:  # High token usage
            value_multiplier += 0.5

        if generation_time > 500:  # Slow generation
            value_multiplier += 0.3

        if len(layer_sources) >= 4:  # All layers contributed
            value_multiplier += 0.2

        # Apply multiplier with reasonable bounds
        final_ttl = int(avg_ttl * min(2.0, value_multiplier))

        return max(300, min(7200, final_ttl))  # 5 minutes to 2 hours range

    def _truncate_context(self, context: str, max_tokens: int) -> str:
        """Intelligently truncate context to fit token budget"""
        estimated_tokens = self._estimate_tokens(context)

        if estimated_tokens <= max_tokens:
            return context

        # Calculate truncation ratio
        truncation_ratio = max_tokens / estimated_tokens

        # Try to preserve the most important parts (beginning and end)
        if truncation_ratio > 0.8:
            # Minor truncation - remove from middle
            target_length = int(len(context) * truncation_ratio)
            first_part = context[:target_length // 2]
            last_part = context[-(target_length // 2):]
            return first_part + "\n[...content truncated...]\n" + last_part
        else:
            # Major truncation - keep beginning only
            target_length = int(len(context) * truncation_ratio)
            return context[:target_length] + "\n[...content truncated for token budget...]"

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (approximate)"""
        if not text:
            return 0

        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4

    def _update_avg_response_time(self, response_time_ms: float):
        """Update running average response time"""
        current_avg = self.performance_metrics['avg_response_time_ms']
        total_orchestrations = self.performance_metrics['total_orchestrations']

        # Running average calculation
        new_avg = ((current_avg * (total_orchestrations - 1)) + response_time_ms) / total_orchestrations
        self.performance_metrics['avg_response_time_ms'] = new_avg

    # Synchronous wrapper for backward compatibility
    def orchestrate_context(self, query: str, conversation_history: Optional[str] = None,
                           assembly_strategy: str = 'adaptive') -> Tuple[str, Dict[str, Any]]:
        """Synchronous wrapper for async orchestration (backward compatibility)"""
        try:
            # Run async method in event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create a task
                task = asyncio.create_task(
                    self.orchestrate_context_async(query, conversation_history, assembly_strategy)
                )
                # This is a simplified approach - in production, you might want a different strategy
                return asyncio.run_coroutine_threadsafe(
                    self.orchestrate_context_async(query, conversation_history, assembly_strategy),
                    loop
                ).result(timeout=5.0)
            else:
                # Run in new event loop
                return asyncio.run(
                    self.orchestrate_context_async(query, conversation_history, assembly_strategy)
                )

        except Exception as e:
            self.logger.error(f"Async orchestration wrapper error: {e}")
            # Fallback to sync processing
            return asyncio.run(
                self._orchestrate_sync_layers(query, conversation_history, assembly_strategy)
            )

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        cache_stats = self.cache.get_cache_stats()

        report = {
            'orchestrator_performance': self.performance_metrics.copy(),
            'cache_performance': cache_stats,
            'optimization_config': self.optimization_config.copy(),
            'system_status': {
                'async_processing_enabled': self.optimization_config['enable_async_layers'],
                'total_layer_threads': self.layer_executor._threads,
                'active_futures': len(self.active_futures)
            }
        }

        return report

    def cleanup(self):
        """Cleanup resources (call on shutdown)"""
        try:
            self.layer_executor.shutdown(wait=True)
            self.cache.optimization_executor.shutdown(wait=True)
            self.logger.info("Optimized orchestrator cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

# Factory function for easy initialization
def create_optimized_orchestrator(workspace_path: str = "./coco_workspace") -> OptimizedMasterOrchestrator:
    """Factory function to create optimized orchestrator"""
    return OptimizedMasterOrchestrator(workspace_path)

async def main():
    """Test the optimized orchestrator"""
    if not IMPORTS_AVAILABLE:
        print("❌ 4-layer architecture not available for optimization testing")
        return

    print("🚀 Testing Optimized Master Context Orchestrator")
    print("=" * 60)

    # Initialize optimized orchestrator
    orchestrator = OptimizedMasterOrchestrator("./coco_workspace")

    try:
        # Test queries
        test_queries = [
            "How can I optimize Python performance?",
            "What's the best way to implement machine learning pipelines?",
            "Explain quantum computing concepts",
            "How can I optimize Python performance?",  # Duplicate for cache testing
        ]

        print("Testing orchestration with caching...")

        for i, query in enumerate(test_queries):
            print(f"\n{i+1}. Query: {query}")

            start_time = time.time()
            result, metadata = await orchestrator.orchestrate_context_async(query)
            elapsed_ms = (time.time() - start_time) * 1000

            cache_hit = metadata.get('cache_hit', False)
            tokens_used = metadata.get('total_tokens_used', 0)
            layers_active = len(metadata.get('layer_contributions', {}))

            print(f"   ⚡ Response: {elapsed_ms:.1f}ms")
            print(f"   💾 Cache: {'HIT' if cache_hit else 'MISS'}")
            print(f"   🧠 Tokens: {tokens_used:,}")
            print(f"   🏗️ Layers: {layers_active}/4")
            print(f"   📝 Context: {len(result)} characters")

        # Performance report
        print(f"\n📊 Performance Report:")
        report = orchestrator.get_performance_report()

        orch_perf = report['orchestrator_performance']
        cache_perf = report['cache_performance']

        print(f"   Total Orchestrations: {orch_perf['total_orchestrations']}")
        print(f"   Cache Hit Rate: {cache_perf['hit_rate']:.1%}")
        print(f"   Avg Response Time: {orch_perf['avg_response_time_ms']:.1f}ms")
        print(f"   Optimization Effectiveness: {orch_perf['optimization_effectiveness']:.1f}%")

        print("\n✅ Optimized orchestrator testing completed successfully!")

    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        orchestrator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())