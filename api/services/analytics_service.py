"""
In-memory analytics singleton — no database needed.
"""
from collections import defaultdict
from statistics import mean


class AnalyticsService:
    def __init__(self):
        self.total_requests = 0
        self.requests_by_endpoint: dict = defaultdict(int)
        self.response_times: list = []
        self.recent_queries: list = []

    def track(self, endpoint: str, query: str, response_time_ms: float):
        self.total_requests += 1
        self.requests_by_endpoint[endpoint] += 1
        self.response_times.append(response_time_ms)
        if query:
            self.recent_queries.append(query)
            self.recent_queries = self.recent_queries[-50:]

    def get_stats(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "requests_by_endpoint": dict(self.requests_by_endpoint),
            "popular_queries": self.recent_queries[-10:],
            "average_response_time_ms": round(mean(self.response_times), 2)
                                        if self.response_times else 0.0,
        }


analytics = AnalyticsService()
