# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based testing ground for various MCP (Model Context Protocol) servers that incorporate parsers and databases with documentation. The project is designed to power LLM agents to run in IDEs like VS Code or Claude Desktop.

## Development Environment

This project uses:
- **Python 3.12+** (required)
- **uv** for dependency management (uv.lock file present)
- **cclib** (>=1.8.1) for computational chemistry parsing
- **mcp[cli]** (>=1.13.1) for Model Context Protocol functionality

## Common Commands
```bash
# Install dependencies
uv sync

# Add new dependency
uv add <package-name>

# Install in development mode
uv pip install -e .
```

### Running Code
```bash
# Run the cclib parser example
uv run python src/cclib/main.py

# Run the unified MCP server
uv run python src/parse_patrol/main.py
```

## Code Architecture

### Project Structure (2025)
- `src/parse_patrol/` - Unified MCP server entrypoint, collects all subservers
- `src/parsers/` - Collection of parsing tools
- `src/pipelines/` - Scripts for generating parsing pipelines
  - `agent_generated/` - Agent-produced pipeline scripts
  - `examples/` - Example pipeline scripts
  - `data/` - Test data files (moved from `tests/data`)
- `src/utils/` - Shared utilities/helpers
- `scripts/` - (Currently empty) CLI tools, setup scripts, etc.
- `pyproject.toml` - Project configuration and dependencies

### Key Components

**Unified MCP Server (`src/parse_patrol/main.py`)**
- Imports and exposes all tools from subservers (e.g., cclib, others).
- Acts as a short-hand entrypoint for all parsing tools.

**Subservers (e.g., `src/cclib/main.py`)**
- Define their own semantic tool definitions and logic.
- Can be extended independently.

**Parsing Tools (`src/parsers/`)**
- Contains individual parser modules (e.g., cclib, gaussian, etc.).

**Parsing Pipelines (`src/pipelines/`)**
- Agent-generated and example scripts for building parsing pipelines.
- Test data files for pipeline validation.

**Utilities (`src/utils/`)**
- Shared helper functions and utilities.

**Scripts (`scripts/`)**
- (Currently empty) CLI tools and setup scripts.

## Development Notes

The project is in early development with minimal implementation. The unified MCP server and subserver architecture allow for modular expansion and agent-driven parsing workflows.