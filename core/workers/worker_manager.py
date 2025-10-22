# core/workers/worker_manager.py
import asyncio
import multiprocessing
from typing import List, Dict, Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import psutil
import os

class EnterpriseWorkerManager:
    def __init__(self, config: Dict):
        self.config = config
        self.worker_pool = {}
        self.task_queue = asyncio.Queue()
        self.performance_monitor = WorkerPerformanceMonitor()
        self.auto_scaling = AutoScalingManager()
        
    async def initialize_workers(self):
        """Initialize worker pool based on system resources"""
        cpu_count = multiprocessing.cpu_count()
        available_ram = psutil.virtual_memory().available / (1024 ** 3)  # GB
        
        # Calculate optimal worker count
        optimal_workers = self._calculate_optimal_workers(cpu_count, available_ram)
        
        logger.info(f"🚀 Initializing {optimal_workers} workers...")
        
        # Create worker processes
        for i in range(optimal_workers):
            worker = await self._create_worker(i)
            self.worker_pool[worker.worker_id] = worker
        
        # Start task distributor
        asyncio.create_task(self._distribute_tasks())
        
        # Start performance monitoring
        asyncio.create_task(self.performance_monitor.monitor_workers())
        
        # Start auto-scaling
        asyncio.create_task(self.auto_scaling.manage_scaling(self))
    
    def _calculate_optimal_workers(self, cpu_count: int, available_ram: float) -> int:
        """Calculate optimal number of workers"""
        # Conservative resource allocation
        cpu_workers = max(1, cpu_count - 2)  # Leave 2 cores for system
        ram_workers = int(available_ram / 2)  # 2GB per worker
        
        return min(cpu_workers, ram_workers, 16)  # Max 16 workers
    
    async def submit_task(self, task_type: str, payload: Dict, priority: int = 1) -> str:
        """Submit task to worker system"""
        task_id = self._generate_task_id()
        
        task = {
            'task_id': task_id,
            'type': task_type,
            'payload': payload,
            'priority': priority,
            'submitted_at': time.time(),
            'status': 'queued'
        }
        
        await self.task_queue.put(task)
        return task_id
    
    async def _distribute_tasks(self):
        """Intelligent task distribution to workers"""
        while True:
            try:
                task = await self.task_queue.get()
                
                # Select optimal worker for this task type
                optimal_worker = self._select_optimal_worker(task)
                
                if optimal_worker:
                    await optimal_worker.assign_task(task)
                else:
                    # No available worker, implement backpressure
                    await asyncio.sleep(0.1)
                    await self.task_queue.put(task)  # Requeue
                
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Task distribution error: {e}")
                await asyncio.sleep(1)

class SpecializedWorkers:
    """Specialized worker types for different tasks"""
    
    class ScrapingWorker:
        def __init__(self, worker_id: int):
            self.worker_id = worker_id
            self.specialization = "scraping"
            self.proxy_manager = EnterpriseProxyManager()
            self.rate_limiter = AdaptiveRateLimiter()
            
        async def process_scraping_task(self, task: Dict):
            """Process scraping tasks with intelligent rate limiting"""
            target = task['payload']['target']
            
            # Get optimal proxy
            proxy = await self.proxy_manager.get_optimal_proxy(target, "scraping")
            
            # Apply rate limiting based on target sensitivity
            await self.rate_limiter.wait_if_needed(target)
            
            # Execute scraping with error handling and retries
            result = await self._execute_scraping_with_retry(target, proxy)
            
            return result
    
    class AnalysisWorker:
        def __init__(self, worker_id: int):
            self.worker_id = worker_id
            self.specialization = "analysis"
            self.ml_models = self._load_ml_models()
            
        async def process_analysis_task(self, task: Dict):
            """Process AI analysis tasks"""
            analysis_type = task['payload']['analysis_type']
            data = task['payload']['data']
            
            # Load appropriate ML model
            model = self.ml_models.get(analysis_type)
            
            if not model:
                raise Exception(f"Unknown analysis type: {analysis_type}")
            
            # Perform analysis with resource monitoring
            result = await self._perform_analysis_with_monitoring(model, data)
            
            return result
    
    class NetworkWorker:
        def __init__(self, worker_id: int):
            self.worker_id = worker_id
            self.specialization = "network"
            self.dns_manager = EnterpriseDNSManager()
            
        async def process_network_task(self, task: Dict):
            """Process network-intensive tasks"""
            operation = task['payload']['operation']
            
            if operation == "dns_resolution":
                domains = task['payload']['domains']
                results = {}
                
                for domain in domains:
                    result = await self.dns_manager.smart_dns_resolution(domain)
                    results[domain] = result
                
                return results
