# core/security/rate_limiting.py
class AdaptiveRateLimiter:
    """
    AI-driven adaptive rate limiting based on client behavior and threat level
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.rate_windows = self._initialize_rate_windows()
        self.behavior_analyzer = ClientBehaviorAnalyzer()
        self.anomaly_detector = RateLimitAnomalyDetector()
        
    def _initialize_rate_windows(self) -> Dict:
        return {
            "second": {"window": 1, "limits": {}},
            "minute": {"window": 60, "limits": {}},
            "hour": {"window": 3600, "limits": {}},
            "day": {"window": 86400, "limits": {}}
        }
    
    async def check_rate_limit(self, client_id: str, endpoint: str, context: APISecurityContext) -> Dict:
        """Check adaptive rate limits for client and endpoint"""
        # Get base limits for client tier
        base_limits = self._get_base_limits(context.rate_limit_tier, endpoint)
        
        # Adjust limits based on behavior and threat
        adaptive_limits = await self._calculate_adaptive_limits(client_id, base_limits, context)
        
        # Check all rate windows
        for window_name, window_config in self.rate_windows.items():
            current_count = await self._get_request_count(client_id, endpoint, window_name)
            window_limit = adaptive_limits[window_name]
            
            if current_count >= window_limit:
                return {
                    "allowed": False,
                    "window": window_name,
                    "current": current_count,
                    "limit": window_limit,
                    "retry_after": window_config['window']
                }
        
        # Increment counters
        await self._increment_request_counters(client_id, endpoint)
        
        # Analyze behavior for future adjustments
        asyncio.create_task(self._analyze_client_behavior(client_id, endpoint, context))
        
        return {
            "allowed": True,
            "limits": adaptive_limits,
            "current_usage": await self._get_current_usage(client_id, endpoint)
        }
    
    async def _calculate_adaptive_limits(self, client_id: str, base_limits: Dict, context: APISecurityContext) -> Dict:
        """Calculate adaptive limits based on client behavior"""
        behavior_profile = await self.behavior_analyzer.get_behavior_profile(client_id)
        threat_level = context.threat_level
        
        adaptive_limits = base_limits.copy()
        
        # Adjust based on threat level
        if threat_level > 0.7:
            # High threat - reduce limits
            for window in adaptive_limits:
                adaptive_limits[window] = int(adaptive_limits[window] * 0.5)
        elif threat_level < 0.3 and behavior_profile.get('trust_score', 0) > 0.8:
            # Low threat + trusted behavior - increase limits
            for window in adaptive_limits:
                adaptive_limits[window] = int(adaptive_limits[window] * 1.5)
        
        # Adjust based on historical behavior
        if behavior_profile.get('consistent_usage', False):
            for window in adaptive_limits:
                adaptive_limits[window] = int(adaptive_limits[window] * 1.2)
        
        return adaptive_limits
