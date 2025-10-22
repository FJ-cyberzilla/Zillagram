# core/network/proxy_manager.py
import aiohttp
import asyncio
from typing import List, Dict, Optional
import random
import time
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class ProxyServer:
    id: str
    host: str
    port: int
    protocol: str
    country: str
    latency: float
    success_rate: float
    last_used: float
    health_score: float

class EnterpriseProxyManager:
    def __init__(self, config: Dict):
        self.config = config
        self.proxy_pool: List[ProxyServer] = []
        self.active_sessions: Dict[str, aiohttp.ClientSession] = {}
        self.performance_metrics = {}
        self.rotation_strategy = self._initialize_rotation_strategy()
        
    async def initialize_proxy_pool(self):
        """Initialize and health-check proxy pool"""
        # Load proxies from configured sources
        proxy_sources = [
            self._load_internal_proxies(),
            self._load_premium_providers(),
            self._load_enterprise_gateways()
        ]
        
        for source in proxy_sources:
            proxies = await source
            await self._health_check_proxies(proxies)
        
        logger.info(f"✅ Proxy pool initialized with {len(self.proxy_pool)} healthy proxies")
    
    async def get_optimal_proxy(self, target_url: str, operation_type: str) -> ProxyServer:
        """AI-driven proxy selection based on multiple factors"""
        candidates = self._filter_proxies_by_requirements(target_url, operation_type)
        
        if not candidates:
            raise Exception("No suitable proxies available")
        
        # AI scoring based on multiple factors
        scored_proxies = []
        for proxy in candidates:
            score = self._calculate_proxy_score(proxy, target_url, operation_type)
            scored_proxies.append((proxy, score))
        
        # Select best proxy
        best_proxy = max(scored_proxies, key=lambda x: x[1])[0]
        
        # Update usage metrics
        self._update_proxy_metrics(best_proxy)
        
        return best_proxy
    
    def _calculate_proxy_score(self, proxy: ProxyServer, target_url: str, operation_type: str) -> float:
        """AI-driven scoring for proxy selection"""
        scores = {
            "performance": self._calculate_performance_score(proxy),
            "geographic": self._calculate_geographic_score(proxy, target_url),
            "security": self._calculate_security_score(proxy, operation_type),
            "reliability": proxy.health_score,
            "rotation_balance": self._calculate_rotation_score(proxy)
        }
        
        # Weighted scoring based on operation type
        weights = self._get_weights_for_operation(operation_type)
        
        total_score = sum(scores[factor] * weights[factor] for factor in scores)
        return total_score
    
    def _calculate_geographic_score(self, proxy: ProxyServer, target_url: str) -> float:
        """Calculate geographic optimization score"""
        target_country = self._extract_target_country(target_url)
        
        if target_country and proxy.country == target_country:
            return 0.9  # Same country - good for localization
        elif target_country and self._are_countries_allied(proxy.country, target_country):
            return 0.7  # Allied countries
        else:
            return 0.5  # Neutral
    
    async def rotate_proxy_automatically(self, current_proxy: ProxyServer, failure_reason: str = None):
        """AI-driven automatic proxy rotation"""
        if failure_reason:
            # Learn from failure
            self._update_failure_patterns(current_proxy, failure_reason)
        
        # Get new optimal proxy
        new_proxy = await self.get_optimal_proxy(self.current_target, self.current_operation)
        
        # Implement smooth transition
        await self._graceful_proxy_transition(current_proxy, new_proxy)
        
        return new_proxy
    
    async def _health_check_proxies(self, proxies: List[ProxyServer]):
        """Comprehensive proxy health checking"""
        health_tasks = []
        
        for proxy in proxies:
            task = asyncio.create_task(self._check_proxy_health(proxy))
            health_tasks.append(task)
        
        results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        for proxy, result in zip(proxies, results):
            if isinstance(result, Exception):
                proxy.health_score = 0.0
            else:
                proxy.health_score = result['health_score']
                proxy.latency = result['latency']
                
                if proxy.health_score > 0.7:
                    self.proxy_pool.append(proxy)
