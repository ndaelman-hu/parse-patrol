
"""
Unified MCP server entrypoint for parse-patrol.
Collects and exposes all tools from subservers (e.g., cclib, others).
"""

from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]

# Import subserver modules (each with its own MCP tool definitions)
import src.cclib.__main__ as cclib_main
import src.nomad.__main__ as nomad_main
import src.gaussian.__main__ as gaussian_main

mcp = FastMCP("Unified MCP Server")

# Register all subservers' tools
for subserver in [cclib_main, nomad_main, gaussian_main]:  # Add other subservers here
    print("Tools discovered:", mcp.__dict__.keys())
    for tool in getattr(subserver.mcp, "tools", []):
        mcp.tools.append(tool)
    for resource in getattr(subserver.mcp, "resources", []):
        mcp.resources.append(resource)
    for prompt in getattr(subserver.mcp, "prompts", []):
        mcp.prompts.append(prompt)

if __name__ == "__main__":
    mcp.run()