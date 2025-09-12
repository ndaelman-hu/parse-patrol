
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
        "tools": ["iodata_parse_file_to_model"],
        "prompts": ["iodata_test_prompt"]
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


@mcp.prompt()
def parse_patrol_parser_pipeline_prompt(
    file_paths: str,
    task_description: str = "Extract and summarize key chemical properties and write the pipeline into a code in a file to the folder `pipelines` in the root of the repository",
    preferred_tools: str = "`get_nomad_raw_files`, `get_nomad_archive`, `search_nomad_entries`, `cclib_parse_file_to_model`, `iodata_parse_file_to_model`, `gauss_parse_file_to_model`"
) -> str:
    """Generate a prompt for a structured parsing pipeline.
    
    Args:
        file_paths: Comma-separated list of file paths to parse
        task_description: Description of the parsing task (default: extract and summarize key chemical properties and write the pipeline into a code in a file to the folder `pipelines` in the root of the repository)
        preferred_tools: Preferred parsing tools (default: any available parsers)

    Returns:
        Formatted prompt string for the MCP client (which is supposed to write a parsing pipeline into a file).
    """
    PIPELINE_PROMPT_TEMPLATE = """
    You are to execute a structured parsing pipeline for the following files: {file_paths}

    Task Description: {task_description}
    Preferred Tools: {preferred_tools}

    - Design and execute a parsing/conversion workflow using the available tools.
    - Log each step, including (pseudo-)code snippets for manual reproduction.
    - Collect all logs and the final results, and save them into files for later reference. Save it as .log, .yaml and .json files.
    - If you design a new workflow or pipeline, ensure the steps are clear and reproducible.
    - Avoid hallucinating code; instead, focus on executing real parsing/conversion steps ({preferred_tools}) and logging the process.
    - Make sure to at least use two tools in the pipeline.
    - If possible, produce code artifacts that could be used to set up an entire database from similar files in the future.
    - Include error handling for unsupported file types or parsing issues.
    - Use the correct parser for each file type (e.g., `.chk` files with Gaussian parser, `.log`/`.out` files with cclib).
    - Use dot notation for Pydantic model instances returned by parser functions, or convert to dict as needed.
    - Consider type hints and input validation where appropriate.
    - Summarize the final parsed data and any insights gained from the analysis.
    - Test and validate the pipeline using the tools from [{preferred_tools}] that you have chosen in agentic mode in the chat.
    - After successful validation, write the entire pipeline into a code in a file to the folder `pipelines` in the root of the repository.
    """

    return PIPELINE_PROMPT_TEMPLATE.format(
        file_paths=file_paths,
        task_description=task_description,
        preferred_tools=preferred_tools
    )


if __name__ == "__main__":
    mcp.run()