
"""
Unified MCP server entrypoint for parse-patrol.
Collects and exposes all tools from subservers (e.g., cclib, others).
"""

from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]

# Import subserver modules (each with its own MCP tool definitions)
import src.cclib.main as cclib_main
# import src.parsers.other_parser.main as other_main

mcp = FastMCP("Unified MCP Server")

# Register all subservers' tools
for subserver in [cclib_main]:  # Add other subservers here
    for tool in getattr(subserver.mcp, "tools", []):
        mcp.tools.append(tool)
    for resource in getattr(subserver.mcp, "resources", []):
        mcp.resources.append(resource)
    for prompt in getattr(subserver.mcp, "prompts", []):
        mcp.prompts.append(prompt)

if __name__ == "__main__":
    mcp.run()