# MCP Configuration Templates

## Quick Setup

Ready-to-use configuration templates are available in the `templates/` folder:

- **VS Code**: Copy `templates/vscode-mcp.json` to `.vscode/mcp.json`
- **Claude Desktop**: Copy content from `templates/claude-desktop-mcp.json` to your Claude config
- **Neovim**: Use `templates/neovim-mcp.json` as a starting point

### Individual Servers (Testing)

For testing specific parsers, you can add individual server configurations, based on the example templates, provided.
Here is an example for VS Code:

```json
{
  "servers": {
    "parse-patrol": {
      "command": "uv",
      "args": ["run", "python", "-m", "parse_patrol"],
      "cwd": "/path/to/parse-patrol"
    },
    "parse-patrol-cclib": {
      "command": "uv", 
      "args": ["run", "python", "-m", "parse_patrol.parsers.cclib"],
      "cwd": "/path/to/parse-patrol"
    },
    "parse-patrol-nomad": {
      "command": "uv",
      "args": ["run", "python", "-m", "parse_patrol.databases.nomad"],
      "cwd": "/path/to/parse-patrol"
    }
  }
}
```

## VS Code (verified)

### Starting the Server

#### Locally

1. Copy `vscode-mcp.json` to `.vscode/mcp.json` in your project root.
2. Start the server either directly from the file (toggles appear above the server name) or the Extensions icon (right-click on the server for all options).
3. Use Agent mode in Copilot Chat to access parse-patrol tools

![mcp.json](assets/images/mcp_json.png)

#### Remotely

In VS Code, go to the command prompt, type `> mcp` and select "MCP: Open Remote User Configuration".
It will open up a `mcp.json` file, where you can paste in your MCP server configurations.

### Using the Agent

Once the server is started, it will be available under the `CHAT` tab when running `Agent` mode.
Note that the default mode for co-pilot is `Ask/Edit` mode.

To access *resources* type the pound symbol (`#`), for prompt commands type slash (`/`) in the chat window and wait for auto-complete.
All resources and prompts names should start with `mcp.parse-patrol`.
(Note that the MCP server name may change when published under a different or multiple servers.)

When executing a prompt command, the input parameters will pop up at the top.
Their names and descriptions are outlined above the active text bar.
Input parameters may be required or optional (marked as such) input.
In the case of the later, the field can be left blank.
Finally, the full prompt will be returned to the chat input field, ready to be submitted.
Reviewing or editing is still possible at this step.

PITFALL: do not use the file explorer for adding fields, but the resource dialog.
Else you copy-paste the file contents, NOT the file path.

### Claude Desktop (experimental)

**Option 1: Project-scoped (Recommended):**

```bash
# From your parse-patrol project directory
# First ensure dependencies are installed
uv sync --extra mcp

# Add the MCP server - use absolute path to ensure correct environment
claude mcp add parse-patrol --scope project -- sh -c "cd $(pwd) && PYTHONPATH=src uv --project $(pwd) run python -m parse_patrol"
```

**Environment Issues:**

- The `claude mcp add` command may run in a different `uv` environment than your project
- Using `--project $(pwd)` ensures `uv` uses the correct project environment
- Alternatively, use the venv Python directly: `.venv/bin/python`

**Option 2: Manual configuration:**

1. Copy `claude-desktop-mcp.json` content to your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux/Ubuntu**: `~/.config/Claude/claude_desktop_config.json`
2. **Important**: Update `/path/to/parse-patrol` with your actual project path
3. Restart Claude Desktop

**Troubleshooting Claude MCP:**

- **Environment mismatch**: If "No module named 'mcp'" error, the `uv` environment differs from your project
  - Use `uv --project $(pwd) run` or direct venv path: `.venv/bin/python`
  - Test manually: `cd /your/project && PYTHONPATH=src uv run python -m parse_patrol`
- **Connection closed**: Server starts but immediately closes
  - Check dependencies: `uv sync --extra mcp`
  - Verify imports work: `PYTHONPATH=src uv run python -c "import parse_patrol.__main__"`
- **Server doesn't sync**: Try restarting Claude Desktop after adding the server

### Neovim (experimental)

1. Copy `neovim-mcp.json` to your Neovim MCP configuration location
2. Configure according to your MCP plugin requirements

## Configuration Options

### Main Server (Recommended)

All templates use the unified server by default, which provides:

- All parser tools (`cclib`, `iodata`)
- Database tools (NOMAD search/download)
- Pre-built prompts for chemistry workflows

## Path Configuration

- Replace `"${workspaceFolder}"` with the absolute path to your parse-patrol directory if needed
- Ensure `uv` is available in your PATH
- For system-wide installations, you can also use `uvx parse-patrol-mcp` instead of the module command

## Prerequisites

Before using these templates, ensure MCP dependencies are installed:

```bash
cd /path/to/parse-patrol
uv sync --extra mcp
```

## Troubleshooting

1. **"No module named 'mcp'" error**: Install MCP dependencies with `uv sync --extra mcp`
2. **"No module named parse_patrol" error**: Ensure `PYTHONPATH` is set correctly in the configuration
3. **Server won't start**: Check that `uv` is installed and the path is correct
4. **Import errors**: Ensure you're using `uv run python -m parse_patrol` (module syntax) not direct file paths
