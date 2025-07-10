# GitHub Agent Orchestrator

**AI-powered GitHub issue management with Claude agents**

## Quick Start

```bash
# Setup environment
cp .env.example .env
# Edit .env with your tokens

# Install and run
uv run run.py
```

## Configuration

Create `.env` file:

```bash
GITHUB_TOKEN=your_github_token
GITHUB_REPO=owner/repo_name
ANTHROPIC_API_KEY=your_anthropic_key  # optional
```

## Commands

```bash
# Status check
python run.py --status

# Install dependencies  
python run.py --install-deps

# Interactive CLI
python agent_cli.py

# Make commands
make run        # Start orchestrator
make cli        # Interactive interface
make status     # Check system status
```

## How it works

1. **Monitor GitHub Issues** - Scans open issues in your repo
2. **Manual Agent Control** - You decide which agents to create via CLI
3. **Execute Tasks** - Agents analyze and work on assigned issues
4. **Health Monitoring** - Track agent status and health
5. **Progress Updates** - Comments and status updates in GitHub

## Project Structure

```
├── src/                # Source code
├── run.py             # Main launcher
├── orchestrator.py    # Orchestrator launcher  
├── agent_cli.py       # Interactive CLI
├── Makefile          # Development commands
└── pyproject.toml    # Dependencies & config
```

## Development

```bash
# Code quality
make format lint check

# Agent management
make tasks agents assign TASK=123
```

Built with [UV](https://github.com/astral-sh/uv) for fast dependency management.
