"""
Simple cache to reduce API calls
"""
import hashlib
import json
from typing import Dict, Any, Optional


class QueryCache:
    """Cache for query results to reduce API calls"""
    
    def __init__(self, max_size: int = 50):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
    
    def _get_key(self, query: str, schema: str) -> str:
        """Generate cache key from query and schema"""
        combined = f"{query}||{schema}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get_plan(self, query: str, schema: str) -> Optional[Dict[str, Any]]:
        """Get cached plan if exists"""
        key = self._get_key(query, schema)
        return self.cache.get(key)
    
    def set_plan(self, query: str, schema: str, plan: Dict[str, Any]):
        """Cache a plan"""
        key = self._get_key(query, schema)
        
        # Implement simple LRU by removing oldest if full
        if len(self.cache) >= self.max_size:
            # Remove first item (oldest)
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[key] = plan
    
    def clear(self):
        """Clear all cached plans"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size
        }
