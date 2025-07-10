# MCPИСЯ

**MCP (Model Context Protocol) implementation with GitHub Agent Orchestrator**

## Quick Start

```bash
# Setup environment
cp .env.example .env
# Edit .env with your tokens

# Install and run
uv run run.py
```

## Features

🔧 **MCP Server** - Full implementation with filesystem and memory components
🤖 **GitHub Agent Orchestrator** - AI-powered issue management with Claude agents  
📋 **Interactive CLI** - Manual control over agent assignments
🔍 **Health Monitoring** - Track agent status and performance
💬 **GitHub Integration** - Automatic comments and status updates

## Configuration

Create `.env` file based on `.env.example`:

```bash
# GitHub Agent Orchestrator
GITHUB_TOKEN=your_github_token
GITHUB_REPO=owner/repo_name
ANTHROPIC_API_KEY=your_anthropic_key  # optional

# MCP Server  
FILESYSTEM_BASE_PATH=./data
MEMORY_MAX_SIZE=268435456
REDIS_URL=redis://localhost:6379/0
```

## Commands

### GitHub Agent Orchestrator
```bash
# Status check
python run.py --status

# Install dependencies  
python run.py --install-deps

# Interactive CLI
python agent_cli.py interactive

# Agent management
python agent_cli.py tasks          # Show all issues
python agent_cli.py agents         # Show active agents
python agent_cli.py assign 12      # Assign agent to issue
python agent_cli.py remove 11      # Remove agent from issue

# Make commands
make run        # Start orchestrator
make cli        # Interactive interface
make status     # Check system status
```

### MCP Server
```bash
# Start MCP server
python src/server.py

# Run with uvicorn
uvicorn src.server:app --reload
```

## How it works

### GitHub Agent Orchestrator
1. **Monitor GitHub Issues** - Scans open issues in your repo
2. **Manual Agent Control** - You decide which agents to create via CLI
3. **Execute Tasks** - Agents analyze and work on assigned issues using Claude Squad
4. **Health Monitoring** - Track agent status and health
5. **Progress Updates** - Comments and status updates in GitHub

### MCP Server
1. **Filesystem Component** - Secure file operations with validation
2. **Memory Component** - In-memory storage with TTL support and Redis fallback
3. **Tool Definitions** - Standard MCP-compliant tools for file and memory operations

## Project Structure

```
├── src/                    # Source code
│   ├── server.py          # MCP server implementation
│   ├── tools.py           # MCP tool definitions
│   ├── filesystem/        # Filesystem component
│   ├── memory/            # Memory component
│   ├── main.py            # Orchestrator entry point
│   ├── agents.py          # Claude Squad integration
│   ├── github_manager.py  # GitHub API wrapper
│   ├── health_monitor.py  # Agent health monitoring
│   └── models.py          # Data models
├── run.py                 # Orchestrator launcher
├── orchestrator.py        # Main orchestrator CLI
├── agent_cli.py           # Interactive agent management
├── Makefile              # Development commands
└── pyproject.toml        # Dependencies & config
```

## Development

```bash
# Code quality
make format lint check

# Agent management
make tasks agents assign TASK=123
```

Built with [UV](https://github.com/astral-sh/uv) for fast dependency management.
