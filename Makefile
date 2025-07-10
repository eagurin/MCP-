# GitHub Agent Orchestrator

.PHONY: run install format lint clean status help cli tasks agents assign check

help: ## Show help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

run: ## Start orchestrator
	@test -f .env || (echo "Create .env file first" && exit 1)
	uv run run.py

cli: ## Interactive CLI
	@test -f .env || (echo "Create .env file first" && exit 1)
	uv run agent_cli.py

status: ## Check status
	uv run run.py --status

install: ## Install dependencies
	uv sync

tasks: ## Show GitHub issues
	uv run agent_cli.py tasks

agents: ## Show active agents
	uv run agent_cli.py agents

assign: ## Assign agent to task (make assign TASK=123)
	@test -n "$(TASK)" || (echo "Usage: make assign TASK=123" && exit 1)
	uv run agent_cli.py assign $(TASK)

format: ## Format code
	uv run ruff format .

lint: ## Lint code
	uv run ruff check .

check: ## Quick check
	uv run ruff check . --no-fix

clean: ## Clean temp files
	rm -rf __pycache__ .ruff_cache *.log 