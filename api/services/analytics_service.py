"""
In-memory analytics singleton — tracks queries, tools, and performance.
"""
import time
from datetime import datetime
from collections import defaultdict, Counter
from statistics import mean


class AnalyticsService:
    def __init__(self):
        self.total_requests = 0
        self.requests_by_endpoint: dict = defaultdict(int)
        self.tool_usage_counts: dict = defaultdict(int)
        self.query_category_counts: dict = defaultdict(int)
        self.model_usage: dict = defaultdict(int)
        self.hourly_distribution: dict = {f"{h:02d}": 0 for h in range(24)}
        self.response_times: list = []
        self.recent_queries: list = []  # List of dicts
        self.popular_query_counter = Counter()

    def _classify_query(self, query: str) -> str:
        q = query.lower()
        
        categories = {
            "regulations": ["dgca", "rule", "law", "legal", "permit", "licence", "license", "comply", "compliance", "allowed", "register", "registration", "zone", "restrict"],
            "flight_ops": ["flight time", "battery", "fly", "range", "altitude", "speed", "wind", "payload", "weight"],
            "business_roi": ["roi", "profit", "revenue", "invest", "cost", "break-even", "breakeven", "return", "income", "business", "earn", "money"],
            "drone_specs": ["drone model", "which drone", "recommend", "buy", "select", "best drone", "compare", "specification", "price", "cost of drone"],
            "companies": ["company", "startup", "manufacturer", "ideaforge", "garuda", "skye", "marut"],
            "training": ["training", "institute", "course", "rpas", "pilot", "certification", "dgca exam", "school"],
        }
        
        for category, keywords in categories.items():
            if any(k in q for k in keywords):
                return category
        return "general"

    def track(self, endpoint: str, query: str, response_time_ms: float, tool_used: str = "", model_used: str = ""):
        self.total_requests += 1
        self.requests_by_endpoint[endpoint] += 1
        self.response_times.append(response_time_ms)
        
        # Track Hour
        hour_str = datetime.now().strftime("%H")
        self.hourly_distribution[hour_str] += 1
        
        # Track Tool and Model
        if tool_used:
            self.tool_usage_counts[tool_used] += 1
        else:
            self.tool_usage_counts["direct"] += 1
            
        if model_used:
            self.model_usage[model_used] += 1
        else:
            self.model_usage["direct"] += 1

        # Classify and Track Query
        if query:
            category = self._classify_query(query)
            self.query_category_counts[category] += 1
            
            # Recent Queries
            entry = {
                "query": query,
                "tool_used": tool_used or "direct",
                "response_time_ms": response_time_ms,
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
            self.recent_queries.append(entry)
            self.recent_queries = self.recent_queries[-100:]
            
            # Popular Queries (Normalize)
            norm_q = query.lower().strip()
            self.popular_query_counter[norm_q] += 1

    def get_stats(self) -> dict:
        sorted_times = sorted(self.response_times)
        p95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0.0
        
        # Popular queries appearing more than once
        popular = [
            {"query": q, "count": count} 
            for q, count in self.popular_query_counter.most_common(10)
            if count > 1
        ]

        return {
            "generated_at": datetime.now().isoformat(),
            "total_requests": self.total_requests,
            "requests_by_endpoint": dict(self.requests_by_endpoint),
            "tool_usage_counts": dict(self.tool_usage_counts),
            "query_category_counts": dict(self.query_category_counts),
            "response_times": {
                "avg": round(mean(self.response_times), 2) if self.response_times else 0.0,
                "min": min(self.response_times) if self.response_times else 0.0,
                "max": max(self.response_times) if self.response_times else 0.0,
                "p95": round(p95, 2)
            },
            "recent_queries": self.recent_queries[::-1], # Most recent first
            "popular_queries": popular,
            "hourly_distribution": self.hourly_distribution,
            "model_usage": dict(self.model_usage)
        }


analytics = AnalyticsService()
