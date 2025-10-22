# core/network/dns_manager.py
import aiodns
import asyncio
from typing import List, Dict
import time

class EnterpriseDNSManager:
    def __init__(self):
        self.resolver = aiodns.DNSResolver()
        self.dns_cache = {}
        self.dns_servers = [
            '8.8.8.8',  # Google
            '1.1.1.1',  # Cloudflare
            '9.9.9.9',  # Quad9
            '208.67.222.222'  # OpenDNS
        ]
        self.performance_stats = {}
        
    async def smart_dns_resolution(self, domain: str, query_type: str = 'A') -> Dict:
        """AI-driven DNS resolution with fallback and optimization"""
        # Check cache first
        cache_key = f"{domain}_{query_type}"
        if cache_key in self.dns_cache:
            cached = self.dns_cache[cache_key]
            if time.time() - cached['timestamp'] < 300:  # 5 minute cache
                return cached['result']
        
        # Try different DNS servers intelligently
        results = []
        for dns_server in self.dns_servers:
            try:
                result = await self._resolve_with_server(domain, query_type, dns_server)
                results.append(result)
                
                # Update performance stats
                self._update_dns_performance(dns_server, True)
                
            except Exception as e:
                self._update_dns_performance(dns_server, False)
                continue
        
        if not results:
            raise Exception(f"DNS resolution failed for {domain}")
        
        # Select best result based on multiple factors
        best_result = self._select_best_dns_result(results, domain)
        
        # Cache the result
        self.dns_cache[cache_key] = {
            'result': best_result,
            'timestamp': time.time(),
            'source': best_result['source']
        }
        
        return best_result
    
    def _select_best_dns_result(self, results: List[Dict], domain: str) -> Dict:
        """AI-driven selection of best DNS result"""
        scored_results = []
        
        for result in results:
            score = self._calculate_dns_result_score(result, domain)
            scored_results.append((result, score))
        
        return max(scored_results, key=lambda x: x[1])[0]
    
    def _calculate_dns_result_score(self, result: Dict, domain: str) -> float:
        """Calculate score for DNS result quality"""
        scores = {
            "response_time": max(0, 1 - (result['response_time'] / 2.0)),  # Faster = better
            "ttl_optimal": 1.0 if 300 <= result['ttl'] <= 3600 else 0.5,  # Optimal TTL
            "server_reliability": self.performance_stats.get(result['source'], {}).get('reliability', 0.5),
            "geographic_relevance": self._calculate_geo_relevance(result, domain)
        }
        
        return sum(scores.values()) / len(scores)
