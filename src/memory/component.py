"""Memory component implementation."""

import asyncio
import json
import time
from typing import Any, Dict, Optional, Union

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class MemoryComponent:
    """Handles in-memory and persistent storage with TTL support."""
    
    def __init__(self, config: Dict[str, Any]):
        self.max_size = config.get("max_size", 268435456)  # 256MB
        self.default_ttl = config.get("default_ttl", 3600)  # 1 hour
        self.redis_url = config.get("redis_url")
        
        # In-memory storage fallback
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._total_size = 0
        
        # Redis client (if available and configured)
        self._redis_client = None
        if REDIS_AVAILABLE and self.redis_url:
            try:
                self._redis_client = redis.from_url(self.redis_url)
            except Exception:
                # Fall back to in-memory storage
                pass
    
    def _get_size(self, value: Any) -> int:
        """Calculate approximate size of a value in bytes."""
        if isinstance(value, str):
            return len(value.encode('utf-8'))
        elif isinstance(value, (int, float)):
            return 8
        elif isinstance(value, bool):
            return 1
        else:
            # For complex objects, use JSON serialization size
            return len(json.dumps(value).encode('utf-8'))
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from in-memory storage."""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self._memory_store.items():
            if data["expires_at"] and current_time > data["expires_at"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_from_memory(key)
    
    def _remove_from_memory(self, key: str) -> bool:
        """Remove a key from in-memory storage."""
        if key in self._memory_store:
            data = self._memory_store.pop(key)
            self._total_size -= data["size"]
            return True
        return False
    
    def _ensure_space(self, required_size: int) -> None:
        """Ensure there's enough space by removing old entries if needed."""
        self._cleanup_expired()
        
        # If still not enough space, remove oldest entries (LRU-style)
        while self._total_size + required_size > self.max_size and self._memory_store:
            # Find oldest entry
            oldest_key = min(self._memory_store.keys(), 
                           key=lambda k: self._memory_store[k]["created_at"])
            self._remove_from_memory(oldest_key)
    
    async def store(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value with optional TTL."""
        if ttl is None:
            ttl = self.default_ttl
        
        # Try Redis first if available
        if self._redis_client:
            try:
                serialized_value = json.dumps(value)
                if ttl > 0:
                    await self._redis_client.setex(key, ttl, serialized_value)
                else:
                    await self._redis_client.set(key, serialized_value)
                return
            except Exception:
                # Fall back to in-memory storage
                pass
        
        # In-memory storage
        size = self._get_size(value)
        self._ensure_space(size)
        
        current_time = time.time()
        expires_at = current_time + ttl if ttl > 0 else None
        
        # Remove existing entry if it exists
        if key in self._memory_store:
            self._remove_from_memory(key)
        
        self._memory_store[key] = {
            "value": value,
            "created_at": current_time,
            "expires_at": expires_at,
            "size": size
        }
        self._total_size += size
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        # Try Redis first if available
        if self._redis_client:
            try:
                value = await self._redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception:
                # Fall back to in-memory storage
                pass
        
        # In-memory storage
        self._cleanup_expired()
        
        if key in self._memory_store:
            data = self._memory_store[key]
            if data["expires_at"] is None or time.time() <= data["expires_at"]:
                return data["value"]
            else:
                # Expired, remove it
                self._remove_from_memory(key)
        
        return None
    
    async def delete(self, key: str) -> bool:
        """Delete a value by key."""
        deleted = False
        
        # Try Redis first if available
        if self._redis_client:
            try:
                result = await self._redis_client.delete(key)
                deleted = result > 0
            except Exception:
                pass
        
        # In-memory storage
        if self._remove_from_memory(key):
            deleted = True
        
        return deleted
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        # Try Redis first if available
        if self._redis_client:
            try:
                return await self._redis_client.exists(key) > 0
            except Exception:
                pass
        
        # In-memory storage
        self._cleanup_expired()
        return key in self._memory_store
    
    async def clear(self) -> None:
        """Clear all stored values."""
        # Try Redis first if available
        if self._redis_client:
            try:
                await self._redis_client.flushdb()
            except Exception:
                pass
        
        # In-memory storage
        self._memory_store.clear()
        self._total_size = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        self._cleanup_expired()
        
        return {
            "total_keys": len(self._memory_store),
            "total_size_bytes": self._total_size,
            "max_size_bytes": self.max_size,
            "utilization_percent": (self._total_size / self.max_size) * 100,
            "storage_backend": "redis" if self._redis_client else "memory"
        }