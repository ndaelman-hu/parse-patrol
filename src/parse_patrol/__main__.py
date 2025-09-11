
"""
Unified MCP server entrypoint for parse-patrol.
Collects and exposes all tools from subservers (e.g., cclib, others).
"""

from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]

# Import subserver modules (each with its own MCP tool definitions)
import src.cclib.__main__ as cclib_main
import src.nomad.__main__ as nomad_main
import src.custom_gaussian.__main__ as custom_gaussian_main

mcp = FastMCP("Unified MCP Server")

# Register all subservers' tools
for subserver in [cclib_main, nomad_main, custom_gaussian_main]:  # Add other subservers here
    print("Tools discovered:", mcp.__dict__.keys())
    for tool in getattr(subserver.mcp, "tools", []):
        mcp.tools.append(tool)
    for resource in getattr(subserver.mcp, "resources", []):
        mcp.resources.append(resource)
    for prompt in getattr(subserver.mcp, "prompts", []):
        mcp.prompts.append(prompt)

@mcp.prompt()
def parse_patrol_assistant_prompt(
    task_description: str,
    preferred_tools: str = "any available parsers"
) -> str:
    """Generate an open-ended prompt for comprehensive chemistry file analysis.
    
    Args:
        task_description: Description of the computational chemistry task
        preferred_tools: Preferred parsing tools (default: any available parsers)
    
    Returns:
        Formatted prompt string for comprehensive analysis
    """
    return f"""Help me with this computational chemistry task: {task_description}

Use {preferred_tools} from the parse-patrol toolkit to:

1. **Data Discovery**: Search for relevant computational data using NOMAD if needed
2. **File Parsing**: Use appropriate parsers (cclib, custom_gaussian) for the file types
3. **Analysis**: Extract and interpret key chemical properties like:
   - Molecular geometries and structures
   - Electronic properties (energies, orbitals, charges)
   - Vibrational properties (frequencies, thermochemistry)
   - Optimization/transition state information
4. **Integration**: Combine data from multiple sources if applicable

Provide insights and recommendations based on the parsed data."""


if __name__ == "__main__":
    mcp.run()