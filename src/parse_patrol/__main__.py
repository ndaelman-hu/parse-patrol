
"""
Unified MCP server entrypoint for parse-patrol.
Collects and exposes all tools from subservers (e.g., cclib, others).
"""

from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]

mcp = FastMCP("Parse Patrol - Unified Chemistry Parser")

# Import subserver modules to trigger their tool/prompt definitions
# but access them through their function references, not mcp instances
import src.cclib.__main__ as cclib_main
import src.nomad.__main__ as nomad_main  
import src.custom_gaussian.__main__ as custom_gaussian_main

# Register tools and prompts directly from the imported functions
# This avoids FastMCP instance conflicts

# Register cclib tools and prompts
mcp.tool()(cclib_main.cclib_parse_file_to_model)
mcp.prompt()(cclib_main.cclib_test_prompt)

# Register NOMAD tools and prompts
mcp.tool()(nomad_main.search_nomad_entries)
mcp.tool()(nomad_main.get_nomad_raw_files)
mcp.tool()(nomad_main.get_nomad_archive)
mcp.prompt()(nomad_main.nomad_materials_prompt)

# Register custom Gaussian tools and prompts
mcp.tool()(custom_gaussian_main.gauss_parse_file_to_model)
mcp.prompt()(custom_gaussian_main.custom_gaussian_test_prompt)

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