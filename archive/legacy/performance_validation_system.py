#!/usr/bin/env python3
"""
Performance Validation and Benchmarking System for COCO 4-Layer Architecture
============================================================================

This system provides comprehensive performance monitoring, benchmarking, and
optimization analysis for the 4-layer memory architecture:

- Real-time performance monitoring and alerting
- Token usage analytics and budget optimization
- Response time benchmarking across all layers
- Memory efficiency tracking and leak detection
- Layer coordination performance analysis
- Historical performance trends and reporting
- Automated optimization recommendations
- Production readiness scoring

Designed for continuous monitoring and performance-driven optimization.
"""

import os
import sys
import time
import asyncio
import json
import sqlite3
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import logging
from enum import Enum

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Performance monitoring imports
try:
    import psutil
    SYSTEM_MONITORING_AVAILABLE = True
except ImportError:
    SYSTEM_MONITORING_AVAILABLE = False
    print("⚠️  System monitoring limited - install psutil for full metrics")

# Try to import the 4-layer architecture
try:
    from master_context_orchestrator import MasterContextOrchestrator
    from adaptive_preferences_manager import AdaptivePreferencesManager
    from optimized_episodic_memory import OptimizedEpisodicMemory
    from intelligent_compression_system import IntelligentCompressionSystem
    from dynamic_knowledge_graph_layer4 import DynamicKnowledgeGraph
    ARCHITECTURE_AVAILABLE = True
    print("✅ 4-layer architecture imports successful")
except ImportError as e:
    ARCHITECTURE_AVAILABLE = False
    print(f"⚠️  4-layer architecture not available: {e}")

class PerformanceLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class PerformanceMetrics:
    """Individual performance measurement"""
    timestamp: datetime
    operation: str
    response_time_ms: float
    tokens_used: int
    memory_usage_mb: float
    layer_contributions: Dict[str, int]
    success: bool
    error_message: Optional[str] = None

@dataclass
class LayerPerformance:
    """Performance metrics for individual layer"""
    layer_name: str
    avg_response_time_ms: float
    token_efficiency: float  # tokens per ms
    success_rate: float
    memory_efficiency_score: float
    contribution_percentage: float

@dataclass
class SystemPerformanceReport:
    """Comprehensive system performance report"""
    timestamp: datetime
    overall_score: float  # 0.0-1.0
    performance_level: PerformanceLevel
    avg_response_time_ms: float
    token_budget_utilization: float  # 0.0-1.0
    memory_efficiency: float
    layer_performance: List[LayerPerformance]
    optimization_recommendations: List[str]
    trending_metrics: Dict[str, float]

class PerformanceValidator:
    """Main performance validation and benchmarking system"""

    def __init__(self, workspace_path: str = "./coco_workspace", enable_monitoring: bool = True):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)

        # Performance database
        self.perf_db_path = self.workspace_path / "performance_metrics.db"
        self.init_performance_database()

        # Monitoring configuration
        self.enable_monitoring = enable_monitoring and SYSTEM_MONITORING_AVAILABLE
        self.baseline_metrics = None
        self.performance_thresholds = {
            'response_time_ms': {
                'excellent': 100,
                'good': 250,
                'acceptable': 500,
                'poor': 1000,
                'critical': 2000
            },
            'token_efficiency': {
                'excellent': 100,  # tokens per ms
                'good': 50,
                'acceptable': 20,
                'poor': 10,
                'critical': 5
            },
            'memory_growth_mb': {
                'excellent': 10,
                'good': 25,
                'acceptable': 50,
                'poor': 100,
                'critical': 200
            }
        }

        # Initialize orchestrator for testing
        self.orchestrator = None
        if ARCHITECTURE_AVAILABLE:
            try:
                self.orchestrator = MasterContextOrchestrator(str(self.workspace_path))
                print("✅ Performance validator initialized with 4-layer orchestrator")
            except Exception as e:
                print(f"⚠️  Could not initialize orchestrator: {e}")

        # Setup logging
        self.setup_performance_logging()

    def setup_performance_logging(self):
        """Setup performance-specific logging"""
        log_path = self.workspace_path / "performance.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger('PerformanceValidator')

    def init_performance_database(self):
        """Initialize SQLite database for performance metrics storage"""
        conn = sqlite3.connect(self.perf_db_path)
        cursor = conn.cursor()

        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                operation TEXT NOT NULL,
                response_time_ms REAL NOT NULL,
                tokens_used INTEGER NOT NULL,
                memory_usage_mb REAL NOT NULL,
                layer_contributions TEXT NOT NULL,  -- JSON
                success BOOLEAN NOT NULL,
                error_message TEXT
            )
        ''')

        # System benchmarks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_benchmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                overall_score REAL NOT NULL,
                performance_level TEXT NOT NULL,
                avg_response_time_ms REAL NOT NULL,
                token_budget_utilization REAL NOT NULL,
                memory_efficiency REAL NOT NULL,
                layer_performance TEXT NOT NULL,  -- JSON
                recommendations TEXT NOT NULL     -- JSON
            )
        ''')

        # Performance alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                metrics TEXT NOT NULL,  -- JSON
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')

        conn.commit()
        conn.close()

        self.logger.info(f"Performance database initialized: {self.perf_db_path}")

    async def benchmark_single_operation(self, query: str, operation_name: str = "orchestration") -> PerformanceMetrics:
        """Benchmark a single orchestration operation with comprehensive metrics"""
        if not self.orchestrator:
            raise ValueError("Orchestrator not available for benchmarking")

        # Pre-operation measurements
        start_time = time.time()
        initial_memory = 0

        if self.enable_monitoring:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        try:
            # Execute the operation
            result, metadata = self.orchestrator.orchestrate_context(
                query=query,
                assembly_strategy='adaptive'
            )

            # Post-operation measurements
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            final_memory = initial_memory
            if self.enable_monitoring:
                final_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Extract metrics from orchestrator response
            tokens_used = metadata.get('total_tokens_used', 0)
            layer_contributions = metadata.get('layer_contributions', {})

            # Create performance metrics
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                operation=operation_name,
                response_time_ms=response_time_ms,
                tokens_used=tokens_used,
                memory_usage_mb=final_memory - initial_memory,
                layer_contributions=layer_contributions,
                success=len(result) > 0 and tokens_used > 0,
                error_message=None
            )

            # Store in database
            self.store_performance_metrics(metrics)

            return metrics

        except Exception as e:
            # Handle errors gracefully
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            error_metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                operation=operation_name,
                response_time_ms=response_time_ms,
                tokens_used=0,
                memory_usage_mb=0,
                layer_contributions={},
                success=False,
                error_message=str(e)
            )

            self.store_performance_metrics(error_metrics)
            self.logger.error(f"Benchmarking failed for operation {operation_name}: {e}")

            return error_metrics

    def store_performance_metrics(self, metrics: PerformanceMetrics):
        """Store performance metrics in database"""
        conn = sqlite3.connect(self.perf_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO performance_metrics
            (timestamp, operation, response_time_ms, tokens_used, memory_usage_mb,
             layer_contributions, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.timestamp,
            metrics.operation,
            metrics.response_time_ms,
            metrics.tokens_used,
            metrics.memory_usage_mb,
            json.dumps(metrics.layer_contributions),
            metrics.success,
            metrics.error_message
        ))

        conn.commit()
        conn.close()

    async def run_comprehensive_benchmark_suite(self, num_iterations: int = 20) -> SystemPerformanceReport:
        """Run comprehensive benchmark suite across multiple scenarios"""
        self.logger.info(f"Starting comprehensive benchmark suite ({num_iterations} iterations)")

        # Define benchmark scenarios
        test_scenarios = [
            ("Simple query optimization", "How can I optimize this code?"),
            ("Complex technical analysis", "Analyze the performance bottlenecks in a distributed microservices architecture with emphasis on database scaling and caching strategies"),
            ("Knowledge synthesis", "Combine insights from machine learning, software architecture, and performance optimization to recommend improvements"),
            ("Memory-intensive task", "Process and analyze this complex dataset: " + "x" * 1000),
            ("Multi-domain query", "Help me with Python performance, React optimization, and database design best practices"),
            ("Contextual follow-up", "Based on our previous discussion about optimization, what specific tools would you recommend?"),
            ("Technical debugging", "I'm getting intermittent 500 errors in production - help me identify the root cause"),
            ("Learning-focused query", "Explain quantum computing concepts and their practical applications in simple terms")
        ]

        all_metrics = []
        scenario_performance = {}

        for iteration in range(num_iterations):
            self.logger.info(f"Running iteration {iteration + 1}/{num_iterations}")

            for scenario_name, query in test_scenarios:
                try:
                    metrics = await self.benchmark_single_operation(query, f"{scenario_name}_iter_{iteration}")
                    all_metrics.append(metrics)

                    if scenario_name not in scenario_performance:
                        scenario_performance[scenario_name] = []
                    scenario_performance[scenario_name].append(metrics)

                except Exception as e:
                    self.logger.error(f"Failed scenario {scenario_name} iteration {iteration}: {e}")
                    continue

            # Small delay between iterations to avoid overwhelming the system
            await asyncio.sleep(0.1)

        # Analyze results
        return self.analyze_benchmark_results(all_metrics, scenario_performance)

    def analyze_benchmark_results(self, all_metrics: List[PerformanceMetrics],
                                 scenario_performance: Dict[str, List[PerformanceMetrics]]) -> SystemPerformanceReport:
        """Analyze comprehensive benchmark results"""
        if not all_metrics:
            raise ValueError("No metrics available for analysis")

        # Calculate overall statistics
        successful_metrics = [m for m in all_metrics if m.success]
        success_rate = len(successful_metrics) / len(all_metrics)

        if not successful_metrics:
            # Handle case where all operations failed
            return SystemPerformanceReport(
                timestamp=datetime.now(),
                overall_score=0.0,
                performance_level=PerformanceLevel.CRITICAL,
                avg_response_time_ms=float('inf'),
                token_budget_utilization=0.0,
                memory_efficiency=0.0,
                layer_performance=[],
                optimization_recommendations=["CRITICAL: All operations failed - check system integrity"],
                trending_metrics={}
            )

        # Response time analysis
        response_times = [m.response_time_ms for m in successful_metrics]
        avg_response_time = statistics.mean(response_times)
        response_time_std = statistics.stdev(response_times) if len(response_times) > 1 else 0

        # Token usage analysis
        token_usage = [m.tokens_used for m in successful_metrics]
        total_tokens = sum(token_usage)
        avg_tokens_per_operation = statistics.mean(token_usage)
        token_budget_utilization = min(total_tokens / 500000, 1.0)  # 500K budget

        # Memory efficiency analysis
        memory_usage = [abs(m.memory_usage_mb) for m in successful_metrics]
        avg_memory_usage = statistics.mean(memory_usage) if memory_usage else 0

        # Layer performance analysis
        layer_performance = self.analyze_layer_performance(successful_metrics)

        # Determine performance level
        performance_level = self.determine_performance_level(
            avg_response_time, success_rate, token_budget_utilization
        )

        # Calculate overall score (0.0-1.0)
        overall_score = self.calculate_overall_score(
            avg_response_time, success_rate, token_budget_utilization, avg_memory_usage
        )

        # Generate optimization recommendations
        recommendations = self.generate_optimization_recommendations(
            avg_response_time, token_budget_utilization, layer_performance, scenario_performance
        )

        # Historical trending analysis
        trending_metrics = self.analyze_historical_trends()

        # Create comprehensive report
        report = SystemPerformanceReport(
            timestamp=datetime.now(),
            overall_score=overall_score,
            performance_level=performance_level,
            avg_response_time_ms=avg_response_time,
            token_budget_utilization=token_budget_utilization,
            memory_efficiency=1.0 / (1.0 + avg_memory_usage / 100),  # Efficiency score
            layer_performance=layer_performance,
            optimization_recommendations=recommendations,
            trending_metrics=trending_metrics
        )

        # Store benchmark report
        self.store_benchmark_report(report)

        # Check for performance alerts
        self.check_performance_alerts(report)

        return report

    def analyze_layer_performance(self, metrics: List[PerformanceMetrics]) -> List[LayerPerformance]:
        """Analyze performance of individual layers"""
        layer_stats = {}
        total_contributions = 0

        # Aggregate layer statistics
        for metric in metrics:
            for layer, contribution in metric.layer_contributions.items():
                if layer not in layer_stats:
                    layer_stats[layer] = {
                        'contributions': [],
                        'response_times': [],
                        'token_usage': [],
                        'successes': 0,
                        'total': 0
                    }

                layer_stats[layer]['contributions'].append(contribution)
                layer_stats[layer]['response_times'].append(metric.response_time_ms)
                layer_stats[layer]['token_usage'].append(metric.tokens_used)
                layer_stats[layer]['total'] += 1
                total_contributions += contribution

                if metric.success:
                    layer_stats[layer]['successes'] += 1

        # Calculate performance metrics for each layer
        layer_performance = []

        for layer_name, stats in layer_stats.items():
            if not stats['contributions']:
                continue

            avg_response_time = statistics.mean(stats['response_times'])
            avg_tokens = statistics.mean(stats['token_usage'])
            avg_contribution = statistics.mean(stats['contributions'])

            success_rate = stats['successes'] / stats['total'] if stats['total'] > 0 else 0
            token_efficiency = avg_tokens / avg_response_time if avg_response_time > 0 else 0
            contribution_percentage = (avg_contribution / total_contributions) * 100 if total_contributions > 0 else 0

            # Calculate memory efficiency score (simplified)
            memory_efficiency_score = min(1.0, 100 / avg_response_time) if avg_response_time > 0 else 0

            layer_perf = LayerPerformance(
                layer_name=layer_name,
                avg_response_time_ms=avg_response_time,
                token_efficiency=token_efficiency,
                success_rate=success_rate,
                memory_efficiency_score=memory_efficiency_score,
                contribution_percentage=contribution_percentage
            )

            layer_performance.append(layer_perf)

        return sorted(layer_performance, key=lambda x: x.contribution_percentage, reverse=True)

    def determine_performance_level(self, avg_response_time: float, success_rate: float,
                                  token_utilization: float) -> PerformanceLevel:
        """Determine overall performance level based on key metrics"""
        response_time_level = self.get_threshold_level('response_time_ms', avg_response_time)

        # Factor in success rate
        if success_rate < 0.5:
            return PerformanceLevel.CRITICAL
        elif success_rate < 0.8:
            response_time_level = max(response_time_level, PerformanceLevel.POOR)

        # Factor in token utilization (too high is bad, but too low might indicate underutilization)
        if token_utilization > 0.95:  # Over 95% budget utilization
            response_time_level = max(response_time_level, PerformanceLevel.POOR)

        return response_time_level

    def get_threshold_level(self, metric_type: str, value: float) -> PerformanceLevel:
        """Get performance level based on threshold comparison"""
        thresholds = self.performance_thresholds.get(metric_type, {})

        if value <= thresholds.get('excellent', 0):
            return PerformanceLevel.EXCELLENT
        elif value <= thresholds.get('good', 0):
            return PerformanceLevel.GOOD
        elif value <= thresholds.get('acceptable', 0):
            return PerformanceLevel.ACCEPTABLE
        elif value <= thresholds.get('poor', 0):
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL

    def calculate_overall_score(self, response_time: float, success_rate: float,
                               token_utilization: float, memory_usage: float) -> float:
        """Calculate overall performance score (0.0-1.0)"""
        # Normalize metrics to 0.0-1.0 scale
        response_score = max(0, 1 - (response_time / 2000))  # 2000ms = 0 score
        success_score = success_rate

        # Token utilization score (optimal around 60-80%)
        if 0.6 <= token_utilization <= 0.8:
            token_score = 1.0
        elif token_utilization < 0.6:
            token_score = token_utilization / 0.6
        else:
            token_score = max(0, 2 - (token_utilization / 0.8))

        # Memory efficiency score
        memory_score = max(0, 1 - (memory_usage / 200))  # 200MB = 0 score

        # Weighted average
        weights = {'response': 0.4, 'success': 0.3, 'token': 0.2, 'memory': 0.1}
        overall_score = (
            response_score * weights['response'] +
            success_score * weights['success'] +
            token_score * weights['token'] +
            memory_score * weights['memory']
        )

        return min(1.0, max(0.0, overall_score))

    def generate_optimization_recommendations(self, response_time: float, token_utilization: float,
                                            layer_performance: List[LayerPerformance],
                                            scenario_performance: Dict) -> List[str]:
        """Generate specific optimization recommendations based on performance analysis"""
        recommendations = []

        # Response time recommendations
        if response_time > 1000:
            recommendations.append("CRITICAL: Average response time exceeds 1 second - implement aggressive caching")
            recommendations.append("Consider async processing for non-critical operations")
        elif response_time > 500:
            recommendations.append("Optimize layer coordination to reduce orchestration overhead")
            recommendations.append("Implement result caching for frequently accessed contexts")

        # Token utilization recommendations
        if token_utilization > 0.9:
            recommendations.append("HIGH: Token budget utilization >90% - implement intelligent compression")
            recommendations.append("Review Layer 3 compression algorithms for better efficiency")
        elif token_utilization < 0.3:
            recommendations.append("Consider increasing context richness for better AI reasoning")

        # Layer-specific recommendations
        if layer_performance:
            slowest_layer = max(layer_performance, key=lambda x: x.avg_response_time_ms)
            if slowest_layer.avg_response_time_ms > response_time * 0.5:
                recommendations.append(f"Optimize {slowest_layer.layer_name} - contributing {slowest_layer.avg_response_time_ms:.1f}ms")

            least_efficient = min(layer_performance, key=lambda x: x.token_efficiency)
            if least_efficient.token_efficiency < 10:
                recommendations.append(f"Improve {least_efficient.layer_name} token efficiency - only {least_efficient.token_efficiency:.1f} tokens/ms")

        # Memory recommendations
        high_memory_scenarios = []
        for scenario, metrics_list in scenario_performance.items():
            avg_memory = statistics.mean([abs(m.memory_usage_mb) for m in metrics_list])
            if avg_memory > 50:
                high_memory_scenarios.append((scenario, avg_memory))

        if high_memory_scenarios:
            recommendations.append("Memory optimization needed for scenarios: " +
                                  ", ".join([f"{s} ({m:.1f}MB)" for s, m in high_memory_scenarios]))

        # General recommendations
        if not recommendations:
            recommendations.append("Performance is within acceptable ranges - monitor for regressions")
            recommendations.append("Consider A/B testing new optimization strategies")

        return recommendations

    def analyze_historical_trends(self) -> Dict[str, float]:
        """Analyze historical performance trends"""
        conn = sqlite3.connect(self.perf_db_path)
        cursor = conn.cursor()

        # Get recent performance data (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)

        cursor.execute('''
            SELECT response_time_ms, tokens_used, memory_usage_mb, success
            FROM performance_metrics
            WHERE timestamp > ? AND success = 1
            ORDER BY timestamp DESC
        ''', (yesterday,))

        recent_data = cursor.fetchall()
        conn.close()

        trends = {}

        if len(recent_data) > 5:  # Need sufficient data for trends
            response_times = [row[0] for row in recent_data]
            token_usage = [row[1] for row in recent_data]
            memory_usage = [row[2] for row in recent_data]

            # Calculate trend indicators (simplified linear trend)
            trends['response_time_trend'] = self.calculate_trend(response_times)
            trends['token_usage_trend'] = self.calculate_trend(token_usage)
            trends['memory_usage_trend'] = self.calculate_trend(memory_usage)
            trends['data_points'] = len(recent_data)
        else:
            trends['insufficient_data'] = True

        return trends

    def calculate_trend(self, data: List[float]) -> float:
        """Calculate simple trend indicator (-1 to +1, negative = improving)"""
        if len(data) < 2:
            return 0.0

        # Compare first half to second half
        mid = len(data) // 2
        first_half_avg = statistics.mean(data[:mid])
        second_half_avg = statistics.mean(data[mid:])

        if first_half_avg == 0:
            return 0.0

        # Return normalized trend (-1 = 50% improvement, +1 = 50% degradation)
        trend = (second_half_avg - first_half_avg) / first_half_avg
        return max(-1.0, min(1.0, trend))

    def store_benchmark_report(self, report: SystemPerformanceReport):
        """Store comprehensive benchmark report"""
        conn = sqlite3.connect(self.perf_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO system_benchmarks
            (timestamp, overall_score, performance_level, avg_response_time_ms,
             token_budget_utilization, memory_efficiency, layer_performance, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.timestamp,
            report.overall_score,
            report.performance_level.value,
            report.avg_response_time_ms,
            report.token_budget_utilization,
            report.memory_efficiency,
            json.dumps([asdict(lp) for lp in report.layer_performance]),
            json.dumps(report.optimization_recommendations)
        ))

        conn.commit()
        conn.close()

    def check_performance_alerts(self, report: SystemPerformanceReport):
        """Check for performance alerts and store if necessary"""
        alerts = []

        # Critical performance alerts
        if report.performance_level == PerformanceLevel.CRITICAL:
            alerts.append(("CRITICAL", "System performance has reached critical levels"))

        if report.avg_response_time_ms > 2000:
            alerts.append(("HIGH", f"Response time exceeded 2 seconds: {report.avg_response_time_ms:.1f}ms"))

        if report.token_budget_utilization > 0.95:
            alerts.append(("HIGH", f"Token budget near limit: {report.token_budget_utilization*100:.1f}%"))

        # Layer-specific alerts
        for layer_perf in report.layer_performance:
            if layer_perf.success_rate < 0.8:
                alerts.append(("MEDIUM", f"{layer_perf.layer_name} success rate low: {layer_perf.success_rate*100:.1f}%"))

        # Store alerts
        if alerts:
            conn = sqlite3.connect(self.perf_db_path)
            cursor = conn.cursor()

            for severity, message in alerts:
                cursor.execute('''
                    INSERT INTO performance_alerts
                    (timestamp, alert_type, severity, message, metrics)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    datetime.now(),
                    "PERFORMANCE",
                    severity,
                    message,
                    json.dumps(asdict(report))
                ))

            conn.commit()
            conn.close()

            self.logger.warning(f"Generated {len(alerts)} performance alerts")

    def print_performance_report(self, report: SystemPerformanceReport):
        """Print comprehensive performance report"""
        print("\n" + "="*80)
        print("🚀 COCO 4-LAYER ARCHITECTURE PERFORMANCE REPORT")
        print("="*80)

        # Overall performance
        print(f"\n📊 OVERALL PERFORMANCE")
        print(f"   🎯 Score: {report.overall_score:.3f}/1.000")
        print(f"   📈 Level: {report.performance_level.value.upper()}")
        print(f"   ⚡ Avg Response: {report.avg_response_time_ms:.1f}ms")
        print(f"   🧠 Token Usage: {report.token_budget_utilization*100:.1f}% of budget")
        print(f"   💾 Memory Efficiency: {report.memory_efficiency:.3f}")

        # Layer performance breakdown
        if report.layer_performance:
            print(f"\n🏗️  LAYER PERFORMANCE BREAKDOWN")
            for i, layer in enumerate(report.layer_performance, 1):
                print(f"   {i}. {layer.layer_name}")
                print(f"      ⚡ Response: {layer.avg_response_time_ms:.1f}ms")
                print(f"      🎯 Success Rate: {layer.success_rate*100:.1f}%")
                print(f"      📊 Contribution: {layer.contribution_percentage:.1f}%")
                print(f"      🧠 Token Efficiency: {layer.token_efficiency:.1f} tokens/ms")

        # Optimization recommendations
        if report.optimization_recommendations:
            print(f"\n💡 OPTIMIZATION RECOMMENDATIONS")
            for i, rec in enumerate(report.optimization_recommendations, 1):
                priority = "🔥" if "CRITICAL" in rec else "⚠️" if "HIGH" in rec else "💡"
                print(f"   {i}. {priority} {rec}")

        # Trending analysis
        if report.trending_metrics and not report.trending_metrics.get('insufficient_data'):
            print(f"\n📈 PERFORMANCE TRENDS")
            trends = report.trending_metrics
            trend_indicators = {
                'response_time_trend': ('Response Time', '⚡'),
                'token_usage_trend': ('Token Usage', '🧠'),
                'memory_usage_trend': ('Memory Usage', '💾')
            }

            for key, (name, emoji) in trend_indicators.items():
                if key in trends:
                    trend_val = trends[key]
                    trend_desc = "improving" if trend_val < -0.1 else "stable" if abs(trend_val) < 0.1 else "degrading"
                    trend_icon = "📈" if trend_val < -0.1 else "📊" if abs(trend_val) < 0.1 else "📉"
                    print(f"   {emoji} {name}: {trend_desc} {trend_icon} ({trend_val:+.3f})")

        print("="*80)

async def main():
    """Main performance validation runner"""
    print("🚀 COCO 4-Layer Architecture Performance Validation System")
    print("Advanced benchmarking and optimization analysis")
    print()

    if not ARCHITECTURE_AVAILABLE:
        print("❌ 4-layer architecture not available - cannot run performance validation")
        return 1

    # Initialize performance validator
    validator = PerformanceValidator(enable_monitoring=SYSTEM_MONITORING_AVAILABLE)

    try:
        print("🔧 Running comprehensive performance benchmark suite...")
        print("   This may take several minutes for thorough analysis...")
        print()

        # Run comprehensive benchmarks
        report = await validator.run_comprehensive_benchmark_suite(num_iterations=15)

        # Display results
        validator.print_performance_report(report)

        # Save detailed report
        report_file = Path("performance_validation_report.json")
        with open(report_file, 'w') as f:
            # Convert report to JSON-serializable format
            report_dict = asdict(report)
            report_dict['performance_level'] = report.performance_level.value
            json.dump(report_dict, f, indent=2, default=str)

        print(f"\n📊 Detailed performance report saved to: {report_file}")
        print(f"📈 Performance database: {validator.perf_db_path}")

        # Return appropriate exit code based on performance level
        if report.performance_level in [PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD]:
            print("\n✅ PERFORMANCE VALIDATION PASSED - System ready for production")
            return 0
        elif report.performance_level == PerformanceLevel.ACCEPTABLE:
            print("\n⚠️  PERFORMANCE ACCEPTABLE - Monitor closely and implement optimizations")
            return 0
        else:
            print("\n❌ PERFORMANCE ISSUES DETECTED - Address critical issues before production")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Performance validation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Performance validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))