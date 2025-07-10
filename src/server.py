#!/usr/bin/env python3
"""MCPISIA MCP Server Implementation."""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ClientCapabilities, ServerCapabilities, Tool

from .filesystem import FilesystemComponent
from .memory import MemoryComponent
from .tools import create_tools


logger = logging.getLogger(__name__)


class MCPISIAServer:
    """Main MCPISIA MCP Server."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.server = Server("mcpisia")
        self.filesystem = FilesystemComponent(self.config.get("filesystem", {}))
        self.memory = MemoryComponent(self.config.get("memory", {}))
        self._setup_handlers()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment and files."""
        return {
            "filesystem": {
                "base_path": os.getenv("FILESYSTEM_BASE_PATH", "./data"),
                "max_file_size": int(os.getenv("FILESYSTEM_MAX_FILE_SIZE", "10485760")),
                "allowed_extensions": os.getenv(
                    "FILESYSTEM_ALLOWED_EXTENSIONS", 
                    ".txt,.json,.yaml,.yml,.md,.log"
                ).split(","),
            },
            "memory": {
                "max_size": int(os.getenv("MEMORY_MAX_SIZE", "268435456")),
                "default_ttl": int(os.getenv("MEMORY_DEFAULT_TTL", "3600")),
                "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            },
            "server": {
                "host": os.getenv("HOST", "localhost"),
                "port": int(os.getenv("PORT", "8000")),
                "debug": os.getenv("DEBUG", "false").lower() == "true",
            }
        }
    
    def _setup_handlers(self) -> None:
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return create_tools()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Handle tool calls."""
            logger.info(f"Tool called: {name} with args: {arguments}")
            
            try:
                if name == "filesystem_read":
                    content = await self.filesystem.read_file(arguments["path"])
                    return [{"type": "text", "text": content}]
                
                elif name == "filesystem_write":
                    await self.filesystem.write_file(arguments["path"], arguments["content"])
                    return [{"type": "text", "text": f"File written to {arguments['path']}"}]
                
                elif name == "filesystem_list":
                    files = await self.filesystem.list_directory(arguments.get("path", "."))
                    return [{"type": "text", "text": json.dumps(files, indent=2)}]
                
                elif name == "memory_store":
                    await self.memory.store(
                        arguments["key"], 
                        arguments["value"],
                        ttl=arguments.get("ttl")
                    )
                    return [{"type": "text", "text": f"Stored value for key: {arguments['key']}"}]
                
                elif name == "memory_retrieve":
                    value = await self.memory.retrieve(arguments["key"])
                    if value is None:
                        return [{"type": "text", "text": f"No value found for key: {arguments['key']}"}]
                    return [{"type": "text", "text": str(value)}]
                
                elif name == "memory_delete":
                    deleted = await self.memory.delete(arguments["key"])
                    status = "deleted" if deleted else "not found"
                    return [{"type": "text", "text": f"Key {arguments['key']}: {status}"}]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [{"type": "text", "text": f"Error: {str(e)}"}]
    
    async def run(self) -> None:
        """Run the MCP server."""
        try:
            logger.info("Starting MCPISIA MCP Server...")
            await self.server.run()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise


async def main() -> None:
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    server = MCPISIAServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())