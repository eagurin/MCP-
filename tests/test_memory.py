"""Tests for memory component."""

import pytest
import asyncio
from src.memory import MemoryComponent


@pytest.fixture
def memory_component():
    """Create a memory component for testing."""
    config = {
        "max_size": 1024,  # 1KB for testing
        "default_ttl": 60,  # 1 minute
        "redis_url": None  # Use in-memory storage for tests
    }
    return MemoryComponent(config)


@pytest.mark.asyncio
async def test_store_and_retrieve(memory_component):
    """Test storing and retrieving values."""
    await memory_component.store("test_key", "test_value")
    
    result = await memory_component.retrieve("test_key")
    assert result == "test_value"


@pytest.mark.asyncio
async def test_nonexistent_key(memory_component):
    """Test retrieving nonexistent key."""
    result = await memory_component.retrieve("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_delete_key(memory_component):
    """Test deleting a key."""
    await memory_component.store("delete_me", "value")
    
    deleted = await memory_component.delete("delete_me")
    assert deleted is True
    
    result = await memory_component.retrieve("delete_me")
    assert result is None


@pytest.mark.asyncio
async def test_ttl_expiration(memory_component):
    """Test TTL expiration."""
    await memory_component.store("ttl_key", "value", ttl=1)  # 1 second TTL
    
    # Should exist immediately
    result = await memory_component.retrieve("ttl_key")
    assert result == "value"
    
    # Wait for expiration
    await asyncio.sleep(1.1)
    
    # Should be expired
    result = await memory_component.retrieve("ttl_key")
    assert result is None


@pytest.mark.asyncio
async def test_memory_stats(memory_component):
    """Test memory statistics."""
    await memory_component.store("stat_key", "value")
    
    stats = memory_component.get_stats()
    assert stats["total_keys"] == 1
    assert stats["total_size_bytes"] > 0
    assert stats["storage_backend"] == "memory"