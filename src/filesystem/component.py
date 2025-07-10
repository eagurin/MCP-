"""Filesystem component implementation."""

import asyncio
import os
import pathlib
from typing import Any, Dict, List, Optional

import aiofiles


class FilesystemComponent:
    """Handles filesystem operations with security and validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.base_path = pathlib.Path(config.get("base_path", "./data"))
        self.max_file_size = config.get("max_file_size", 10485760)  # 10MB
        self.allowed_extensions = set(config.get("allowed_extensions", []))
        
        # Ensure base path exists
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _validate_path(self, path: str) -> pathlib.Path:
        """Validate and normalize a file path."""
        # Convert to Path object and resolve
        file_path = pathlib.Path(path)
        
        # If relative, make it relative to base_path
        if not file_path.is_absolute():
            file_path = self.base_path / file_path
        
        # Resolve to handle .. and . components
        file_path = file_path.resolve()
        
        # Ensure the path is within base_path
        try:
            file_path.relative_to(self.base_path.resolve())
        except ValueError:
            raise PermissionError(f"Path {path} is outside allowed directory")
        
        return file_path
    
    def _validate_extension(self, path: pathlib.Path) -> None:
        """Validate file extension if restrictions are configured."""
        if self.allowed_extensions and path.suffix.lower() not in self.allowed_extensions:
            raise ValueError(
                f"File extension {path.suffix} not allowed. "
                f"Allowed: {', '.join(self.allowed_extensions)}"
            )
    
    async def read_file(self, path: str) -> str:
        """Read content from a file."""
        file_path = self._validate_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        # Check file size
        if file_path.stat().st_size > self.max_file_size:
            raise ValueError(f"File too large: {file_path.stat().st_size} > {self.max_file_size}")
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def write_file(self, path: str, content: str) -> None:
        """Write content to a file."""
        file_path = self._validate_path(path)
        self._validate_extension(file_path)
        
        # Check content size
        content_bytes = content.encode('utf-8')
        if len(content_bytes) > self.max_file_size:
            raise ValueError(f"Content too large: {len(content_bytes)} > {self.max_file_size}")
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    async def list_directory(self, path: str = ".") -> List[Dict[str, Any]]:
        """List files and directories at the given path."""
        dir_path = self._validate_path(path)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        items = []
        for item in dir_path.iterdir():
            try:
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": stat.st_mtime,
                    "permissions": oct(stat.st_mode)[-3:],
                })
            except (OSError, PermissionError):
                # Skip inaccessible items
                continue
        
        return sorted(items, key=lambda x: (x["type"] == "file", x["name"]))
    
    async def create_directory(self, path: str) -> None:
        """Create a directory."""
        dir_path = self._validate_path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
    
    async def delete_file(self, path: str) -> bool:
        """Delete a file."""
        file_path = self._validate_path(path)
        
        if not file_path.exists():
            return False
        
        if file_path.is_file():
            file_path.unlink()
            return True
        else:
            raise ValueError(f"Path is not a file: {path}")
    
    async def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        try:
            file_path = self._validate_path(path)
            return file_path.exists() and file_path.is_file()
        except (PermissionError, ValueError):
            return False