from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger
from .utils import iodata_parse, IODataModel

configure_logging("INFO")
logger = get_logger(__name__)


mcp = FastMCP("IOData: A python library for reading, writing, and converting computational chemistry file formats and generating input files")


@mcp.tool()
async def iodata_parse_file_to_model(filepath: str) -> IODataModel:
    """Parse chemistry file and return as IODataModel for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        IODataModel with parsed data converted for JSON serialization
    """
    logger.info("Parsing IOData file: %s ...", filepath)
    try:
        return iodata_parse(filepath)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Failed to parse file: %s", e)
        return IODataModel(extra={"error": str(e)})


@mcp.prompt()
async def iodata_test_prompt(
    file_description: str, output_format: str = "a IOData for JSON serialization"
) -> str:
    """Generate a prompt for parsing chemistry files using IOData.
    
    Args:
        file_description: Description of the file to be parsed
        output_format: Desired output format (default: IOData)
    
    Returns:
        Formatted prompt string for the MCP client
    """

    return (
        f"Use `iodata_parse_file_to_model` to parse the file (with extension .fck) with description {file_description} "
        f"and return the data as {output_format}."
    )


if __name__ == "__main__":
    mcp.run()