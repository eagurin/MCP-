"""Tests for filesystem component."""

import pytest
import tempfile
import pathlib
from src.filesystem import FilesystemComponent


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.fixture
def filesystem_component(temp_dir):
    """Create a filesystem component with temp directory."""
    config = {
        "base_path": str(temp_dir),
        "max_file_size": 1024,  # 1KB for testing
        "allowed_extensions": [".txt", ".json"]
    }
    return FilesystemComponent(config)


@pytest.mark.asyncio
async def test_write_and_read_file(filesystem_component):
    """Test writing and reading a file."""
    content = "Hello, MCPISIA!"
    await filesystem_component.write_file("test.txt", content)
    
    result = await filesystem_component.read_file("test.txt")
    assert result == content


@pytest.mark.asyncio
async def test_list_directory(filesystem_component):
    """Test listing directory contents."""
    await filesystem_component.write_file("file1.txt", "content1")
    await filesystem_component.write_file("file2.txt", "content2")
    
    items = await filesystem_component.list_directory(".")
    assert len(items) == 2
    assert any(item["name"] == "file1.txt" for item in items)
    assert any(item["name"] == "file2.txt" for item in items)


@pytest.mark.asyncio
async def test_file_size_limit(filesystem_component):
    """Test file size limitations."""
    large_content = "x" * 2048  # 2KB, larger than 1KB limit
    
    with pytest.raises(ValueError, match="Content too large"):
        await filesystem_component.write_file("large.txt", large_content)


@pytest.mark.asyncio
async def test_extension_validation(filesystem_component):
    """Test file extension validation."""
    with pytest.raises(ValueError, match="not allowed"):
        await filesystem_component.write_file("test.py", "print('hello')")