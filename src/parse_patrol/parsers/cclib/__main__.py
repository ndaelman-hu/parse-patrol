from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger
from .utils import cclib_parse, CCDataModel

configure_logging("INFO")
logger = get_logger(__name__)


mcp = FastMCP("CCLib Chemistry Parser")


@mcp.tool()
async def cclib_parse_file_to_model(filepath: str) -> CCDataModel:
    """Parse chemistry file and return as CCDataModel for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        CCDataModel with parsed data converted for JSON serialization
    """
    logger.info("Parsing file: %s ...", filepath)
    try:
        return cclib_parse(filepath)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Failed to parse file: %s", e)
        return CCDataModel()


@mcp.prompt()
async def cclib_test_prompt(
    file_description: str, output_format: str = "a CCDataModel for JSON serialization"
) -> str:
    """Generate a prompt for parsing chemistry files using cclib.
    
    Args:
        file_description: Description of the file to be parsed
        output_format: Desired output format (default: CCDataModel)
    
    Returns:
        Formatted prompt string for the MCP client
    """

    return f"""
    Use `cclib_parse_file_to_model`
    to parse the file with description {file_description}
    and return the data as {output_format}.
    """

if __name__ == "__main__":
    mcp.run()
