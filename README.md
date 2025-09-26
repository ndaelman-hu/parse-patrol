# parse-patrol

> **"Try Before You Buy"** - Dual-Mode Chemistry Parsing Package

## Project Overview

**Dual-mode architecture** is a software design pattern that enables the perfect "try before you buy" workflow for AI tools. Parse-patrol demonstrates this architecture by providing computational chemistry parsing tools that can be both discovered/experimented with via MCP protocol AND directly imported for production use.

*Submission for LLM Hackathon in Materials Science and Chemistry 2025.*

## The Dual-Mode Architecture

Parse-patrol implements **dual-mode** to solve a common problem: the disconnect between AI experimentation and production integration.

**The Problem:** LLMs discover tools, experiment, and generate code - but then developers must manually figure out how to integrate the same functionality into their applications.

**The Solution:** Dual-mode architecture where the same tools are accessible via:

### 🔍 **MCP Discovery Mode**
LLMs can discover and experiment with tools through MCP protocol:
- **Parser tools**: cclib, gaussian, iodata for parsing computational chemistry files
- **Database tools**: NOMAD materials database search and file download
- **Prompts**: Pre-built prompts for common chemistry analysis workflows

### ⚡ **Direct Import Mode** 
Developers can install and use parser functions directly in production code:
```python
from parse_patrol import cclib_parse, gaussian_parse, iodata_parse

# Parse chemistry files directly - sync functions
result = cclib_parse("calculation.log")
gauss_data = gaussian_parse("gaussian.out") 
iodata_result = iodata_parse("structure.xyz")
```

### Available Tools

**Parser Tools** (both MCP + direct import):
- **cclib**: Multi-format quantum chemistry parser (Gaussian, ORCA, etc.)
- **gaussian**: Custom Gaussian file parser (.log, .out, .gjf, .fchk)
- **iodata**: IOData-based parser for various chemistry formats

**Database Tools** (MCP only):
- **NOMAD**: Search and download from NOMAD materials database

Potential development routes -aside from extending tooling- include:

- adding documentation on the parsers and quantum chemistry software via RAG/MCP.
- proving the modularity of LLM: integrating with another agent, e.g. Claude.
- coding our own, smaller and more modular parsing functions.
- using multiple agents for orchestrating complex tasks.

## Installation

### Prerequisites
This project uses `uv` for Python package management. If you don't have it installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Understanding `uv` vs `uvx`:**
- **`uv`**: Package manager and virtual environment tool (like pip + venv combined)
- **`uvx`**: Tool for running packages temporarily without installation (like pipx)

### Development Setup
There is currently only a development version of this project.
Firstly, `git clone` this repository to your own local machine.

```bash
git clone <repository>
cd parse-patrol
uv sync  # Creates venv and installs dependencies
```

### For Direct Python Usage

**Install specific parsers only:**
```bash
# Install just cclib parser
uv sync --extra cclib

# Install multiple parsers
uv sync --extra cclib --extra gaussian --extra iodata

# Install all parsers at once
uv sync --extra parsers
```

**Use in your Python code:**
```python
from parse_patrol import cclib_parse, gaussian_parse, iodata_parse

result = cclib_parse("my_calculation.log")
print(f"Final energy: {result.final_energy}")
```

### For MCP Server Usage

**Install with specific parser support:**
```bash
# MCP + specific parsers
uv sync --extra mcp --extra cclib --extra gaussian

# MCP + all parsers 
uv sync --extra all-parsers

# Everything (parsers + databases + MCP + dev tools)
uv sync --extra all
```

**Run the MCP server:**
```bash
uv run python -m parse_patrol  # Run the unified MCP server
```

**Alternative installation methods:**
```bash
# Temporary execution (no installation)
uvx --from .[all] parse-patrol-mcp

# System-wide installation
uv tool install .[all-parsers]
parse-patrol-mcp
```

## Testing

### Manual Testing with MCP Inspector
MCP primitives developed for a single server can be tested using [MCP instructor](https://github.com/modelcontextprotocol/inspector). The problem with it can not handle multiple servers at once. So, it requires to test each server individually. (We did not find the way to inspect multiple servers at once using MCP inspector).

```bash
# Test the unified server (recommended)
uv run mcp dev -m parse_patrol

# Test individual parsers  
uv run mcp dev -m parse_patrol.parsers.cclib
uv run mcp dev -m parse_patrol.parsers.gaussian
uv run mcp dev -m parse_patrol.databases.nomad
```
Then click on the url link appeared on the terminal to open the MCP inspector in the browser or inspector will automatically open in browser.

### VS Code Integration
To run and test all the servers together in VS Code, as a client, list your servers in a `json` file e.g., `.vscode/mcp.json` and VSCode will be capable of detect the servers and can be run on the clicking button above the server (appeared in the VSCode UI).

![mcp.json](assets/images/mcp_json.png)

## MCP Configuration

### Quick Setup
Ready-to-use configuration templates are available in the `templates/` folder:

- **VS Code**: Copy `templates/vscode-mcp.json` to `.vscode/mcp.json`
- **Claude Desktop**: Copy content from `templates/claude-desktop-mcp.json` to your Claude config
- **Neovim**: Use `templates/neovim-mcp.json` as a starting point

See `templates/README.md` for detailed setup instructions for each editor.

### Main Configuration
All templates use the unified server that provides all tools:

```json
{
  "servers": {
    "parse-patrol": {
      "command": "uv",
      "args": ["run", "python", "-m", "parse_patrol"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    }
  }
}
```

### Individual Servers (Testing Only)
For testing specific parsers, see `templates/README.md` for examples of individual server configurations.

## Project Structure

```
parse-patrol/
├── src/
│   ├── parse_patrol/             # Unified MCP server entrypoint, collects all subservers
│   ├── parsers/                  # Parsing tools with their own MCP server in `__main__.py`
│   └── utils/                    # Shared utilities/helpers
├── scripts/                      # (Currently empty) CLI tools, setup scripts, etc.
├── .pipelines/                   # Scripts and data for parsing pipelines
│   ├── scripts/                  # Agent-generated pipeline scripts and examples
│   └── data/                     # Test data files for pipeline processing
├── .resources/                   # Schema and documentation resources
│   ├── semantic-schema.md        # Semantic schema definitions
│   └── structure-schema.md       # Structure schema definitions
└── .data/                        # Data files downloaded by nomad MCP, to parse by the agent
├── pyproject.toml
├── README.md
├── LICENSE
```

## Usage

- **VS Code**: A central access server with all functional tools is registered under `.vscode/mcp.json` (copy from `.vscode/mcp.template.json`). It can be run from this file in the IDE, or found under the extensions the (`Ctrl+Shift+X` on Ubuntu). Once the server is started, it will be available to the `Agent` mode in co-pilot `CHAT` (make sure to switch your co-pilot from `Ask/Edit` to `Agent` mode!!!).

There are now various prompts available. Type slash (`/`) in the chat window and wait for auto-complete.
All prompts should show under `/mcp.parse-patrol.<prompt path>`. Note that the MCP server name may change when published under a different or multiple servers. While you are executing the slash commands, you can find the description of the required and optional input above the bar where you are entering the info (it is not very obvious at first).

Some prompts are dynamic and will request fields to filled in. When a field is optional, it will be marked as such. Finally, the full prompt will be returned to the chat input field, ready to be submitted.
Editing is still possible at this step.

PITFALL: do not use the file explorer for adding fields. This will copy-paste the file contents, NOT the file path.

### Starting the MCP servers remotely

In VS Code, go t the command prompt, type `> mcp` and select "MCP: Open Remote User Configuration". It will open up a `mcp.json` file, where you can paste in your MCP server configurations.

## Development

Develop servers for each tool individually. Each tool has its own dedicated folder under `src/parsers/`. Define their MCP servers in `__main__.py`.

For testing of a new server, add it to IDE as outlined above.
Once the servers passes the checks, register the new MCP server:

- to unified interface in `src/parse_patrol/`. **Only the central interface is exposed in `main` branch!** This allows agents and users to access all parsing tools via a single, clear server endpoint.
- in this `README.md`, if this is a new tool.

Testing is done 2 ways:

- the agent attempts to generate pipeline scripts. Successful cases may be stored under in `.pipelines/scripts/`. The input to be processed is found in `.pipelines/data/`. Schema definitions and documentation resources are available in `.resources/`.
- test the parser and server code in `tests/`.

## Online Resources

The following links explain the basics of MCP, including the distinction between _tools_, _resources_, and _prompts_. **Make sure to respect these distinctions!**

- Basics
  - Full repo and README of the MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
  - The FastMCP package docs: https://gofastmcp.com
- Advanced
  - JSON-RPC: foundational protocol that formalizes MCP server-client communication. It is transport-layer agnostic: https://www.jsonrpc.org/specification
- VS Code
  - detailed MCP server setup and management: https://code.visualstudio.com/docs/copilot/customization/mcp-servers
- cclib
  - Docs explaining the supported fields and codes: https://cclib.github.io/data.html
  - Repo for in-depth navigation of the code: https://github.com/cclib

## Demo video clip

[![Watch the demo](https://img.youtube.com/vi/fSAyi5ubkR0/0.jpg)](https://youtu.be/fSAyi5ubkR0)

