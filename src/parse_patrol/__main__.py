
"""
Unified MCP server entrypoint for parse-patrol.
Collects and exposes all tools from subservers.
"""

from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]

mcp = FastMCP("Parse Patrol - Unified Chemistry Parser")

# Subserver modules to register
SUBSERVERS = [
    "src.cclib.__main__",
    "src.nomad.__main__",
    "src.custom_gaussian.__main__",
    "src.iodata_parser.__main__",
]

# Tool and prompt function names to register from each module
REGISTRY = {
    "src.cclib.__main__": {
        "tools": ["cclib_parse_file_to_model"],
        "prompts": ["cclib_test_prompt"]
    },
    "src.nomad.__main__": {
        "tools": ["search_nomad_entries", "get_nomad_raw_files", "get_nomad_archive"],
        "prompts": ["nomad_materials_prompt"]
    },
    "src.custom_gaussian.__main__": {
        "tools": ["gauss_parse_file_to_model"],
        "prompts": ["custom_gaussian_test_prompt"]
    },
    "src.iodata_parser.__main__": {
        "tools": ["iodata_parser_parse_file_to_model"],
        "prompts": ["ciodata_test_prompt"]
    },
}

# Import and register all subserver functions
import importlib
for module_name in SUBSERVERS:
    module = importlib.import_module(module_name)
    
    # Register tools
    for tool_name in REGISTRY[module_name]["tools"]:
        tool_func = getattr(module, tool_name)
        mcp.tool()(tool_func)
    
    # Register prompts  
    for prompt_name in REGISTRY[module_name]["prompts"]:
        prompt_func = getattr(module, prompt_name)
        mcp.prompt()(prompt_func)

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
    return f"""
    Help me with this computational chemistry task: {task_description}

    Use {preferred_tools} from the parse-patrol toolkit to:

    1. **Data Discovery**: Search for relevant computational data using NOMAD if needed
    2. **File Parsing**: Use appropriate parsers (cclib, custom_gaussian) for the file types
    3. **Analysis**: Extract and interpret key chemical properties like:
       - Molecular geometries and structures
       - Electronic properties (energies, orbitals, charges)
       - Vibrational properties (frequencies, thermochemistry)
       - Optimization/transition state information
    4. **Integration**: Combine data from multiple sources if applicable

    Provide insights and recommendations based on the parsed data.
    """


if __name__ == "__main__":
    mcp.run()