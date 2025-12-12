# parse-patrol

This README explains the objective, base usage and project structure.
For more detailed information on

- deploying the MCP services, see `./templates/README.md`.
- running the unit tests, see `./tests/README.md`.

> **"Try Before You Buy"** - Dual-Mode Chemistry Parsing Package

## Project Overview

*This project was originally conceived as a submission for LLM Hackathon in Materials Science and Chemistry 2025.*

Parse-patrol offers a framework for introducing mature community parsers / file converters.
These community parsers have been tested to work on some input, providing high-fidelity data extraction within a domain.
This allows any AI agent to focus on the conversion layer between the parser output and (user-defined) target file formats or schemas.
It can even combine multiple parsing tools in one to guarantee wider processing coverage.

Parse-patrol implements a **dual-mode architecture** to mitigate a common disconnect between AI experimentation and production integration.
More specifically, when asked to script a parser, agents often produce them from scratch.
Herein, they rely on (potentially outdated) knowledge or on-the-fly research about crucial aspects like the input format specifications.
Hence, this process leads to a prolonged test cycles where the final results may vary in quality.

With dual-mode, the same infrastructure is used in testing and scripting, enabling a *try before you buy* workflow for AI tools.
The community parsers can now act both as tools presented via the MCP protocol, or as plain code dependencies.
As a developer, you can casually brainstorm and test various parsers with your AI, before settling on a design for your high-volume script.
All MCP tools come with documentation that explains (to any client agent) how to both execute them and call them for usage within an autonomously written piece of code.

Watch our overviews [![demo](https://img.youtube.com/vi/fSAyi5ubkR0/0.jpg)](https://youtu.be/fSAyi5ubkR0) on YouTube.

### **MCP Discovery Mode**

Agents can discover and experiment with tools through MCP protocol:

- **Parser tools**: The actual computational chemistry parsers
- **Database tools**: Quick download of test files from popular computational chemistry databases. Is not meant as a complete MCP solution for database interaction, but only offers partial coverage.
- **Prompts**: Pre-built prompts for common chemistry analysis workflows

### **Direct Import Mode**

Developers and agents can install and use parser functions directly in production code:

```python
from parse_patrol import cclib_parse

result = cclib_parse("my_calculation.log")
print(f"Final energy: {result.final_energy}")
```

## **Adaptive Tool Availability**

Both modes automatically adapt to your local installation - **you only get tools for packages you've installed**:

```bash
# Lightweight: Only cclib tools available
uv sync --extra mcp --extra cclib
→ MCP exposes: cclib_parse_file_to_model only
→ Direct import: from parse_patrol import cclib_parse

# Full installation: All tools available  
uv sync --extra all
→ MCP exposes: all parsers + NOMAD database tools
→ Direct import: all parsers available

# Check what's available at runtime
from parse_patrol import available_parsers
print(available_parsers())  # ['cclib', 'gaussian', 'iodata']
```

This means the same codebase works across different deployment scenarios - from lightweight containers to full research environments.

### Available Tools

**Parser Tools** (both MCP + direct import):

- **cclib**: Multi-format quantum chemistry parser (Gaussian, ORCA, etc.)
- **iodata**: IOData-based parser for various chemistry formats

**Database Tools** (MCP only):

- **NOMAD**: Search and download from NOMAD materials database

Potential development routes -aside from extending tooling- include:

- adding documentation on the parsers and quantum chemistry software via RAG/MCP.
- proving the modularity of LLM: integrating with other AI agents via MCP protocol.
- coding our own, smaller and more modular parsing functions.
- using multiple agents for orchestrating complex tasks.

## Installation

### Prerequisites

This project uses `uv` for Python package management. If you don't have it installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**`uv` vs `uvx`:**

- **`uv`**: Package manager and virtual environment tool (like pip + venv combined)
- **`uvx`**: Tool for running packages temporarily without installation (like pipx)

### Development Setup

There is currently only a development version of this project.
Firstly, `git clone` this repository to your own local machine.

```bash
git clone <repository>
cd parse-patrol
uv sync  # Creates (+ manages) a virtual environment and installs dependencies
```

### For Direct Python Usage

**Install specific parsers only:**

```bash
# Install multiple parsers
uv sync --extra cclib --extra iodata

# Install all parsers at once
uv sync --extra parsers
```

### For MCP Server Usage

**Install with specific parser support:**

```bash
# MCP standalone
uv sync --extra mcp

# MCP + all parsers 
uv sync --extra all-parsers

# Everything (parsers + databases + MCP + dev tools)
uv sync --extra all
```

**Running the MCP server:**

There are 2 options to start the MCP server.
Either from within the host application (in this case typically an IDE).
See the IDE-specific instructions under `./templates/README.md` (**recommend**).

Alternatively, you can start the server from your terminal.
In this case, you have to manage connecting an agent yourself (**dis**).

```bash
uv run python -m parse_patrol
```

**Alternative installation methods:**

```bash
# Temporary execution (no installation)
uvx --from .[all] parse-patrol-mcp

# System-wide installation
uv tool install .[all-parsers]
parse-patrol-mcp
```

## Project Structure

```bash
parse-patrol/
├── src/
│   ├── parse_patrol/             # Unified MCP server entrypoint, collects all sub-servers
│   │   ├── databases/            # All database tools for downloading testing data
│   │   │   └── < db name >/      # Specific database tool
│   │   │       ├── __main__.py   # Tool MCP functionalities
│   │   │       └── utils.py      # Schema definitions and interface layer. Can be loaded in as a dependency.
│   │   └── parsers/              # All parsing tools
│   │       └── < parser name >/  # Specific parsing tool
│   │           ├── __main__.py   # Tool MCP functionalities
│   │           └── utils.py      # Schema definitions and interface layer. Can be loaded in as a dependency.
│   ├──utils/                     # Utilities/helpers across tools
│   ├── __init__.py               # File to log all available tools, resources (and prompts)
│   └── __main__.py               # Main interface to parse patrol. Defines most prompts
├── scripts/                      # CLI tools, setup scripts, etc. (Currently empty)
├── .pipelines/                   # Placeholder folder for the agent to write local tests to. Should only be used locally!
│   ├── data/                     # Temporary data files for testing the generated pipeline
│   ├── resources/                # Schema specifications defining the target file format / schema
│   └── scripts/                  # Agent-generated pipeline scripts and examples
├── pyproject.toml
├── README.md
└── LICENSE
```

## Development

Develop servers for each tool individually. Each tool has its own dedicated folder under `src/parsers/`. Define their MCP servers in `__main__.py`.

For testing of a new server, add it to IDE as outlined above.
Once the servers passes the checks, register the new MCP server:

- to unified interface in `src/parse_patrol/`. **Only the central interface is exposed in `main` branch!** This allows agents and users to access all parsing tools via a single, clear server endpoint.
- in this `README.md`, if this is a new tool.

For running or adding tests, as well as contributing to the official repository, see `./tests/README.md`.

### Warning Suppression for Dependencies

Some third-party dependencies (like cclib) may emit warnings during compilation or runtime. Here's how to suppress them:

#### For MCP Server Usage (Compile-time warnings)

Warnings like `SyntaxWarning` occur when Python compiles source files. To suppress them, set the `PYTHONWARNINGS` environment variable in your MCP configuration:

```json
{
  "servers": {
    "parse-patrol": {
      "command": "uv",
      "args": ["run", "python", "-m", "parse_patrol"],
      "env": {
        "PYTHONWARNINGS": "ignore::SyntaxWarning"
      }
    }
  }
}
```

This is already configured in all template files under `templates/`.

#### For Direct Python Usage (Runtime warnings)

For runtime warnings when using parsers as direct dependencies, parse-patrol includes specialized `__init__.py` files in parser modules (e.g., `src/parse_patrol/parsers/cclib/__init__.py`) that automatically suppress known dependency warnings before imports.

If you need additional suppression in your own scripts, use Python's warnings module:

```python
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

from parse_patrol import cclib_parse
```

Alternatively, set the environment variable before running your script:

```bash
export PYTHONWARNINGS="ignore::SyntaxWarning"
python your_script.py
```

#### For pytest (Test suite)

Warning filters are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
    "ignore::SyntaxWarning",
]
```

This ensures tests run cleanly without noise from dependency warnings.

## Online Resources

The following links explain the basics of MCP, including the distinction between *tools*, *resources*, and *prompts*. **Make sure to respect these distinctions!**

- Basics
  - Full repo and README of the MCP Python SDK: <https://github.com/modelcontextprotocol/python-sdk>
  - The FastMCP package docs: <https://gofastmcp.com>
- Advanced
  - JSON-RPC: foundational protocol that formalizes MCP server-client communication. It is transport-layer agnostic: <https://www.jsonrpc.org/specification>
- VS Code
  - detailed MCP server setup and management: <https://code.visualstudio.com/docs/copilot/customization/mcp-servers>
- cclib
  - Docs explaining the supported fields and codes: <https://cclib.github.io/data.html>
  - Repo for in-depth navigation of the code: <https://github.com/cclib>
