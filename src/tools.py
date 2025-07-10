"""MCP Tool definitions for MCPISIA."""

from typing import List

from mcp.types import Tool


def create_tools() -> List[Tool]:
    """Create and return all available MCP tools."""
    return [
        Tool(
            name="filesystem_read",
            description="Read content from a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="filesystem_write",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="filesystem_list",
            description="List files and directories",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to list (default: current directory)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="memory_store",
            description="Store a value in memory with optional TTL",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key to store the value under"
                    },
                    "value": {
                        "type": "string",
                        "description": "Value to store"
                    },
                    "ttl": {
                        "type": "integer",
                        "description": "Time-to-live in seconds (optional)"
                    }
                },
                "required": ["key", "value"]
            }
        ),
        Tool(
            name="memory_retrieve",
            description="Retrieve a value from memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key to retrieve the value for"
                    }
                },
                "required": ["key"]
            }
        ),
        Tool(
            name="memory_delete",
            description="Delete a value from memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key to delete"
                    }
                },
                "required": ["key"]
            }
        ),
    ]