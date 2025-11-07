from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger
from .utils import gaussian_parse, CustomGaussianDataModel

configure_logging("INFO")
logger = get_logger(__name__)


mcp = FastMCP("Custom Gaussian Parser")


@mcp.tool()
async def gauss_parse_file_to_model(filepath: str) -> CustomGaussianDataModel:
    """
    Parse a Gaussian file (.log/.out, .gjf/.com, .fchk) and return a CustomGaussianDataModel.

    - .log/.out: Extracts charge/multiplicity, last geometry, SCF energies, basic thermochemistry, vibrational frequencies/IR.
    - .gjf/.com: Extracts route, title, charge/multiplicity, and geometry.
    - .fchk: Extracts atomic numbers and coordinates.
    - .chk (binary): Not supported; convert with 'formchk' first.

    Args:
        filepath: Path to Gaussian file.

    Returns:
        CustomGaussianDataModel with parsed contents.
    """
    logger.info("Parsing Gaussian file: %s ...", filepath)
    try:
        return gaussian_parse(filepath)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Failed to parse file: %s", e)
        return CustomGaussianDataModel(metadata={"error": str(e)})


@mcp.prompt()
async def custom_gaussian_test_prompt(
    file_description: str, analysis_type: str = "comprehensive analysis"
) -> str:
    """Generate a prompt for parsing Gaussian files with custom analysis.
    
    Args:
        file_description: Description of the Gaussian file to be parsed
        analysis_type: Type of analysis desired (default: comprehensive analysis)
    
    Returns:
        Formatted prompt string for the MCP client
    """
    return f"""
    Use `gauss_parse_file_to_model` to parse the Gaussian file: {file_description}

    Perform {analysis_type} on the parsed data, focusing on:
    - Molecular geometry and atomic coordinates
    - SCF energies and convergence
    - Vibrational frequencies and thermochemistry
    - Any optimization or transition state information

    Return the data as a CustomGaussianDataModel with detailed analysis.
    """


if __name__ == "__main__":
    mcp.run()