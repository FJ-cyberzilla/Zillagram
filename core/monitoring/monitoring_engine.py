# core/monitoring/monitoring_engine.py
import asyncio
import time
import psutil
import platform
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import logging

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_usage: float
    disk_usage: float
    network_io: Dict
    process_count: int
    system_load: List[float]

class EnterpriseMonitoring:
    """
    Comprehensive monitoring for system, network, application, and business metrics
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.metrics_collector = MetricsCollector(config)
        self.alert_manager = AlertManager(config)
        self.performance_analyzer = PerformanceAnalyzer(config)
        self.dashboard_reporter = DashboardReporter(config)
        
        # Prometheus metrics
        self.metrics = self._initialize_prometheus_metrics()
        
    def _initialize_prometheus_metrics(self) -> Dict:
        """Initialize Prometheus metrics for monitoring"""
        return {
            'requests_total': Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status']),
            'request_duration': Histogram('http_request_duration_seconds', 'HTTP request duration'),
            'system_cpu': Gauge('system_cpu_usage', 'System CPU usage percentage'),
            'system_memory': Gauge('system_memory_usage', 'System memory usage percentage'),
            'active_connections': Gauge('active_connections', 'Active network connections'),
            'queue_size': Gauge('task_queue_size', 'Current task queue size'),
            'error_rate': Gauge('error_rate', 'Application error rate')
        }
    
    async def start_comprehensive_monitoring(self):
        """Start all monitoring systems"""
        monitoring_tasks = [
            self._monitor_system_resources(),
            self._monitor_network_activity(),
            self._monitor_application_performance(),
            self._monitor_business_metrics(),
            self._monitor_security_events(),
            self._monitor_compliance_metrics()
        ]
        
        for task in monitoring_tasks:
            asyncio.create_task(task)
        
        logger.info("📊 Comprehensive monitoring system started")
    
    async def _monitor_system_resources(self):
        """Monitor system resource usage with predictive analytics"""
        while True:
            try:
                metrics = await self.metrics_collector.collect_system_metrics()
                
                # Update Prometheus metrics
                self.metrics['system_cpu'].set(metrics.cpu_percent)
                self.metrics['system_memory'].set(metrics.memory_usage)
                
                # Check thresholds and trigger alerts
                await self._check_system_thresholds(metrics)
                
                # Predictive capacity planning
                await self._analyze_capacity_trends(metrics)
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_network_activity(self):
        """Monitor network performance and security"""
        while True:
            try:
                network_metrics = await self.metrics_collector.collect_network_metrics()
                
                # Monitor connection patterns
                connection_analysis = await self._analyze_network_patterns(network_metrics)
                
                # Detect network anomalies
                anomalies = await self._detect_network_anomalies(network_metrics)
                if anomalies:
                    await self.alert_manager.trigger_alert("NETWORK_ANOMALY", anomalies)
                
                # Monitor bandwidth usage
                await self._analyze_bandwidth_usage(network_metrics)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_application_performance(self):
        """Monitor application performance and health"""
        while True:
            try:
                app_metrics = await self.metrics_collector.collect_application_metrics()
                
                # Track key performance indicators
                kpis = {
                    'response_time': app_metrics.get('avg_response_time', 0),
                    'throughput': app_metrics.get('requests_per_second', 0),
                    'error_rate': app_metrics.get('error_percentage', 0),
                    'concurrent_users': app_metrics.get('active_users', 0)
                }
                
                # Update Prometheus metrics
                self.metrics['error_rate'].set(kpis['error_rate'])
                
                # Check performance thresholds
                if kpis['response_time'] > 2.0:  # 2 seconds threshold
                    await self.alert_manager.trigger_alert("HIGH_RESPONSE_TIME", kpis)
                
                if kpis['error_rate'] > 1.0:  # 1% error rate threshold
                    await self.alert_manager.trigger_alert("HIGH_ERROR_RATE", kpis)
                
                # Performance trend analysis
                await self._analyze_performance_trends(app_metrics)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Application monitoring error: {e}")
                await asyncio.sleep(60)
